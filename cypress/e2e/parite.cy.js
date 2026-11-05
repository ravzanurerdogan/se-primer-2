// Diferansiyel test (parite): Python Oracle (tests/parite.py) ile uygulamadaki onnxruntime-web
// aynı 5 referans girdiye hata toleransı (1e-4) dahilinde aynı olasılığı vermeli.
// Referans: tests/parite.json (python tests/parite.py --yaz ile üretilir).
// Çalıştır: npx cypress run --spec cypress/e2e/parite.cy.js

// "p = 0.0359..." gibi yazılar olsa bile ilk ondalıklı sayıyı al
const sayiOku = (metin) => {
  const m = String(metin).match(/-?\d+(?:\.\d+)?(?:e-?\d+)?/i);
  return m ? parseFloat(m[0]) : NaN;
};

describe("Diferansiyel test: Python Oracle vs uygulama içi ONNX", () => {
  let kayit;

  before(() => {
    cy.readFile("tests/parite.json").then((j) => {
      kayit = j;
    });
  });

  it("5 referans girdide |p_uygulama - p_python| < 1e-4", () => {
    expect(kayit.vakalar).to.have.length(5);
    kayit.vakalar.forEach((vaka) => {
      cy.visit("/?parite=1");
      // Model (ONNX + wasm) yüklenmeden hesaplama başlamasın (yükleme ~6 sn sürebilir)
      cy.get('[data-cy="model-durum"]', { timeout: 60000 }).should("contain.text", "hazir");
      kayit.ozellik_sirasi.forEach((ad) => {
        cy.get(`[data-cy="in-${ad}"]`).clear().type(String(vaka.girdi[ad]));
      });
      cy.get('[data-cy="hesapla"]').click();
      cy.get('[data-cy="p"]', { timeout: 30000 })
        .should(($p) => {
          expect(sayiOku($p.text()), `p okunabilir: ${vaka.ad} (görünen metin: "${$p.text()}")`).to.not.be.NaN;
        })
        .then(($p) => {
          const fark = Math.abs(sayiOku($p.text()) - vaka.p);
          cy.log(`${vaka.ad}: uygulama=${$p.text()} python=${vaka.p} fark=${fark}`);
          expect(fark, `parite farkı (${vaka.ad})`).to.be.lessThan(kayit.tolerans);
        });
    });
  });

  it("model yüklendiğinde durum 'hazir' görünür", () => {
    cy.visit("/?parite=1");
    cy.get('[data-cy="model-durum"]', { timeout: 30000 }).should("contain.text", "hazir");
  });

  it("?model=0 ile model kapanır ve oyun bozulmaz (KÖ-10)", () => {
    cy.visit("/?model=0");
    cy.get('[data-cy="model-durum"]').should("contain.text", "kapali");
  });
});
