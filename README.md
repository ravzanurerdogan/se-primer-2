# SE Primer: Sızan Token

Kişiye uyum sağlayan, karar tabanlı bir yazılım mühendisliği simülasyonu. Senaryo: hastane laboratuvar sonuç API'sinin token'ı repoya sızdı, tanımadığın bir IP sonuç çekiyor, nöbetçi sensin. Oyuncu 3 karar verir, uygulama her kararın teknik sonucunu ve nedenini gösterir. Girişte seçilen seviye, rol ve hedef anlatıyı, süre baskısını ve ipucu sistemini değiştirir.

## Teslim linkleri

| | Link |
|---|---|
| Çalışan uygulama (telefonda açılır, giriş gerektirmez) | https://se-primer-2.ai.studio |
| Demo video (Cypress E2E koşusu) | https://youtu.be/2DtxfUhy__o |
| Canlı Uygulama Linki | (https://youtu.be/gHA01zqwt7I) |

## Repo içeriği ve ödev karşılığı

| Dosya | İçerik |
|---|---|
| `spec.md` | Problem, kapsam dışı, gizli durum ve karar kuralları, akış şeması, 7 kabul örneği, arkadaş testi bulguları |
| `DESIGN.md` + `screens/` | Stitch tasarım sistemi, projeye özgü ekler, 3 ekran görüntüsü |
| `eval.md` | AI tutor değerlendirmesi: 20 öğrenci mesajı, etiketler, hata türleri, oranlar |
| `cypress/e2e/se-primer.cy.js` | E2E testler (11 test, tüm yollar) |
| `cypress.config.js` | Test ayarları (mobil görünüm, video) |

## Nasıl oynanır

1. Linki telefonda aç.
2. Seviye, rol ve hedefi seç, "Başla"ya bas.
3. Her karar ekranında log satırlarına dokunarak araştırma yapabilir (her biri süre harcar), ekip sohbetini okuyabilir, ardından A veya B'yi seçip "Kararı uygula"ya basarsın.
4. Her seçimden sonra "ne oldu / neden oldu" kartı çıkar. Üç karardan sonra iyi ya da kötü son gösterilir.

İyi son için: K1, K2, K3'ün hepsi A, ALERT logu incelenmiş (kapsamlı bildirim) ve toplam süre 45 dakikayı aşmamış olmalı.

## Testleri çalıştırma

```
npm install cypress --save-dev
npx cypress run      # arka planda koşar, cypress/videos altına video üretir
npx cypress open     # tarayıcıda canlı izlemek için
```

Testler `cypress.config.js` içindeki `baseUrl` adresine (yukarıdaki uygulama linki) bağlanır.

## Tutor değerlendirmesi (özet)

20 öğrenci mesajıyla ölçüldü (ayrıntı: `eval.md`):

- Doğrudan cevap veren: 0 / 20
- Soru biçiminde doğru tarafı ima eden: 8 / 20 (%40)
- Ele vermeyen: 12 / 20 (%60)
- Sistem talimatını aşma ve rol yapma denemeleri tutmadı.
- Zayıf yan: cevapların çoğu somut olaydan kopuk genel mühendislik diline kaydı.

Bilinen sınırlama: Tutor Gemini API kotası dolduğunda yedek bir soruya düşer. İlk ölçüm turu bu yüzden geçersiz sayıldı; hata kaydı, yeniden deneme ve `data-source` işareti eklenerek düzeltildi.

## Ürün kararı: yapmadığım 3 özellik

1. **Kullanıcı hesabı ve ilerleme kaydı:** Oyun tek oturumluk bir deneyim; hesap öğrenme değerine katkı yapmadan kapsamı büyütürdü.
2. **İkinci senaryo:** Tek senaryoyu derinleştirmek (gizli durum, araştırma, ekip sohbeti) ikinci bir yüzeysel senaryodan daha çok öğretir.
3. **Gerçek GitHub/AWS bağlantısı:** Gerçek token'larla çalışmak güvenlik riski yaratırdı; kurgusal veri aynı dersi tehlikesiz verir.

## Kaynaklar

Kaynakça `spec.md` sonundadır.
