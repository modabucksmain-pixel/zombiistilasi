# ============================================================
#  sistemler/gorev_sistemi.py — Aktif Görev Sistemi
#  Her dalga başında rastgele 3 görev verilir.
#  Tamamlanan görevler para + kristal verir.
# ============================================================
import random


GOREV_HAVUZU = [
    # (tip, hedef_deger, aciklama_sablonu, para_odulu, kristal_odulu)
    ("oldurme",        15,  "{h} zombi öldür",             300,  3),
    ("oldurme",        30,  "{h} zombi öldür",             600,  6),
    ("oldurme",        50,  "{h} zombi öldür",             1000, 10),
    ("boss_oldurme",    1,  "Bir boss yok et",              800,  15),
    ("boss_oldurme",    2,  "{h} boss yok et",              1500, 25),
    ("kombo",          10,  "{h} kombo yap",                400,  5),
    ("kombo",          20,  "{h} kombo yap",                700,  8),
    ("hasar_alma",    180,  "{h} saniye hasar almadan yak", 500,  8),
    ("cant_doldurma",   3,  "3 can topu topla",             350,  4),
    ("silah_degistir",  5,  "{h} farklı silahla öldür",     600,  7),
    ("element_oldurme","ateş",  "Ateşli silahla 10 zombi öldür", 500, 6),
    ("element_oldurme","buz",   "Buzlu silahla 10 zombi öldür",  500, 6),
    ("element_oldurme","şok",   "Elektrikli silahla 10 öldür",   600, 8),
    ("patlama_oldurme",  8, "{h} zombiyi patlatarak öldür", 700, 9),
    ("dalga_hizli",      1, "Dalgayı 60 saniyede bitir",    900, 12),
]


class Gorev:
    def __init__(self, tanim):
        self.tip = tanim[0]
        self.hedef = tanim[1]
        self.aciklama = tanim[2].format(h=tanim[1])
        self.para_odulu = tanim[3]
        self.kristal_odulu = tanim[4]
        self.ilerleme = 0
        self.tamamlandi = False
        self._dalga_sure = 0.0   # dalga_hizli için

    @property
    def yuzde(self):
        if isinstance(self.hedef, int):
            return min(1.0, self.ilerleme / max(1, self.hedef))
        return 1.0 if self.tamamlandi else 0.0

    def olay_isle(self, olay_tip, veri=None):
        if self.tamamlandi:
            return False

        tatmin = False
        if olay_tip == "oldurme" and self.tip == "oldurme":
            self.ilerleme += 1
            tatmin = self.ilerleme >= self.hedef
        elif olay_tip == "boss_oldurme" and self.tip == "boss_oldurme":
            self.ilerleme += 1
            tatmin = self.ilerleme >= self.hedef
        elif olay_tip == "kombo" and self.tip == "kombo":
            if veri and veri >= self.hedef:
                self.ilerleme = veri
                tatmin = True
        elif olay_tip == "hasar_alma" and self.tip == "hasar_alma":
            # veri = sürekli hasar almadan geçen saniye
            if veri and veri >= self.hedef:
                tatmin = True
        elif olay_tip == "cant_doldurma" and self.tip == "cant_doldurma":
            self.ilerleme += 1
            tatmin = self.ilerleme >= self.hedef
        elif olay_tip == "silah_degistir" and self.tip == "silah_degistir":
            if veri:  # veri = kullanılan benzersiz silah seti
                self.ilerleme = len(veri)
                tatmin = self.ilerleme >= self.hedef
        elif olay_tip == "element_oldurme" and self.tip == "element_oldurme":
            if veri == self.hedef:  # veri = element adı
                self.ilerleme += 1
                tatmin = self.ilerleme >= 10
        elif olay_tip == "patlama_oldurme" and self.tip == "patlama_oldurme":
            self.ilerleme += 1
            tatmin = self.ilerleme >= self.hedef
        elif olay_tip == "dalga_sure" and self.tip == "dalga_hizli":
            # veri = dalgayı bitirmek için geçen saniye
            tatmin = (veri is not None and veri <= 60)

        if tatmin:
            self.tamamlandi = True
        return tatmin


