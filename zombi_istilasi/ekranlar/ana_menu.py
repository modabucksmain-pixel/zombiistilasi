# ============================================================
#  ekranlar/ana_menu.py — Ana Menü
# ============================================================
import pygame
import math
from ayarlar import (
    GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, KIRMIZI,
    YESIL, ACIK_GRI, ARKAPLAN, DURUM_OYUN
)


class AnaMenu:
    def __init__(self):
        self.font_baslik  = pygame.font.SysFont("Consolas", 64, bold=True)
        self.font_alt     = pygame.font.SysFont("Consolas", 22)
        self.font_buton   = pygame.font.SysFont("Consolas", 30, bold=True)
        self.zaman = 0.0
        self.loglar = [
            "Son iletişim: 14:32 — Bölge 7 karantinaya alındı",
            "ARGUS İç Hat: EDEN stabil değil",
            "Saha Raporu: Nüfusun %70'i Dönmüş",
            "Dr. Kerem Aydın: antidotun yarısı elimde",
            "Direktör Selim Koç yayını ele geçirdi",
        ]

        self.butonlar = [
            {"metin": "OYNA",    "durum": DURUM_OYUN,  "renk": YESIL},
            {"metin": "ÇIKIŞ",   "durum": "cikis",     "renk": KIRMIZI},
        ]

    # ----------------------------------------------------------
    def guncelle(self, dt):
        self.zaman += dt

    # ----------------------------------------------------------
    def ciz(self, ekran):
        # Arkaplan gradyan simülasyonu
        ekran.fill(ARKAPLAN)
        self._ciz_arkaplan_detay(ekran)
        self._ciz_baslik(ekran)
        self._ciz_butonlar(ekran)
        self._ciz_lore_loglari(ekran)
        self._ciz_alt_bilgi(ekran)

    # ----------------------------------------------------------
    def _ciz_arkaplan_detay(self, ekran):
        """Animasyonlu ızgara efekti."""
        for i in range(0, GENISLIK + 80, 80):
            offset = int(math.sin(self.zaman * 0.5 + i * 0.05) * 6)
            pygame.draw.line(ekran, (35, 55, 35),
                             (i, 0), (i, YUKSEKLIK), 1)
        for j in range(0, YUKSEKLIK + 80, 80):
            pygame.draw.line(ekran, (35, 55, 35),
                             (0, j), (GENISLIK, j), 1)

    # ----------------------------------------------------------
    def _ciz_baslik(self, ekran):
        # Titreyen başlık
        sal = math.sin(self.zaman * 2) * 3
        baslik_surf = self.font_baslik.render("🧟 ZOMBİ İSTİLASI", True, BEYAZ)
        alt_surf    = self.font_baslik.render("🧟 ZOMBİ İSTİLASI", True, KIRMIZI)

        gx = GENISLIK // 2 - baslik_surf.get_width() // 2
        gy = 140

        # Gölge (kırmızı offset)
        ekran.blit(alt_surf, (gx + 3, gy + 3 + int(sal)))
        ekran.blit(baslik_surf, (gx, gy + int(sal)))

        alt = self.font_alt.render("— Hayatta Kal —", True, (150, 200, 150))
        ekran.blit(alt, (GENISLIK // 2 - alt.get_width() // 2, gy + 75))

    # ----------------------------------------------------------
    def _ciz_butonlar(self, ekran):
        fare = pygame.mouse.get_pos()
        for i, b in enumerate(self.butonlar):
            bx = GENISLIK // 2 - 130
            by = 290 + i * 80
            bw, bh = 260, 54

            uzerinde = pygame.Rect(bx, by, bw, bh).collidepoint(fare)
            renk = b["renk"] if not uzerinde else (
                min(255, b["renk"][0] + 40),
                min(255, b["renk"][1] + 40),
                min(255, b["renk"][2] + 40),
            )
            scale = 1.06 if uzerinde else 1.0
            ybw = int(bw * scale)
            ybh = int(bh * scale)
            ybx = bx - (ybw - bw) // 2
            yby = by - (ybh - bh) // 2

            pygame.draw.rect(ekran, (20, 20, 20), (ybx + 4, yby + 4, ybw, ybh), border_radius=10)
            pygame.draw.rect(ekran, renk, (ybx, yby, ybw, ybh), border_radius=10)
            pygame.draw.rect(ekran, BEYAZ, (ybx, yby, ybw, ybh), 2, border_radius=10)

            metin = self.font_buton.render(b["metin"], True, SIYAH if b["metin"] == "OYNA" else BEYAZ)
            ekran.blit(metin, (ybx + ybw // 2 - metin.get_width() // 2,
                                yby + ybh // 2 - metin.get_height() // 2))

    # ----------------------------------------------------------
    def _ciz_lore_loglari(self, ekran):
        for i, log in enumerate(self.loglar):
            x = int(GENISLIK - ((self.zaman * 85 + i * 280) % (GENISLIK + 900)))
            satir = self.font_alt.render(log, True, (110, 170, 130))
            ekran.blit(satir, (x, YUKSEKLIK - 140 + i * 22))

    def _ciz_alt_bilgi(self, ekran):
        ipucu = self.font_alt.render("WASD: Hareket  |  Fare: Nişan  |  Sol Tık: Ateş  |  ESC: Duraklat", True, (100, 140, 100))
        ekran.blit(ipucu, (GENISLIK // 2 - ipucu.get_width() // 2, YUKSEKLIK - 50))

    # ----------------------------------------------------------
    def tik_isle(self, event, yuksek_skor):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fare = pygame.mouse.get_pos()
            for i, b in enumerate(self.butonlar):
                bx = GENISLIK // 2 - 130
                by = 290 + i * 80
                if pygame.Rect(bx, by, 260, 54).collidepoint(fare):
                    return b["durum"]
        return None
