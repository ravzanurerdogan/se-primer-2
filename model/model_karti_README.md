---
library_name: onnx
tags: [onnx, tabular, scikit-learn, logistic-regression, education]
---
# primer-yanlis-secim-riski (v2.0) — Model Kartı

## Amaç
The Primer: "Sızan Token" oyununda, **bir karar ekranı açılırken oyuncunun yanlış seçeneği (B) seçme olasılığını** tahmin eder. Oyun bu olasılığa göre yardım düzeyini ayarlar (sayaç kalkar, ipucu açılır, ayrıntılı sonuç kartı). Eğitim amaçlı bir ödev modelidir.

## Girdi / çıktı (sözleşme: `config.json`)
11 özellik, **bu sırayla**, `float32`, şekil `[1, 11]`:
`seviye, rol_backend, rol_mobil, rol_qa, karar_no, onceki_yanlis_sayisi, onceki_karar_suresi_sn, onceki_inceleme_sayisi, alert_incelendi, gecen_dk, ipucu_sayisi`

- İstemci tek ön işlem yapar: `onceki_karar_suresi_sn` değerini `[0, 60]` aralığına kırpar. **Ölçekleme ONNX'in içindedir**, istemcide yapılmaz.
- Çıktı: `probabilities` `[1, 2]`; indeks 1 = "yanlış seçim (B) veya süre doldu" olasılığı.
- Oyun kararı: `p >= 0.35` ise yüksek risk.

## Veri
Oyunun veri toplama modunda gerçek insanların oynadığı **19 oturum, 57 karar satırı, 11 pozitif etiket** (`data/oturumlar.csv`, sözlük: `data/SOZLUK.md`). Tüm satırlar gerçek, sentetik veri kullanılmadı. Kişisel veri yok (rastgele 8 karakterlik oturum kimliği).

## Eğitim
`StandardScaler + LogisticRegression(C=0.3)`, `random_state=42`. Tek komut: `python train.py`. Eşik altında betik durur.

## Metrikler (dürüst ölçüm)
| Metrik | Değer |
|---|---|
| ROC-AUC, oturum bazlı 5 katlı çapraz doğrulama | **0.692** |
| Kabul eşiği (eğitimden önce yazıldı) | 0.65 |
| Oturum bazlı bootstrap %95 aralığı | **[0.50, 0.87]** |
| ONNX − sklearn maks. olasılık farkı | 6e-08 (tolerans 1e-4) |

**Yorum:** Eşik geçildi, ancak aralığın alt ucu rastgele tahmin düzeyindedir (0.50). 19 oturumla "model güvenilir biçimde öğreniyor" diyemeyiz; sonuç bir kanıt değil, bir ilk işarettir.

## Sınırlar
- Çok küçük veri (19 oturum). Bilinmeyen kullanıcılar için genelleme **kanıtlanmamıştır**.
- Yalnızca bu oyunun 3 kararı ve 3 rolü için anlamlıdır.
- "Deneyimliyim" modunda etiketin bir kısmı 60 sn sayacından gelir (süre dolarsa B); bu bilgi eksikliği değil süre baskısıdır.
- Aynı kişinin tekrar oynaması (öğrenme etkisi) davranışı değiştirir.
- `onceki_inceleme_sayisi` ve `alert_incelendi` büyük ölçüde aynı bilgiyi taşır.
- Aykırı değer (196 sn) silinmedi, 60 sn'ye kırpıldı.
- Olasılıklar kalibre edilmemiştir; 0.35 eşiği ayarlanmamış başlangıç değeridir.

## Kullanılmaması gereken durumlar
- Gerçek kişilerin yeteneği, başarısı veya işe uygunluğu hakkında karar vermek (not, işe alım, değerlendirme).
- Başka bir oyun, senaryo veya kullanıcı kitlesi için doğrulama yapmadan kullanmak.
- Tek başına bir güvenlik/kritik karar için.

## Sürüm
`v2.0`, Hugging Face commit `a889310fd9fdb59ef8bcda7e0d42b93040cf7e01`.
