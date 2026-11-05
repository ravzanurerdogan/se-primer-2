"""Test Kahini (Oracle): model.onnx'i Python'dan çalıştırır.

  python tests/parite.py --yaz     -> tests/parite.json'ı üretir (5 referans girdi + Python'un olasılığı)
  python tests/parite.py           -> parite.json'daki değerleri yeniden hesaplayıp tutarlılığı doğrular

Uygulama (onnxruntime-web) aynı girdilerle `data-cy="p"` içine olasılığı yazar;
Cypress farkın < 1e-4 olduğunu kontrol eder.
Girdiler HAM değerlerdir. Kırpma (onceki_karar_suresi_sn <= 60) uygulama ve oracle'da aynıdır,
ölçekleme ONNX'in içindedir.
"""
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort

KOK = Path(__file__).resolve().parent.parent
CFG = json.loads((KOK / "model" / "config.json").read_text(encoding="utf-8"))
OZ = CFG["ozellikler"]
TOL = 1e-4

# 5 referans girdi: farklı profiller, K1/K2/K3, aykırı süre dahil
GIRDILER = [
    {"ad": "K1 yeni başladım, backend",           "seviye": 0, "rol_backend": 1, "rol_mobil": 0, "rol_qa": 0, "karar_no": 1, "onceki_yanlis_sayisi": 0, "onceki_karar_suresi_sn": 0,   "onceki_inceleme_sayisi": 0, "alert_incelendi": 0, "gecen_dk": 0,  "ipucu_sayisi": 0},
    {"ad": "K2 deneyimli, K1'de B seçti",         "seviye": 1, "rol_backend": 0, "rol_mobil": 1, "rol_qa": 0, "karar_no": 2, "onceki_yanlis_sayisi": 1, "onceki_karar_suresi_sn": 8,   "onceki_inceleme_sayisi": 3, "alert_incelendi": 1, "gecen_dk": 18, "ipucu_sayisi": 0},
    {"ad": "K2 deneyimli, K1'de A seçti",         "seviye": 1, "rol_backend": 1, "rol_mobil": 0, "rol_qa": 0, "karar_no": 2, "onceki_yanlis_sayisi": 0, "onceki_karar_suresi_sn": 3,   "onceki_inceleme_sayisi": 0, "alert_incelendi": 0, "gecen_dk": 5,  "ipucu_sayisi": 0},
    {"ad": "K3 aykırı süre (196 sn -> 60'a kırp)", "seviye": 0, "rol_backend": 0, "rol_mobil": 1, "rol_qa": 0, "karar_no": 3, "onceki_yanlis_sayisi": 1, "onceki_karar_suresi_sn": 196, "onceki_inceleme_sayisi": 0, "alert_incelendi": 0, "gecen_dk": 9,  "ipucu_sayisi": 3},
    {"ad": "K3 QA, alert incelenmiş",             "seviye": 0, "rol_backend": 0, "rol_mobil": 0, "rol_qa": 1, "karar_no": 3, "onceki_yanlis_sayisi": 1, "onceki_karar_suresi_sn": 2,   "onceki_inceleme_sayisi": 3, "alert_incelendi": 1, "gecen_dk": 15, "ipucu_sayisi": 0},
]


def olasilik(sess, satir: dict) -> float:
    v = dict(satir)
    for k, (alt, ust) in CFG["on_isleme"]["kirp"].items():
        v[k] = min(max(v[k], alt), ust)
    x = np.array([[v[o] for o in OZ]], dtype=np.float32)
    ad = CFG["onnx"]["giris_adi"]
    return float(sess.run(None, {ad: x})[1][0][CFG["onnx"]["pozitif_sinif_indeksi"]])


def main() -> None:
    sess = ort.InferenceSession(str(KOK / "model" / "model.onnx"), providers=["CPUExecutionProvider"])
    if "--yaz" in sys.argv:
        cikti = [{"ad": g["ad"], "girdi": {o: g[o] for o in OZ}, "p": olasilik(sess, g)} for g in GIRDILER]
        (KOK / "tests" / "parite.json").write_text(
            json.dumps({"tolerans": TOL, "ozellik_sirasi": OZ, "vakalar": cikti}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        for c in cikti:
            print(f"p={c['p']:.6f}  {c['ad']}")
        print("tests/parite.json yazıldı")
        return
    kayit = json.loads((KOK / "tests" / "parite.json").read_text(encoding="utf-8"))
    en_kotu = max(abs(olasilik(sess, {**v["girdi"]}) - v["p"]) for v in kayit["vakalar"])
    print(f"maks fark = {en_kotu:.2e} (tolerans {TOL:.0e})")
    sys.exit(0 if en_kotu < TOL else 1)


if __name__ == "__main__":
    main()
