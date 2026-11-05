# RELEASE.md: The Primer v2.0

## 1. Bu sürümde ne değişti?
- v1: Giriş profiline göre **sabit kurallar** (Yeni başladım → ipucu, Deneyimliyim → 60 sn sayaç).
- v2.0: Üstüne **öğrenilmiş bir model katmanı**: karar ekranı açılırken yanlış seçim (B) riskini tahmin eder; `p >= 0.35` ise sayaç kalkar, ipucu açılır, sonuç kartı ayrıntılanır. Karar mantığı ve sonlar (v1 bölüm 4-5) değişmedi.

**Sürüm sabitleme:** Uygulama modeli `main` dalından değil, commit'e sabit adresten indirir:

```
https://huggingface.co/Ravza13/primer/resolve/a889310fd9fdb59ef8bcda7e0d42b93040cf7e01/model.onnx
https://huggingface.co/Ravza13/primer/resolve/a889310fd9fdb59ef8bcda7e0d42b93040cf7e01/config.json
```
`main` değişse bile bu adres aynı baytları verir. Bu yüzden kimse farkında olmadan yeni modele geçmez (Sommerville Bl. 25 Konfigürasyon Yönetimi). Not: Model kartını (README) sonradan yüklemek yeni bir commit oluşturur, ancak `model.onnx` ve `config.json` içeriği aynı kaldığından yukarıdaki sabit adresler geçerlidir.

## 2. Geri alma (Rollback)
1. **Hızlı (saniyeler):** Uygulamada `?model=0` veya sabit bayrak `MODEL_ACIK=false` → oyun v1 kurallarıyla çalışır (KÖ-10 aynı yolu kullanır).
2. **Önceki sürüm:** İlk model olduğu için "önceki sürüm" v1'in kural tabanlı hâlidir. Sonraki bir `v2.1` çıkarsa geri dönüş, uygulamadaki tek sabit olan commit hash'ini eski değere çevirmektir; model kodu değişmez.
3. **Tetikleyici:** Parite testi (`1e-4`) kırılırsa veya model yüklenemezse otomatik olarak v1'e düşülür.

## 3. Yeni sürümü güvenle devreye alma
Modelin herkese birden açılması yerine, bu senaryoda şöyle işler:

| Aşama | Bu projede ne yapılır | Geçiş koşulu |
|---|---|---|
| **Shadow (gölge)** | Model gerçek oturumlarda **çalışır ama oyunu değiştirmez**; `p` kaydedilir ve gerçek seçimle (B mi A mı) karşılaştırılır | Gölge AUC ≥ 0.65 ve model hata vermiyor |
| **Canary %5** | `oturum_id`'nin karma değeri %100'de 5'in altındaysa model oyunu değiştirir, diğerleri v1 | v1 E2E testleri geçiyor, hata/çökme yok |
| **Progressive 25% → 50% → 100%** | Aynı karmanın eşiği büyütülür | Her aşamada kötü son oranı v1'e göre anlamlı kötüleşmiyor |

Bu ödevde gerçek trafik olmadığı için aşamalar küçük arkadaş grubuyla ve demo koşularıyla temsil edilir; mantık aynıdır.

## 4. Mimari dağıtım kararı ve ödünleşim matrisi
**Karar:** Modeli **tarayıcıda (`onnxruntime-web`)**, GitHub Pages / AI Studio'da çalıştırıyoruz.

| Soru | Tarayıcı (`onnxruntime-web`) ✅ seçilen | Cihaz içi mobil (Expo + `onnxruntime-react-native`) | Kendi sunucum (Render / Rails veya FastAPI) |
|---|---|---|---|
| **1. İnternet zorunlu mu, gecikme?** | İlk açılışta ~650 bayt model + ONNX Runtime wasm indirilir (ilk yükte gecikme); sonra tahmin yerelde, ağ gecikmesi yok. Model yüklenemezse v1'e düşülür | Model uygulamayla gömülü, internetsiz çalışır, gecikme en düşük | Her tahminde ağ gecikmesi; ücretsiz Render katmanı uykudan uyanırken saniyeler sürebilir |
| **2. Veri cihazdan çıkar mı?** | **Çıkmaz.** Davranış özellikleri tarayıcıda kalır; KVKK açısından en kolay | Çıkmaz | **Çıkar**; her istekte özellikler sunucuya gider, KVKK ve aydınlatma yükümlülüğü doğar |
| **3. Model gizli kalır mı?** | **Kalmaz.** `model.onnx` indirilebilir. Bu modelde sorun değil (645 bayt, kamuya açık, hassas bilgi yok) | Paket içinden çıkarılabilir | Gizli kalır, ama çok sayıda sorguyla tersine mühendislikle taklit edilebilir (REA riski) |

**Gerekçe:** Model çok küçük ve gizli değil, veri hassas olabilir ve internet kesintisinde oyun bozulmamalı. Bu üç ölçüt tarayıcıyı öne çıkarıyor. Bedel: sunucu gibi merkezi izleme (monitoring) yok; bu yüzden gölge aşamasında kayıt ayrıca eklenmelidir.

## 5. Bilinen riskler
- AUC güven aralığı geniş [0.50, 0.87] (bkz. `model/README.md`). Bu yüzden devreye alma kademeli yapılır.
- İlk açılışta `onnxruntime-web` wasm dosyası CDN'den gelir; CDN erişilemezse v1'e düşülür.
