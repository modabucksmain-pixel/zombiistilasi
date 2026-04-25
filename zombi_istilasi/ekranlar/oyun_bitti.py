# ============================================================
#  ekranlar/oyun_bitti.py — Game Over Ekranı
# ============================================================
import pygame
import math
from ayarlar import GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, KIRMIZI, YESIL, ACIK_GRI


class OyunBitti:
    def __init__(self):
        self.font_buyuk  = pygame.font.SysFont("Consolas", 72, bold=True)
        self.font_orta   = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_kucuk  = pygame.font.SysFont("Consolas", 20)
        self.zaman = 0.0
        self.son_puan = 0
        self.son_dalga = 0
        self.yuksek_skorlar = []
        self.bitis_tipi = "devam"

    # ----------------------------------------------------------
    def ayarla(self, puan, dalga, yuksek_skorlar, bitis_tipi="devam"):

        self.son_puan = puan
        self.son_dalga = dalga
        self.yuksek_skorlar = yuksek_skorlar
        self.zaman = 0.0
        self.bitis_tipi = bitis_tipi

    # ----------------------------------------------------------
    def guncelle(self, dt):
        self.zaman += dt

    # ----------------------------------------------------------
    def ciz(self, ekran):
        zafer = self.bitis_tipi == "zafer"
        ekran.fill((8, 20, 14) if zafer else (25, 8, 8))

        sal = math.sin(self.zaman * 3) * 4
        baslik = self.font_buyuk.render("ZAFER" if zafer else "ÖLDÜN!", True, YESIL if zafer else KIRMIZI)
        ekran.blit(baslik, (GENISLIK // 2 - baslik.get_width() // 2, 80 + int(sal)))

        # Skor ve dalga
        puan_s = self.font_orta.render(f"Puan: {self.son_puan}", True, BEYAZ)
        dalga_s = self.font_orta.render(f"Ulaşılan Dalga: {self.son_dalga}", True, (180, 220, 180))
        ekran.blit(puan_s, (GENISLIK // 2 - puan_s.get_width() // 2, 200))
        ekran.blit(dalga_s, (GENISLIK // 2 - dalga_s.get_width() // 2, 240))

        # High Score Listesi
        hs_baslik = self.font_orta.render("— EN YÜKSEK SKORLAR —", True, YESIL)
        ekran.blit(hs_baslik, (GENISLIK // 2 - hs_baslik.get_width() // 2, 310))
        for i, skor in enumerate(self.yuksek_skorlar[:5]):
            renk = (255, 215, 0) if i == 0 else (200, 200, 200)
            s = self.font_kucuk.render(f"  {i + 1}. {skor}", True, renk)
            ekran.blit(s, (GENISLIK // 2 - s.get_width() // 2, 350 + i * 30))

        # Butonlar
        self._ciz_buton(ekran, "TEKRAR OYNA", GENISLIK // 2, 530, YESIL)
        self._ciz_buton(ekran, "ANA MENÜ",    GENISLIK // 2, 600, (100, 150, 220))

    # ----------------------------------------------------------
    def _ciz_buton(self, ekran, metin, cx, cy, renk):
        fare = pygame.mouse.get_pos()
        bw, bh = 240, 48
        bx, by = cx - bw // 2, cy - bh // 2
        uzerinde = pygame.Rect(bx, by, bw, bh).collidepoint(fare)
        r = tuple(min(255, c + 40) for c in renk) if uzerinde else renk
        pygame.draw.rect(ekran, r, (bx, by, bw, bh), border_radius=10)
        pygame.draw.rect(ekran, BEYAZ, (bx, by, bw, bh), 2, border_radius=10)
        t = self.font_kucuk.render(metin, True, SIYAH if renk == YESIL else BEYAZ)
        ekran.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))

    # ----------------------------------------------------------
    def tik_isle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fare = pygame.mouse.get_pos()
            # Tekrar Oyna
            if pygame.Rect(GENISLIK // 2 - 120, 506, 240, 48).collidepoint(fare):
                return "oyun"
            # Ana Menü
            if pygame.Rect(GENISLIK // 2 - 120, 576, 240, 48).collidepoint(fare):
                return "menu"
        return None
