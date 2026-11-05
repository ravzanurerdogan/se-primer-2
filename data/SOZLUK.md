# Veri sözlüğü: `data/oturumlar.csv`

Her satır **bir karar ekranıdır** (bir oturumda 3 satır: K1, K2, K3). Özellikler karar ekranı **açıldığı an** bilinen değerlerdir. Etiket, o karardan sonra belli olur.

**Gizlilik (KVKK):** Ad, e-posta, cihaz kimliği, konum gibi hiçbir kişisel veri toplanmaz. `oturum_id` rastgele üretilir (`crypto.randomUUID` ilk 8 karakter) ve kişiye geri götürülemez. Gerçek ve kurgusal olmayan hiçbir hasta/token verisi yoktur.

| Sütun | Tür | Birim / değerler | Anlamı |
|---|---|---|---|
| `oturum_id` | metin | 8 karakter | Bir oyun oturumu. Aynı oturumun 3 satırı aynı kimliği taşır |
| `kaynak` | metin | `gercek` \| `sentetik` | Verinin kaynağı. Bu sürümde tüm satırlar `gercek` |
| `karar_no` | tam sayı | 1, 2, 3 | K1 müdahale, K2 temizlik, K3 KVKK |
| `seviye` | 0/1 | 0 = Yeni başladım, 1 = Deneyimliyim | Girişte seçilen seviye |
| `rol_backend` | 0/1 | | Rol Backend ise 1 |
| `rol_mobil` | 0/1 | | Rol Mobil ise 1 |
| `rol_qa` | 0/1 | | Rol QA ise 1 (üç rol sütunundan biri 1'dir) |
| `onceki_yanlis_sayisi` | tam sayı | adet, 0..2 | Bu karardan önce kaç kez B seçildi |
| `onceki_karar_suresi_sn` | sayı | saniye | Bir önceki kararın ekranda geçen süresi. K1'de 0 |
| `onceki_inceleme_sayisi` | tam sayı | adet, 0..3 (kümülatif) | Önceki ekranlarda dokunulan log satırı sayısı. K1'de 0 |
| `alert_incelendi` | 0/1 | | ALERT logu bu ana kadar açıldı mı |
| `gecen_dk` | tam sayı | oyun içi dakika | Oyun içi geçen süre (`elapsedMinutes`), limit 45 |
| `ipucu_sayisi` | tam sayı | adet | Bu ana kadar "İpucu al" kaç kez kullanıldı |
| `yanlis_secim` | 0/1 | **etiket** | Bu kararda B seçildi veya süre doldu ise 1 |

## Bilinen veri sorunları ve sınırlar

- **Az veri:** 19 oturum, 57 satır, 11 pozitif etiket.
- **Aykırı değer:** Bir oturumda `onceki_karar_suresi_sn = 196` (oyuncu ekranı açık bırakmış olabilir). Satır silinmedi, eğitimde ve uygulamada 60 sn'ye kırpılır.
- **Fazlalık:** `onceki_inceleme_sayisi` ile `alert_incelendi` büyük ölçüde aynı bilgiyi taşır (3 ise 1, 0 ise 0).
- **Seviye farkı:** "Deneyimliyim" modunda etiketin bir kısmı 60 sn sayacından gelir (süre dolarsa B). Bu, bilgi eksikliğinden değil süre baskısından doğar.
- **Öğrenme etkisi:** Aynı kişinin sonraki oturumlarında doğru yolu bilmesi davranışı değiştirir. Tekrarlar bağımsız sayılmaz, bu yüzden değerlendirme `oturum_id`'ye göre gruplanır.
