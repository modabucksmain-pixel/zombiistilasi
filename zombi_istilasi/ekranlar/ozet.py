# ============================================================
#  ekranlar/ozet.py — Run Sonu Özet Ekranı (Sinematik)
# ============================================================
import pygame
import math
import random
from ayarlar import GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, KIRMIZI, YESIL, SARI, ALTIN, CAMGOBEGI, MOR


class OzetEkrani:
    """Oyun bitince Kerem'in hikayesini sinematik olarak gösterir."""

    def __init__(self):
        self.font_baslik = pygame.font.SysFont("Consolas", 52, bold=True)
        self.font_buyuk = pygame.font.SysFont("Consolas", 32, bold=True)
        self.font_normal = pygame.font.SysFont("Consolas", 22)
        self.font_kucuk = pygame.font.SysFont("Consolas", 17)
        self.zaman = 0.0
        self.dalga_no = 0
        self.zombi_sayisi = 0
        self.bolgeler: list[str] = []
        self.zafer = False
        self.parcaciklar: list[dict] = []
        self._satirlar_hazirla()

    def _satirlar_hazirla(self):
        self._istatistik_satirlari: list[tuple[str, str, tuple]] = []

    def ayarla(self, dalga_no: int, zombi_sayisi: int, bolgeler: list[str], zafer: bool) -> None:
        self.dalga_no = dalga_no
        self.zombi_sayisi = zombi_sayisi
        self.bolgeler = bolgeler
        self.zafer = zafer
        self.zaman = 0.0
        self.parcaciklar = []

        if zafer:
            for _ in range(80):
                self.parcaciklar.append({
                    "x": random.randint(0, GENISLIK),
                    "y": random.randint(-50, YUKSEKLIK),
                    "vx": random.uniform(-60, 60),
                    "vy": random.uniform(-120, -20),
                    "omur": random.uniform(1.5, 4.0),
                    "max_omur": 3.0,
                    "renk": random.choice([(255, 220, 0), (255, 100, 50), (100, 255, 150), (100, 200, 255)]),
                    "r": random.randint(3, 7),
                })

    def guncelle(self, dt: float) -> None:
        self.zaman += dt
        for p in self.parcaciklar:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["omur"] -= dt
            p["vy"] += 60 * dt  # yerçekimi

    def ciz(self, ekran: pygame.Surface) -> None:
        ekran.fill((5, 8, 12))
        self._ciz_arkaplan(ekran)
        self._ciz_parcaciklar(ekran)
        self._ciz_icerik(ekran)
        self._ciz_devam_ipucu(ekran)

    def _ciz_arkaplan(self, ekran: pygame.Surface) -> None:
        for i in range(0, GENISLIK, 90):
            pygame.draw.line(ekran, (14, 22, 18), (i, 0), (i, YUKSEKLIK), 1)
        for j in range(0, YUKSEKLIK, 90):
            pygame.draw.line(ekran, (14, 22, 18), (0, j), (GENISLIK, j), 1)

        # Dramatik kenar ışıması
        renk = (255, 220, 0) if self.zafer else (180, 20, 20)
        for i in range(5):
            alpha = 30 - i * 5
            s = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
            pygame.draw.rect(s, (*renk, alpha), (i * 4, i * 4, GENISLIK - i * 8, YUKSEKLIK - i * 8), 4)
            ekran.blit(s, (0, 0))

    def _ciz_parcaciklar(self, ekran: pygame.Surface) -> None:
        for p in self.parcaciklar:
            if p["omur"] <= 0:
                continue
            alpha = int(255 * (p["omur"] / p["max_omur"]))
            s = pygame.Surface((p["r"] * 2, p["r"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["renk"], alpha), (p["r"], p["r"]), p["r"])
            ekran.blit(s, (int(p["x"]) - p["r"], int(p["y"]) - p["r"]))

    def _ciz_icerik(self, ekran: pygame.Surface) -> None:
        # Başlık belirir
        fade = min(1.0, self.zaman / 1.5)
        alpha = int(255 * fade)

        if self.zafer:
            baslik_text = "🏆 ZAFER — İSTANBUL KURTARILDI!"
            baslik_renk = ALTIN
            alt_text = "Antidot tamamlandı. ARGUS Protokolü iptal edildi."
            alt_renk = YESIL
        else:
            baslik_text = "💀 DR. KEREM AYDIN DÜŞTÜ"
            baslik_renk = KIRMIZI
            alt_text = "Formül tamamlanamadı. Şehir hâlâ karanlıkta."
            alt_renk = (200, 80, 80)

        baslik = self.font_baslik.render(baslik_text, True, baslik_renk)
        baslik.set_alpha(alpha)
        ekran.blit(baslik, (GENISLIK // 2 - baslik.get_width() // 2, 80))

        alt = self.font_normal.render(alt_text, True, alt_renk)
        alt.set_alpha(alpha)
        ekran.blit(alt, (GENISLIK // 2 - alt.get_width() // 2, 148))

        pygame.draw.line(ekran, (100, 100, 120), (GENISLIK // 2 - 300, 185), (GENISLIK // 2 + 300, 185), 1)

        # İstatistikler (kademeli belirir)
        istatistikler = [
            ("Ulaşılan Dalga", f"{self.dalga_no}", CAMGOBEGI),
            ("Etkisiz Hale Getirilen Dönmüş", f"{self.zombi_sayisi}", (255, 120, 120)),
            ("Keşfedilen Bölgeler", f"{len(self.bolgeler)}", YESIL),
            ("Bölgeler", " · ".join(self.bolgeler[:3]) or "—", (180, 200, 180)),
        ]

        panel = pygame.Surface((700, 260), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 15, 20, 200), (0, 0, 700, 260), border_radius=16)
        pygame.draw.rect(panel, (50, 80, 70, 180), (0, 0, 700, 260), 2, border_radius=16)
        px, py = GENISLIK // 2 - 350, 210
        panel.set_alpha(alpha)
        ekran.blit(panel, (px, py))

        for i, (etiket, deger, renk) in enumerate(istatistikler):
            delay_fade = min(1.0, max(0.0, (self.zaman - 0.5 - i * 0.3) / 0.6))
            da = int(255 * delay_fade)
            et = self.font_kucuk.render(etiket, True, (150, 160, 160))
            et.set_alpha(da)
            dg = self.font_buyuk.render(deger, True, renk)
            dg.set_alpha(da)
            ekran.blit(et, (px + 30, py + 20 + i * 56))
            ekran.blit(dg, (px + 30, py + 36 + i * 56))

        # Hikaye sonu metni
        if self.zafer:
            mesajlar = [
                "Dr. Kerem Aydın antidotu tamamladı.",
                "ARGUS'ın kötülüğü gün yüzüne çıktı.",
                "İstanbul yavaş yavaş kendine dönmeye başladı.",
                "Selim Koç tutuklandı.",
            ]
        else:
            mesajlar = [
                "Kerem düştü. Ama formülün bir parçası burada.",
                "Biri bu görevi sürdürmeli.",
                "ARGUS hâlâ ayakta.",
                "Belki bir sonraki deneme...",
            ]

        for i, m in enumerate(mesajlar):
            delay_fade = min(1.0, max(0.0, (self.zaman - 1.5 - i * 0.4) / 0.5))
            da = int(255 * delay_fade)
            mt = self.font_kucuk.render(f"▸ {m}", True, (170, 190, 180))
            mt.set_alpha(da)
            ekran.blit(mt, (GENISLIK // 2 - 300, 500 + i * 28))

    def _ciz_devam_ipucu(self, ekran: pygame.Surface) -> None:
        if self.zaman > 2.5:
            puls = int(200 + 55 * math.sin(self.zaman * 3))
            t = self.font_kucuk.render("ENTER: Devam", True, (puls, puls, puls))
            ekran.blit(t, (GENISLIK // 2 - t.get_width() // 2, YUKSEKLIK - 50))
