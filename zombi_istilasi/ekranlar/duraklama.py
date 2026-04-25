# ============================================================
#  ekranlar/duraklama.py — Duraklama Menüsü
# ============================================================
import pygame
from ayarlar import GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, YESIL, KIRMIZI


class Duraklama:
    def __init__(self):
        self.font_buyuk = pygame.font.SysFont("Consolas", 54, bold=True)
        self.font_orta  = pygame.font.SysFont("Consolas", 26, bold=True)

    # ----------------------------------------------------------
    def ciz(self, ekran):
        # Yarı saydam koyu katman
        overlay = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        ekran.blit(overlay, (0, 0))

        baslik = self.font_buyuk.render("⏸ DURAKLATILDI", True, BEYAZ)
        ekran.blit(baslik, (GENISLIK // 2 - baslik.get_width() // 2, 200))

        self._ciz_buton(ekran, "DEVAM ET",  GENISLIK // 2, 320, YESIL)
        self._ciz_buton(ekran, "KAYITLAR",  GENISLIK // 2, 390, (180, 180, 80))
        self._ciz_buton(ekran, "META",      GENISLIK // 2, 460, (120, 80, 220))
        self._ciz_buton(ekran, "ANA MENÜ",  GENISLIK // 2, 530, (100, 150, 220))
        self._ciz_buton(ekran, "ÇIKIŞ",     GENISLIK // 2, 600, KIRMIZI)

    # ----------------------------------------------------------
    def _ciz_buton(self, ekran, metin, cx, cy, renk):
        fare = pygame.mouse.get_pos()
        bw, bh = 240, 50
        bx, by = cx - bw // 2, cy - bh // 2
        uzerinde = pygame.Rect(bx, by, bw, bh).collidepoint(fare)
        r = tuple(min(255, c + 40) for c in renk) if uzerinde else renk
        pygame.draw.rect(ekran, r, (bx, by, bw, bh), border_radius=10)
        pygame.draw.rect(ekran, BEYAZ, (bx, by, bw, bh), 2, border_radius=10)
        t = self.font_orta.render(metin, True, SIYAH if renk == YESIL else BEYAZ)
        ekran.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))

    # ----------------------------------------------------------
    def tik_isle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fare = pygame.mouse.get_pos()
            if pygame.Rect(GENISLIK // 2 - 120, 295, 240, 50).collidepoint(fare):
                return "devam"
            if pygame.Rect(GENISLIK // 2 - 120, 365, 240, 50).collidepoint(fare):
                return "gunluk"
            if pygame.Rect(GENISLIK // 2 - 120, 435, 240, 50).collidepoint(fare):
                return "meta"
            if pygame.Rect(GENISLIK // 2 - 120, 505, 240, 50).collidepoint(fare):
                return "menu"
            if pygame.Rect(GENISLIK // 2 - 120, 575, 240, 50).collidepoint(fare):
                return "cikis"
        return None
