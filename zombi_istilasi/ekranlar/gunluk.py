# ============================================================
#  ekranlar/gunluk.py — Günlük/Kayıt Ekranı (Lore)
# ============================================================
import pygame
import math
from ayarlar import GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, KIRMIZI, YESIL, ALTIN, CAMGOBEGI


class GunlukEkrani:
    """ESC → Günlükler ekranı. Açılan ARGUS kayıtlarını gösterir."""

    def __init__(self):
        self.font_baslik = pygame.font.SysFont("Consolas", 36, bold=True)
        self.font_kart = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_metin = pygame.font.SysFont("Consolas", 15)
        self.zaman = 0.0
        self.kayitlar: list[str] = []
        self.secili_index = 0
        self.kaydirma = 0

    def ayarla(self, kayitlar: list[str]) -> None:
        self.kayitlar = kayitlar or []
        self.secili_index = 0

    def guncelle(self, dt: float) -> None:
        self.zaman += dt

    def ciz(self, ekran: pygame.Surface) -> None:
        ekran.fill((6, 10, 8))

        # Arka plan ızgara
        for i in range(0, GENISLIK, 60):
            pygame.draw.line(ekran, (12, 20, 14), (i, 0), (i, YUKSEKLIK), 1)
        for j in range(0, YUKSEKLIK, 60):
            pygame.draw.line(ekran, (12, 20, 14), (0, j), (GENISLIK, j), 1)

        # Üst panel
        pygame.draw.rect(ekran, (8, 18, 12), (0, 0, GENISLIK, 80))
        pygame.draw.line(ekran, (50, 150, 80), (0, 80), (GENISLIK, 80), 2)

        t_baslik = self.font_baslik.render("📂 ARGUS KAYIT ARŞİVİ", True, CAMGOBEGI)
        ekran.blit(t_baslik, (50, 22))

        bilgi = self.font_metin.render(f"{len(self.kayitlar)} kayıt bulundu  |  ESC: Geri", True, (100, 160, 100))
        ekran.blit(bilgi, (GENISLIK - bilgi.get_width() - 30, 32))

        if not self.kayitlar:
            bos = self.font_kart.render("Henüz kayıt açılmadı. Haritayı keşfet!", True, (120, 150, 120))
            ekran.blit(bos, (GENISLIK // 2 - bos.get_width() // 2, YUKSEKLIK // 2))
            return

        # Sol liste
        liste_x, liste_y = 40, 100
        for i, kayit in enumerate(self.kayitlar[:20]):
            ky = liste_y + i * 38
            renk = CAMGOBEGI if i == self.secili_index else (120, 160, 130)
            bg = (15, 35, 20) if i == self.secili_index else (10, 18, 12)

            pygame.draw.rect(ekran, bg, (liste_x, ky - 5, 480, 32), border_radius=6)
            if i == self.secili_index:
                pygame.draw.rect(ekran, (50, 140, 70), (liste_x, ky - 5, 480, 32), 1, border_radius=6)

            kisa = kayit[:55] + ("…" if len(kayit) > 55 else "")
            t = self.font_metin.render(f"[{i+1:02d}] {kisa}", True, renk)
            ekran.blit(t, (liste_x + 10, ky))

        # Sağ detay paneli
        if self.secili_index < len(self.kayitlar):
            seçili = self.kayitlar[self.secili_index]
            panel_x, panel_y = 560, 100
            pygame.draw.rect(ekran, (8, 22, 14), (panel_x, panel_y, GENISLIK - panel_x - 30, YUKSEKLIK - panel_y - 30), border_radius=12)
            pygame.draw.rect(ekran, (50, 130, 70), (panel_x, panel_y, GENISLIK - panel_x - 30, YUKSEKLIK - panel_y - 30), 2, border_radius=12)

            t = self.font_kart.render("KAYIT İÇERİĞİ:", True, (120, 200, 140))
            ekran.blit(t, (panel_x + 20, panel_y + 20))
            pygame.draw.line(ekran, (50, 130, 70), (panel_x + 20, panel_y + 45), (GENISLIK - 60, panel_y + 45), 1)

            # Metni kelimeler halinde wrap et
            kelimeler = seçili.split()
            satirlar = []
            satir = ""
            for k in kelimeler:
                if len(satir + " " + k) * 8 < (GENISLIK - panel_x - 80):
                    satir = (satir + " " + k).strip()
                else:
                    satirlar.append(satir)
                    satir = k
            if satir:
                satirlar.append(satir)

            for i, satir in enumerate(satirlar):
                st = self.font_metin.render(satir, True, (180, 220, 190))
                ekran.blit(st, (panel_x + 20, panel_y + 60 + i * 24))

        # Alt kontrol bilgisi
        kontrol = self.font_metin.render("↑/↓: Seç  |  ESC: Geri", True, (70, 120, 80))
        ekran.blit(kontrol, (40, YUKSEKLIK - 30))

    def tik_isle(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "geri"
            if event.key == pygame.K_UP:
                self.secili_index = max(0, self.secili_index - 1)
            if event.key == pygame.K_DOWN:
                self.secili_index = min(len(self.kayitlar) - 1, self.secili_index + 1)
        return None