class GorevSistemi:
    def __init__(self):
        self.aktif_gorevler = []
        self.tamamlanan_gorevler = []
        self.bekleme_bildirimleri = []  # (metin, süre)
        self.kullanilan_silahlar = set()
        self.hasarsiz_sure = 0.0
        self._dalga_baslangic_sure = 0.0

    def yeni_dalga_gorevi_ver(self, dalga_no):
        """Her dalga başında 2-3 görev ver."""
        self.aktif_gorevler.clear()
        adet = 3 if dalga_no >= 3 else 2

        # Dalga numarasına göre uygun görevleri filtrele
        havuz = list(GOREV_HAVUZU)
        if dalga_no < 5:
            # İlk dalgalarda boss görevi çıkmasın
            havuz = [g for g in havuz if g[0] != "boss_oldurme"]
        if dalga_no < 3:
            havuz = [g for g in havuz if g[0] not in ("element_oldurme", "patlama_oldurme")]

        secilen = random.sample(havuz, min(adet, len(havuz)))
        self.aktif_gorevler = [Gorev(t) for t in secilen]
        self._dalga_baslangic_sure = 0.0
        self.hasarsiz_sure = 0.0
        self.kullanilan_silahlar = set()

    def guncelle(self, dt, oyuncu_hasar_alindi_mi=False):
        self._dalga_baslangic_sure += dt
        if oyuncu_hasar_alindi_mi:
            self.hasarsiz_sure = 0.0
        else:
            self.hasarsiz_sure += dt
            self._olay_isle("hasar_alma", self.hasarsiz_sure)

        # Bildirim sayaçları
        for b in self.bekleme_bildirimleri[:]:
            b[1] -= dt
            if b[1] <= 0:
                self.bekleme_bildirimleri.remove(b)

    def olay_isle(self, olay_tip, veri=None):
        self._olay_isle(olay_tip, veri)

    def _olay_isle(self, olay_tip, veri):
        for gorev in self.aktif_gorevler:
            if gorev.tamamlandi:
                continue
            tamamlandi = gorev.olay_isle(olay_tip, veri)
            if tamamlandi:
                self.tamamlanan_gorevler.append(gorev)
                self.bekleme_bildirimleri.append(
                    [f"✅ GÖREV TAMAM: {gorev.aciklama[:30]}  +{gorev.para_odulu}₺ +{gorev.kristal_odulu}💎", 3.0]
                )

    def silah_kullanildi(self, silah_key, zombi_oldu):
        """Silah ile zombi öldürüldüğünde çağırılır."""
        self.kullanilan_silahlar.add(silah_key)
        self._olay_isle("silah_degistir", self.kullanilan_silahlar)

    def dalga_bitti(self, sure=None):
        """Dalga bittiğinde çağırılır."""
        gecen = sure or self._dalga_baslangic_sure
        self._olay_isle("dalga_sure", gecen)

    def toplam_odulleri_topla(self):
        """Tamamlanan görevlerin ödüllerini topla ve listeyi temizle."""
        toplam_para = sum(g.para_odulu for g in self.tamamlanan_gorevler)
        toplam_kristal = sum(g.kristal_odulu for g in self.tamamlanan_gorevler)
        self.tamamlanan_gorevler.clear()
        return toplam_para, toplam_kristal

    def ciz(self, ekran, font_k, font_m, genislik, yukseklik):
        """Ekrana görev panelini ve bildirimleri çizer."""
        import pygame
        panel_x = genislik - 260
        panel_y = 190
        panel_gen = 250
        satir_yuk = 52

        for i, gorev in enumerate(self.aktif_gorevler):
            py = panel_y + i * satir_yuk
            # Arka panel
            surf = pygame.Surface((panel_gen, satir_yuk - 4), pygame.SRCALPHA)
            if gorev.tamamlandi:
                surf.fill((20, 80, 20, 160))
            else:
                surf.fill((10, 10, 30, 160))
            ekran.blit(surf, (panel_x, py))

            # Çerçeve
            renk = (50, 200, 50) if gorev.tamamlandi else (100, 100, 160)
            pygame.draw.rect(ekran, renk, (panel_x, py, panel_gen, satir_yuk - 4), 1,
                             border_radius=4)

            # Metin
            metin = ("✅ " if gorev.tamamlandi else "◻ ") + gorev.aciklama[:28]
            t = font_k.render(metin, True, (200, 255, 200) if gorev.tamamlandi else (200, 200, 255))
            ekran.blit(t, (panel_x + 5, py + 4))

            # İlerleme barı
            if not gorev.tamamlandi and isinstance(gorev.hedef, int):
                bar_gen = panel_gen - 10
                dolu = int(bar_gen * gorev.yuzde)
                pygame.draw.rect(ekran, (30, 30, 60), (panel_x + 5, py + 32, bar_gen, 8),
                                 border_radius=3)
                if dolu > 0:
                    pygame.draw.rect(ekran, (80, 120, 255), (panel_x + 5, py + 32, dolu, 8),
                                     border_radius=3)
                ilerleme_t = font_k.render(
                    f"{gorev.ilerleme}/{gorev.hedef}", True, (180, 180, 220))
                ekran.blit(ilerleme_t, (panel_x + 5, py + 20))

            # Ödül
            odul_t = font_k.render(f"+{gorev.para_odulu}₺ +{gorev.kristal_odulu}💎",
                                   True, (200, 180, 80))
            ekran.blit(odul_t, (panel_x + panel_gen - odul_t.get_width() - 5, py + 20))

        # Görev tamamlama bildirimleri (alt)
        for j, (metin, kalan) in enumerate(self.bekleme_bildirimleri):
            alpha = int(255 * min(1.0, kalan))
            bs = font_m.render(metin[:50], True, (80, 255, 120))
            bs.set_alpha(alpha)
            ekran.blit(bs, (genislik // 2 - bs.get_width() // 2,
                             yukseklik - 160 - j * 36))
