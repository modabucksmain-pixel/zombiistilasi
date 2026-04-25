"""Hikaye cutscene ve anlatım katmanı."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import pygame

from ayarlar import BEYAZ, SIYAH, KIRMIZI, GENISLIK, YUKSEKLIK


@dataclass(slots=True)
class CutsceneLine:
    """Tek satırlık cutscene girdisi."""

    speaker: str
    text: str


CHAPTER_DATA: dict[int, dict[str, object]] = {
    1: {
        "title": "BÖLÜM I — Karantina",
        "subtitle": "2031 · ARGUS Protokolü kırıldı",
        "lines": [
            CutsceneLine("Sistem", "Son iletişim: 14:32 — Bölge 7 karantinaya alındı."),
            CutsceneLine("Kerem", "EDEN virüsü... yarım antidot bende."),
            CutsceneLine("Kerem", "Diğer yarı ARGUS yedek sunucusunda olmalı."),
            CutsceneLine("Kerem", "48 saatte şehir düştü. Ama henüz bitmedi."),
        ],
    },
    2: {
        "title": "BÖLÜM II — ARGUS Yeraltı",
        "subtitle": "Gerçekler, betonun altına gömüldü",
        "lines": [
            CutsceneLine("Kerem", "Yeraltı laboratuvarlarına iniyorum."),
            CutsceneLine("Radyo", "Direktör Selim Koç canlı yayınlara el koydu."),
            CutsceneLine("Kerem", "Bu bir kaza değilmiş. Planlı bir salınım."),
            CutsceneLine("Kerem", "Sunucu çekirdeği bende olana kadar durmak yok."),
        ],
    },
    3: {
        "title": "BÖLÜM III — Sıfır Noktası",
        "subtitle": "Antidot ya da yıkım",
        "lines": [
            CutsceneLine("Selim Koç", "Kaos yeni düzenin başlangıcıdır."),
            CutsceneLine("Kerem", "Ben düzeni değil, insanları geri getireceğim."),
            CutsceneLine("Sistem", "ARGUS Reaktör Odası — son kilit açıldı."),
            CutsceneLine("Kerem", "Bu gece, İstanbul'un kaderi belli olacak."),
        ],
    },
}


class CutscenePlayer:
    """Dalga öncesi kayan metinli cutscene çizer."""

    def __init__(self) -> None:
        self.font_title = pygame.font.SysFont("Consolas", 46, bold=True)
        self.font_text = pygame.font.SysFont("Consolas", 26)
        self.font_sub = pygame.font.SysFont("Consolas", 20)
        self.active = False
        self.chapter = 1
        self.duration = 10.0
        self.timer = 0.0
        self._lines: list[CutsceneLine] = []

    def start(self, chapter: int, duration: float = 10.0) -> None:
        data = CHAPTER_DATA.get(chapter, CHAPTER_DATA[1])
        self.chapter = chapter
        self.duration = duration
        self.timer = duration
        self.active = True
        self._lines = list(data["lines"])  # type: ignore[index]

    def skip(self) -> None:
        self.active = False
        self.timer = 0.0

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.timer -= dt
        if self.timer <= 0:
            self.skip()

    def draw(self, screen: pygame.Surface) -> None:
        if not self.active:
            return
        data = CHAPTER_DATA.get(self.chapter, CHAPTER_DATA[1])
        overlay = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 232))
        screen.blit(overlay, (0, 0))

        title = self.font_title.render(str(data["title"]), True, BEYAZ)
        sub = self.font_sub.render(str(data["subtitle"]), True, (180, 180, 180))
        screen.blit(title, (GENISLIK // 2 - title.get_width() // 2, 90))
        screen.blit(sub, (GENISLIK // 2 - sub.get_width() // 2, 145))

        progress = 1.0 - (self.timer / max(0.01, self.duration))
        start_y = int(YUKSEKLIK + 180 - progress * (YUKSEKLIK + 300))
        for i, line in enumerate(self._lines):
            color = KIRMIZI if line.speaker == "Selim Koç" else BEYAZ
            txt = self.font_text.render(f"{line.speaker}: {line.text}", True, color)
            screen.blit(txt, (100, start_y + i * 44))

        tip = self.font_sub.render("SPACE: Atla", True, (220, 220, 220))
        screen.blit(tip, (GENISLIK - tip.get_width() - 24, YUKSEKLIK - 34))


class BossGirisBildirim:
    """Boss geldiğinde isim + replik gösterir."""

    def __init__(self) -> None:
        self.font_b = pygame.font.SysFont("Consolas", 42, bold=True)
        self.font_s = pygame.font.SysFont("Consolas", 24)
        self.timer = 0.0
        self.boss_name = ""
        self.line = ""

    def trigger(self, boss_name: str, line: str) -> None:
        self.boss_name = boss_name
        self.line = line
        self.timer = 3.0

    def update(self, dt: float) -> None:
        if self.timer > 0:
            self.timer -= dt

    def draw(self, screen: pygame.Surface) -> None:
        if self.timer <= 0:
            return
        alpha = min(255, int(255 * (self.timer / 3.0)))
        bar = pygame.Surface((GENISLIK, 120), pygame.SRCALPHA)
        bar.fill((30, 0, 0, int(180 + alpha * 0.2)))
        screen.blit(bar, (0, YUKSEKLIK // 2 - 60))
        t = self.font_b.render(self.boss_name, True, (255, 120, 120))
        l = self.font_s.render(self.line, True, BEYAZ)
        t.set_alpha(alpha)
        l.set_alpha(alpha)
        screen.blit(t, (GENISLIK // 2 - t.get_width() // 2, YUKSEKLIK // 2 - 40))
        screen.blit(l, (GENISLIK // 2 - l.get_width() // 2, YUKSEKLIK // 2 + 8))


def chapter_from_wave(wave: int) -> int:
    """Dalga numarasına göre bölüm döndürür."""
    if wave >= 21:
        return 3
    if wave >= 11:
        return 2
    return 1


def iter_loading_notes() -> Iterable[str]:
    """Shop geçişinde kullanılacak Kerem notları."""
    notes = [
        "EDEN suşu sıcaklıkta kararlı, ama UV'de kırılgan.",
        "Selim, klinik fazı beklemeden yayılım emri verdi.",
        "Dönmüş bireylerde ağrı reseptörü kapanıyor.",
        "Antidotun ikinci yarısı muhtemelen şifreli.",
        "Karantina kuleleri sinyal bozucu ile kilitlenmiş.",
    ]
    while True:
        for n in notes:
            yield n
