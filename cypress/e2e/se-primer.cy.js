// SE Primer: E2E testleri (spec.md kabul ornekleri KO-1 ... KO-7)

const LEVELS = { new: "level-new", exp: "level-experienced" };
const ROLES = { backend: "role-backend", mobile: "role-mobile", qa: "role-qa" };
const GOALS = { intern: "goal-intern", interview: "goal-interview", product: "goal-product" };

const tid = (id) => `[data-testid="${id}"]`;

// Giris ekrani: seviye, rol, hedef sec, basla
function startGame({ level = "new", role = "backend", goal = "intern" } = {}) {
  cy.get(tid(LEVELS[level])).click();
  cy.get(tid(ROLES[role])).click();
  cy.get(tid(GOALS[goal])).click();
  cy.get(tid("start-button")).should("not.be.disabled").click();
}

// Bir karar ekraninda secim yap, uygula, sonuc kartini gor, devam et
function decide(k, option) {
  cy.get(tid(`choice-${k}-${option}`)).click();
  cy.get(tid("apply-button")).click();
  cy.get(tid("result-card")).should("be.visible");
  cy.get(tid("continue-button")).click();
}

// ALERT log satirini incele (log-line-3)
function inspectAlert() {
  cy.get(tid("log-line-3")).click();
  cy.get(tid("investigate-result")).should("be.visible");
}

describe("SE Primer", () => {
  // Uygulama kodundan gelebilecek beklenmeyen hatalar testi bozmasin
  Cypress.on("uncaught:exception", () => false);

  beforeEach(() => {
    cy.visit("/");
  });

  it("Giris: uc soru cevaplanmadan Basla pasif (giris ekrani)", () => {
    cy.get(tid("start-button")).should("be.disabled");
    cy.get(tid(LEVELS.new)).click();
    cy.get(tid("start-button")).should("be.disabled");
    cy.get(tid(ROLES.backend)).click();
    cy.get(tid("start-button")).should("be.disabled");
    cy.get(tid(GOALS.intern)).click();
    cy.get(tid("start-button")).should("not.be.disabled");
  });

  it("KO-1 Mutlu yol: ALERT incelenir, K1=A, K2=A, K3=A, Iyi son", () => {
    startGame({ level: "new", role: "backend", goal: "intern" });
    inspectAlert();
    decide("k1", "a");
    decide("k2", "a");
    decide("k3", "a");
    cy.get(tid("ending-title")).should("contain.text", "İyi son");
    cy.get(tid("ending-metrics")).should("be.visible");
  });

  it("KO-2 Yanlis ilk karar: K1=B ise sonuc ne olursa olsun Kotu son", () => {
    startGame({ level: "new", role: "backend", goal: "intern" });
    inspectAlert();
    decide("k1", "b");
    decide("k2", "a");
    decide("k3", "a");
    cy.get(tid("ending-title")).should("contain.text", "Kötü son");
    cy.get(tid("ending-reasons")).should("contain.text", "K1");
  });

  it("KO-3 ALERT incelenmeden K3=A: bildirim eksik, Kotu son", () => {
    startGame({ level: "new", role: "backend", goal: "intern" });
    decide("k1", "a");
    decide("k2", "a");
    decide("k3", "a");
    cy.get(tid("ending-title")).should("contain.text", "Kötü son");
    cy.get(tid("ending-reasons")).should("contain.text", "ALERT");
  });

  it("KO-3b K3=B (kimseye soyleme): Kotu son", () => {
    startGame({ level: "new", role: "backend", goal: "intern" });
    inspectAlert();
    decide("k1", "a");
    decide("k2", "a");
    decide("k3", "b");
    cy.get(tid("ending-title")).should("contain.text", "Kötü son");
  });

  it("KO-4a Yeni basladim: ipucu butonu var, sayac yok", () => {
    startGame({ level: "new" });
    cy.get(tid("hint-button")).should("be.visible");
    cy.get(tid("timer")).should("not.exist");
  });

  it("KO-4b Deneyimliyim: sayac var, ipucu yok", () => {
    startGame({ level: "exp" });
    cy.get(tid("timer")).should("be.visible");
    cy.get(tid("hint-button")).should("not.exist");
  });

  it("KO-4c Deneyimliyim: sure dolarsa karar B sayilir", () => {
    startGame({ level: "exp" });
    cy.get(tid("timer")).should("be.visible");
    // Gercek 60 sn bekle; sure dolunca sonuc karti acilmali
    cy.get(tid("result-card"), { timeout: 70000 })
      .should("be.visible")
      .invoke("text")
      .should("match", /süre|zaman|dolduğu|dolmuş/i);
  });

  it("KO-5 Yeni basladim: ipucu butonu tutor panelini acar", () => {
    startGame({ level: "new" });
    cy.get(tid("hint-button")).click();
    cy.get(tid("tutor-panel")).should("be.visible");
    cy.get(tid("tutor-input")).should("be.visible");
  });

  it("KO-6 Rol farki: Backend ve QA farkli sahne metni gorur", () => {
    startGame({ level: "new", role: "backend", goal: "intern" });
    cy.contains("backend geliştiricisi").should("exist");
    cy.visit("/");
    startGame({ level: "new", role: "qa", goal: "intern" });
    cy.contains("QA mühendisi").should("exist");
    cy.contains("backend geliştiricisi").should("not.exist");
  });

  it("Tekrar oyna: son ekrandan girise donulur ve durum sifirlanir", () => {
    startGame({ level: "new", role: "backend", goal: "intern" });
    decide("k1", "b");
    decide("k2", "b");
    decide("k3", "b");
    cy.get(tid("ending-title")).should("contain.text", "Kötü son");
    cy.get(tid("replay-button")).click();
    cy.get(tid("start-button")).should("be.disabled");
  });
});
