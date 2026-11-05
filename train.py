"""The Primer v2: tek komutla eğitim + eval kapısı + ONNX paketi.

Çalıştır:  python train.py
Eşik (spec.md bölüm 13, eğitimden önce yazıldı): AUC >= 0.65, GroupKFold(5), yalnızca gerçek veri.
Eşik altında betik hata koduyla (1) durur ve model/ altına hiçbir artefakt YAZILMAZ.
"""
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
import pandas as pd
import sklearn
import skl2onnx
from skl2onnx import to_onnx
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# --- spec.md ile birebir aynı sabitler ---
SEED = 42
ESIK_AUC = 0.65
ONNX_TOLERANS = 1e-4
KARAR_ESIGI = 0.35
OZELLIKLER = [
    "seviye", "rol_backend", "rol_mobil", "rol_qa", "karar_no",
    "onceki_yanlis_sayisi", "onceki_karar_suresi_sn", "onceki_inceleme_sayisi",
    "alert_incelendi", "gecen_dk", "ipucu_sayisi",
]
ETIKET = "yanlis_secim"
KIRP = {"onceki_karar_suresi_sn": [0.0, 60.0]}

KOK = Path(__file__).parent
VERI = KOK / "data" / "oturumlar.csv"
CIKTI = KOK / "model"


def onisle(df: pd.DataFrame) -> np.ndarray:
    df = df.copy()
    for kolon, (alt, ust) in KIRP.items():
        df[kolon] = df[kolon].clip(alt, ust)
    return df[OZELLIKLER].to_numpy(dtype=np.float32)


def yeni_pipeline() -> Pipeline:
    return Pipeline([
        ("olcek", StandardScaler()),
        ("lr", LogisticRegression(C=0.3, max_iter=1000, random_state=SEED)),
    ])


def main() -> None:
    df = pd.read_csv(VERI)
    df = df[df["kaynak"] == "gercek"].reset_index(drop=True)
    X, y, gruplar = onisle(df), df[ETIKET].to_numpy(), df["oturum_id"].to_numpy()
    n_oturum = len(np.unique(gruplar))
    print(f"Veri: {len(df)} satır, {n_oturum} oturum, {int(y.sum())} pozitif")

    # --- Eval kapısı: oturum bazlı çapraz doğrulama ---
    oof = np.zeros(len(df))
    for egitim, test in GroupKFold(n_splits=5).split(X, y, gruplar):
        m = clone(yeni_pipeline()).fit(X[egitim], y[egitim])
        oof[test] = m.predict_proba(X[test])[:, 1]
    auc = float(roc_auc_score(y, oof))

    # Oturum bazlı bootstrap %95 aralığı (dürüstlük için, karar bunu kullanmaz)
    rng = np.random.default_rng(SEED)
    benzersiz = np.unique(gruplar)
    aucler = []
    for _ in range(1000):
        secilen = rng.choice(benzersiz, size=len(benzersiz), replace=True)
        idx = np.concatenate([np.where(gruplar == g)[0] for g in secilen])
        if len(np.unique(y[idx])) == 2:
            aucler.append(roc_auc_score(y[idx], oof[idx]))
    ci = [float(np.percentile(aucler, 2.5)), float(np.percentile(aucler, 97.5))]

    print(f"AUC (GroupKFold-5, birleşik) = {auc:.3f}   eşik = {ESIK_AUC}")
    print(f"Bootstrap %95 aralığı        = [{ci[0]:.3f}, {ci[1]:.3f}]")
    if auc < ESIK_AUC:
        print(f"EVAL KAPISI: AUC {auc:.3f} < {ESIK_AUC}. Artefakt yayınlanmadı.")
        sys.exit(1)

    # --- Son model: tüm gerçek veriyle ---
    model = yeni_pipeline().fit(X, y)
    onx = to_onnx(
        model, X[:1], target_opset={"": 15, "ai.onnx.ml": 3},
        options={id(model.steps[-1][1]): {"zipmap": False}},
    )
    CIKTI.mkdir(exist_ok=True)
    onnx_yolu = CIKTI / "model.onnx"
    onnx_yolu.write_bytes(onx.SerializeToString())

    # --- ONNX ile sklearn farkı ---
    oturum = ort.InferenceSession(str(onnx_yolu), providers=["CPUExecutionProvider"])
    giris = oturum.get_inputs()[0].name
    cikis = [o.name for o in oturum.get_outputs()]
    p_onnx = oturum.run(None, {giris: X})[1][:, 1]
    p_skl = model.predict_proba(X)[:, 1]
    fark = float(np.max(np.abs(p_onnx - p_skl)))
    print(f"ONNX - sklearn maks fark = {fark:.2e}   tolerans = {ONNX_TOLERANS:.0e}")
    if fark >= ONNX_TOLERANS:
        onnx_yolu.unlink()
        print("ONNX KAPISI: fark toleransı aşıyor. Artefakt yayınlanmadı.")
        sys.exit(1)

    config = {
        "model_adi": "primer-yanlis-secim-riski",
        "surum": "v2.0",
        "gorev": "Karar ekranı açılırken yanlış seçenek (B) seçme olasılığı",
        "ozellikler": OZELLIKLER,
        "ozellik_sayisi": len(OZELLIKLER),
        "on_isleme": {"kirp": KIRP, "not": "Ölçekleme (StandardScaler) ONNX'in içindedir, istemcide ayrıca ölçekleme YAPILMAZ."},
        "onnx": {"giris_adi": giris, "giris_tipi": "float32", "giris_sekli": [None, len(OZELLIKLER)],
                 "cikis_adlari": cikis, "olasilik_cikisi": cikis[1], "pozitif_sinif_indeksi": 1},
        "siniflar": {"0": "doğru seçim (A)", "1": "yanlış seçim (B) veya süre doldu"},
        "karar_esigi": KARAR_ESIGI,
        "kabul_esigi": {"metrik": "roc_auc", "deger": ESIK_AUC},
        "metrikler": {
            "roc_auc_groupkfold5": round(auc, 4),
            "auc_bootstrap_95": [round(ci[0], 4), round(ci[1], 4)],
            "onnx_sklearn_maks_fark": fark,
            "n_satir": int(len(df)), "n_oturum": int(n_oturum), "n_pozitif": int(y.sum()),
        },
        "egitim": {"random_state": SEED, "algoritma": "StandardScaler + LogisticRegression(C=0.3)",
                   "sklearn": sklearn.__version__, "skl2onnx": skl2onnx.__version__,
                   "onnxruntime": ort.__version__},
    }
    (CIKTI / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Artefakt yazıldı: model/model.onnx, model/config.json")


if __name__ == "__main__":
    main()
