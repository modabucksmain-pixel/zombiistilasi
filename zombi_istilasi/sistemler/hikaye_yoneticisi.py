# ============================================================
#  sistemler/hikaye_yoneticisi.py — Hikaye Durumu ve NPC Görevleri
#  Kapı kilitleri, görev takibi, NPC diyalog durumları
# ============================================================
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class NPCGorev:
    """Bir NPC'nin verdiği görev."""
    id: str
    npc_isim: str
    aciklama: str
    tip: str              # "terminal_oku", "boss_oldur", "item_topla", "bolge_git"
    hedef: int | str      # Sayısal hedef veya string hedef
    ilerleme: int = 0
    tamamlandi: bool = False
    para_odulu: int = 0
    kristal_odulu: int = 0
    kilit_acar: str = ""  # Tamamlanınca hangi kilidi açar

    @property
    def yuzde(self) -> float:
        if isinstance(self.hedef, int) and self.hedef > 0:
            return min(1.0, self.ilerleme / self.hedef)
        return 1.0 if self.tamamlandi else 0.0


# ── Ana Hikaye Görevleri ─────────────────────────────────────
HIKAYE_GOREVLERI = [
    # Faz 1: Karantina
    NPCGorev(
        id="elif_terminal",
        npc_isim="Dr. Elif",
        aciklama="Karantina'daki 3 terminali oku",
        tip="terminal_oku",
        hedef=3,
        para_odulu=500,
        kristal_odulu=10,
    ),
    NPCGorev(
        id="zeynep_can",
        npc_isim="Sivil Zeynep",
        aciklama="5 can topu topla ve getir",
        tip="item_topla",
        hedef=5,
        para_odulu=400,
        kristal_odulu=5,
    ),
    NPCGorev(
        id="deniz_boss1",
        npc_isim="Komutan Deniz",
        aciklama="Et Göbeği boss'unu yok et",
        tip="boss_oldur",
        hedef="et_gobegi",
        para_odulu=1000,
        kristal_odulu=20,
        kilit_acar="karantina_boss",
    ),
    # Faz 2: Yeraltı
    NPCGorev(
        id="arda_kapi",
        npc_isim="Mühendis Arda",
        aciklama="Yeraltı kontrol terminalini etkinleştir",
        tip="terminal_oku",
        hedef=2,
        para_odulu=600,
        kristal_odulu=12,
    ),
    NPCGorev(
        id="deniz_boss2",
        npc_isim="Komutan Deniz",
        aciklama="Zehir Ustası'nı yok et",
        tip="boss_oldur",
        hedef="zehir_usta",
        para_odulu=1200,
        kristal_odulu=25,
        kilit_acar="yeralti_boss",
    ),
    # Faz 3: Otoyol
    NPCGorev(
        id="deniz_boss3",
        npc_isim="Komutan Deniz",
        aciklama="Alev Kral'ı yok et",
        tip="boss_oldur",
        hedef="alev_kral",
        para_odulu=1500,
        kristal_odulu=30,
        kilit_acar="otoyol_boss",
    ),
    # Final
    NPCGorev(
        id="final_boss",
        npc_isim="Dr. Elif",
        aciklama="Fırtına Lordu'nu yok et — İstanbul'u kurtar",
        tip="boss_oldur",
        hedef="firtina_lord",
        para_odulu=3000,
        kristal_odulu=50,
    ),
]

# ── NPC Diyalogları (duruma göre değişir) ────────────────────
NPC_DIYALOGLARI = {
    # (npc_konum_key, hikaye_aşaması) -> diyalog
    "dr_elif": {
        "bekliyor": [
            "Ben Dr. Elif. Antidot üzerinde çalışıyorum.",
            "Karantina'daki terminallerde veri var. Onları okumalısın.",
            "3 terminal → veri → antidot formülünün yarısı.",
        ],
        "gorev_aktif": [
            "Terminalleri okudun mu? Hâlâ {kalan} terminal kaldı.",
        ],
        "tamamlandi": [
            "Harika! Veriler geldi. Formül ilerleme kaydetti.",
            "Şimdi Yeraltı Lab'a inmeliyiz. Arda kapıyı açacak.",
        ],
    },
    "muhendis_arda": {
        "bekliyor": [
            "Kapı sistemi bende. Ama önce Karantina'yı temizle.",
        ],
        "gorev_aktif": [
            "Yeraltı terminallerini etkinleştir. {kalan} kaldı.",
        ],
        "tamamlandi": [
            "Güzel iş. Otoyol yolu açıldı. Dikkatli ol.",
        ],
    },
    "komutan_deniz": {
        "bekliyor": [
            "Ben Komutan Deniz. Bu bölgelerin boss'larını temizlemen lazım.",
            "Boss'u öldür → kapı açılır → yeni bölge.",
        ],
        "gorev_aktif": [
            "Boss hâlâ aktif. Dikkatli yaklaş.",
        ],
        "tamamlandi": [
            "Boss düştü. Yeni bölge açıldı.",
            "Devam et asker.",
        ],
    },
    "karaborsaci": {
        "her_zaman": [
            "Hoş geldin. Ne lazım? Silah, cephane, her şey var.",
            "Fiyatlar krizde biraz yükseldi. Kusura bakma.",
        ],
    },
}


