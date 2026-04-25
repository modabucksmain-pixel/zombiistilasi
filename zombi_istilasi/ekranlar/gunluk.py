"""Kayıt/Günlük ekranı."""

from __future__ import annotations

import pygame
from ayarlar import ACIK_GRI, BEYAZ, GENISLIK, KIRMIZI, YUKSEKLIK


class GunlukEkrani:
    """Haritada açılan lore kayıtlarını listeler."""

    def __init__(self) -> None:
        self.font_b = pygame.font.SysFont("Consolas", 42, bold=True)
        self.font_s = pygame.font.SysFont("Consolas", 22)
        self.records: list[str] = []

    def ayarla(self, records: list[str]) -> None:
        self.records = records

    def ciz(self, ekran: pygame.Surface) -> None:
        ekran.fill((12, 14, 18))
        title = self.font_b.render("ARGUS KAYITLARI", True, BEYAZ)
        ekran.blit(title, (GENISLIK // 2 - title.get_width() // 2, 40))
        tip = self.font_s.render("ESC: Geri", True, ACIK_GRI)
        ekran.blit(tip, (GENISLIK - tip.get_width() - 30, 24))

        if not self.records:
            t = self.font_s.render("Henüz kayıt açılmadı.", True, KIRMIZI)
            ekran.blit(t, (80, 140))
            return

        for i, record in enumerate(self.records[-14:]):
            r = self.font_s.render(f"{i+1:02d}. {record}", True, (210, 220, 235))
            ekran.blit(r, (80, 130 + i * 34))
