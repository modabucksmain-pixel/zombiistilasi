"""Run sonu hikaye özeti ekranı."""

from __future__ import annotations

import pygame
from ayarlar import BEYAZ, GENISLIK, YESIL, YUKSEKLIK


class OzetEkrani:
    """Oyun bitiminde sinematik özet gösterir."""

    def __init__(self) -> None:
        self.font_b = pygame.font.SysFont("Consolas", 44, bold=True)
        self.font_s = pygame.font.SysFont("Consolas", 24)
        self.timer = 0.0
        self.lines: list[str] = []
        self.ending = "devam"

    def ayarla(self, dalga: int, zombi: int, bolgeler: list[str], kazandi: bool) -> None:
        self.timer = 0.0
        self.ending = "zafer" if kazandi else "devam"
        son = "Antidot tamamlandı. İstanbul için umut var." if kazandi else "Kerem düştü, ama ARGUS Protokolü sürüyor."
        self.lines = [
            "Dr. Kerem Aydın — Saha Raporu",
            f"Ulaşılan dalga: {dalga}",
            f"Etkisiz hale getirilen dönmüş: {zombi}",
            f"Geçilen bölgeler: {', '.join(bolgeler) if bolgeler else 'Karantina'}",
            son,
        ]

    def guncelle(self, dt: float) -> None:
        self.timer += dt

    def ciz(self, ekran: pygame.Surface) -> None:
        ekran.fill((6, 8, 12) if self.ending == "zafer" else (20, 8, 8))
        t = self.font_b.render("KEREM'İN HİKAYESİ", True, BEYAZ)
        ekran.blit(t, (GENISLIK // 2 - t.get_width() // 2, 70))

        reveal = int(self.timer * 2.2) + 1
        for i, line in enumerate(self.lines[:reveal]):
            col = YESIL if i == len(self.lines) - 1 and self.ending == "zafer" else (220, 220, 220)
            s = self.font_s.render(line, True, col)
            ekran.blit(s, (120, 190 + i * 54))

        tip = self.font_s.render("ENTER: Devam", True, (180, 180, 180))
        ekran.blit(tip, (GENISLIK - tip.get_width() - 34, YUKSEKLIK - 44))