class HikayeYoneticisi:
    """Ana hikaye durumunu ve NPC görevlerini yönetir."""

    def __init__(self, dunya_haritasi):
        self.dunya = dunya_haritasi
        self.gorevler = [self._kopya(g) for g in HIKAYE_GOREVLERI]
        self.aktif_gorev_index = 0
        self.tamamlanan_gorevler: list[str] = []
        self.bildirimler: list[tuple[str, float]] = []  # (metin, kalan_süre)
        self.zafer = False

    def _kopya(self, g: NPCGorev) -> NPCGorev:
        """Görev kopyası oluşturur."""
        return NPCGorev(
            id=g.id, npc_isim=g.npc_isim, aciklama=g.aciklama,
            tip=g.tip, hedef=g.hedef, para_odulu=g.para_odulu,
            kristal_odulu=g.kristal_odulu, kilit_acar=g.kilit_acar,
        )

    @property
    def aktif_gorev(self) -> NPCGorev | None:
        """Şu anki aktif görev."""
        if self.aktif_gorev_index < len(self.gorevler):
            g = self.gorevler[self.aktif_gorev_index]
            if not g.tamamlandi:
                return g
        return None

    def guncelle(self, dt: float):
        """Bildirim sayaçlarını günceller."""
        self.bildirimler = [(m, s - dt) for m, s in self.bildirimler if s - dt > 0]

    def olay_isle(self, olay_tip: str, veri=None):
        """Oyun olaylarını işler (terminal okuma, boss öldürme vb.)."""
        gorev = self.aktif_gorev
        if not gorev:
            return

        tamamlandi = False

        if olay_tip == "terminal_oku" and gorev.tip == "terminal_oku":
            gorev.ilerleme += 1
            if isinstance(gorev.hedef, int) and gorev.ilerleme >= gorev.hedef:
                tamamlandi = True

        elif olay_tip == "boss_oldu" and gorev.tip == "boss_oldur":
            if veri == gorev.hedef:  # veri = boss_tipi
                tamamlandi = True

        elif olay_tip == "item_topla" and gorev.tip == "item_topla":
            gorev.ilerleme += 1
            if isinstance(gorev.hedef, int) and gorev.ilerleme >= gorev.hedef:
                tamamlandi = True

        if tamamlandi:
            self._gorev_tamamla(gorev)

    def _gorev_tamamla(self, gorev: NPCGorev):
        """Görevi tamamlar ve ödülleri verir."""
        gorev.tamamlandi = True
        self.tamamlanan_gorevler.append(gorev.id)

        # Kapı aç
        if gorev.kilit_acar:
            self.dunya.hikaye_durum[gorev.kilit_acar] = True

        # Bildirim
        self.bildirimler.append((
            f"✅ GÖREV TAMAM: {gorev.aciklama}  +{gorev.para_odulu}₺ +{gorev.kristal_odulu}💎",
            4.0,
        ))

        # Sonraki göreve geç
        self.aktif_gorev_index += 1

        # Final kontrolü
        if gorev.id == "final_boss":
            self.zafer = True

    def odulleri_topla(self) -> tuple[int, int]:
        """Tamamlanan görevlerin ödüllerini toplar."""
        para = sum(g.para_odulu for g in self.gorevler if g.tamamlandi and g.id in self.tamamlanan_gorevler)
        kristal = sum(g.kristal_odulu for g in self.gorevler if g.tamamlandi and g.id in self.tamamlanan_gorevler)
        return para, kristal

    def npc_diyalog(self, npc_rol: str) -> list[str]:
        """NPC'nin mevcut hikaye durumuna göre diyalogunu döndürür."""
        gorev = self.aktif_gorev
        if npc_rol == "satici":
            return NPC_DIYALOGLARI.get("karaborsaci", {}).get("her_zaman", ["..."])

        # Basit diyalog eşleme
        if gorev and gorev.npc_isim == "Dr. Elif" and npc_rol == "gorev":
            key = "dr_elif"
        elif gorev and gorev.npc_isim == "Mühendis Arda" and npc_rol == "gorev":
            key = "muhendis_arda"
        elif npc_rol == "gorev":
            key = "komutan_deniz"
        else:
            return ["Dikkatli ol dışarıda.", "Zombiler her yerde."]

        diyaloglar = NPC_DIYALOGLARI.get(key, {})
        if gorev and not gorev.tamamlandi:
            satirlar = diyaloglar.get("gorev_aktif", diyaloglar.get("bekliyor", ["..."]))
            kalan = ""
            if isinstance(gorev.hedef, int):
                kalan = str(gorev.hedef - gorev.ilerleme)
            return [s.format(kalan=kalan) for s in satirlar]

        return diyaloglar.get("tamamlandi", diyaloglar.get("bekliyor", ["..."]))

    def gorev_paneli_verisi(self) -> dict | None:
        """HUD'da gösterilecek görev bilgisi."""
        gorev = self.aktif_gorev
        if not gorev:
            if self.zafer:
                return {"aciklama": "İstanbul kurtarıldı!", "yuzde": 1.0, "tamamlandi": True}
            return None
        return {
            "aciklama": f"{gorev.npc_isim}: {gorev.aciklama}",
            "yuzde": gorev.yuzde,
            "tamamlandi": gorev.tamamlandi,
            "ilerleme": f"{gorev.ilerleme}/{gorev.hedef}" if isinstance(gorev.hedef, int) else "",
        }
