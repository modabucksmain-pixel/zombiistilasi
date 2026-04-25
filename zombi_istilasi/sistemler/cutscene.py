"""Hikaye cutscene ve anlatım katmanı — ARGUS Protokolü."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Generator
import pygame

from ayarlar import BEYAZ, SIYAH, KIRMIZI, GENISLIK, YUKSEKLIK, ALTIN, CAMGOBEGI


@dataclass(slots=True)
class CutsceneLine:
    """Tek satırlık cutscene girdisi."""
    speaker: str
    text: str


CHAPTER_DATA: dict[int, dict[str, object]] = {
    1: {
        "title": "BÖLÜM I — Karantina",
        "subtitle": "2031 · İstanbul · EDEN Virüsü Yayıldı",
        "lines": [
            CutsceneLine("Sistem", "Son iletişim: 14:32 — Bölge 7 karantinaya alındı."),
            CutsceneLine("Sistem", "Nüfusun %70'i 48 saat içinde 'Dönmüş' oldu."),
            CutsceneLine("Kerem", "EDEN virüsü... antidotun yarısı bendeydi."),
            CutsceneLine("Kerem", "Diğer yarı ARGUS yedek sunucusunda olmalı."),
            CutsceneLine("Kerem", "Sokaklar cehennem. Ama henüz bitmedi."),
            CutsceneLine("Kerem", "Hayatta kalacağım. Ve bu şehri geri alacağım."),
        ],
    },
    2: {
        "title": "BÖLÜM II — ARGUS Yeraltı",
        "subtitle": "Gerçekler, betonun altına gömüldü",
        "lines": [
            CutsceneLine("Kerem", "Yeraltı laboratuvarlarına iniyorum."),
            CutsceneLine("Radyo", "Direktör Selim Koç tüm iletişim hatlarına el koydu."),
            CutsceneLine("Kerem", "Bu bir kaza değilmiş. Planlanmış, kasıtlı bir salınım."),
            CutsceneLine("Selim Koç", "EDEN sadece bir başlangıç, Dr. Aydın."),
            CutsceneLine("Kerem", "Sunucu çekirdeği bende olana kadar durmak yok."),
            CutsceneLine("Kerem", "Selim seni durduracağım. Yemin ediyorum."),
        ],
    },
    3: {
        "title": "BÖLÜM III — Sıfır Noktası",
        "subtitle": "Son çatışma — Antidot ya da Yıkım",
        "lines": [
            CutsceneLine("Selim Koç", "Kaos yeni düzenin başlangıcıdır."),
            CutsceneLine("Selim Koç", "Zombi ordusu... mükemmel itaat eden bir güç."),
            CutsceneLine("Kerem", "İnsanlar araç değil, Selim."),
            CutsceneLine("Kerem", "Ben düzeni değil, insanları geri getireceğim."),
            CutsceneLine("Sistem", "ARGUS Reaktör Odası — son kilit açıldı."),
            CutsceneLine("Kerem", "Bu gece, İstanbul'un kaderi belli olacak."),
        ],
    },
}

ZAFER_MESAJLARI = [
    "Antidot tamamlandı. EDEN virüsü etkisizleştirildi.",
    "Selim Koç tutuklandı. ARGUS Protokolü iptal edildi.",
    "İstanbul yavaş yavaş kendine dönmeye başladı.",
    "Dr. Kerem Aydın... hayatta kaldı. Ve kazandı.",
]

DEVAM_MESAJLARI = [
    "Dr. Kerem Aydın düştü. Ama savaş devam ediyor.",
    "Formül tamamlanamadı. İstanbul hâlâ karanlıkta.",
    "ARGUS kazandı. Bu sefer.",
    "Belki bir sonraki denemede...",
]


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

        # Başlık çizgisi
        pygame.draw.line(screen, (180, 30, 30), (80, 80), (GENISLIK - 80, 80), 2)
        pygame.draw.line(screen, (180, 30, 30), (80, 175), (GENISLIK - 80, 175), 2)

        title = self.font_title.render(str(data["title"]), True, BEYAZ)
        sub = self.font_sub.render(str(data["subtitle"]), True, (160, 160, 200))
        screen.blit(title, (GENISLIK // 2 - title.get_width() // 2, 90))
        screen.blit(sub, (GENISLIK // 2 - sub.get_width() // 2, 145))

        progress = 1.0 - (self.timer / max(0.01, self.duration))
        start_y = int(YUKSEKLIK + 180 - progress * (YUKSEKLIK + 500))
        for i, line in enumerate(self._lines):
            if line.speaker == "Selim Koç":
                color = (255, 80, 80)
            elif line.speaker == "Kerem":
                color = (120, 200, 255)
            elif line.speaker == "Radyo":
                color = (120, 255, 160)
            else:
                color = (200, 200, 200)
            sp = self.font_sub.render(line.speaker + ":", True, color)
            tx = self.font_text.render(line.text, True, BEYAZ)
            screen.blit(sp, (100, start_y + i * 56))
            screen.blit(tx, (100, start_y + i * 56 + 22))

        tip = self.font_sub.render("SPACE: Atla", True, (180, 180, 180))
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
        self.timer = 3.5

    def update(self, dt: float) -> None:
        if self.timer > 0:
            self.timer -= dt

    def draw(self, screen: pygame.Surface) -> None:
        if self.timer <= 0:
            return
        alpha = min(255, int(255 * min(1.0, self.timer / 1.0)))
        bar = pygame.Surface((GENISLIK, 130), pygame.SRCALPHA)
        bar.fill((40, 0, 0, int(200)))
        screen.blit(bar, (0, YUKSEKLIK // 2 - 65))

        # Kenar çizgileri
        pygame.draw.line(screen, (200, 20, 20), (0, YUKSEKLIK // 2 - 65), (GENISLIK, YUKSEKLIK // 2 - 65), 2)
        pygame.draw.line(screen, (200, 20, 20), (0, YUKSEKLIK // 2 + 65), (GENISLIK, YUKSEKLIK // 2 + 65), 2)

        uyari_f = pygame.font.SysFont("Consolas", 16, bold=True)
        uyari = uyari_f.render("⚠ BOSS DALGASI ⚠", True, (255, 60, 60))
        uyari.set_alpha(alpha)
        screen.blit(uyari, (GENISLIK // 2 - uyari.get_width() // 2, YUKSEKLIK // 2 - 58))

        t = self.font_b.render(self.boss_name, True, (255, 150, 50))
        l = self.font_s.render(f'"{self.line}"', True, BEYAZ)
        t.set_alpha(alpha)
        l.set_alpha(alpha)
        screen.blit(t, (GENISLIK // 2 - t.get_width() // 2, YUKSEKLIK // 2 - 30))
        screen.blit(l, (GENISLIK // 2 - l.get_width() // 2, YUKSEKLIK // 2 + 22))


def chapter_from_wave(wave: int) -> int:
    """Dalga numarasına göre bölüm döndürür."""
    if wave >= 21:
        return 3
    if wave >= 11:
        return 2
    return 1


def iter_loading_notes() -> Generator[str, None, None]:
    """Shop geçişinde kullanılacak Kerem'in 25 notu."""
    notes = [
        "EDEN suşu sıcaklıkta kararlı, ama UV-C ışınımında kırılgan.",
        "Selim, klinik fazı beklemeden yayılım emri verdi. Bunun belgeleri elimde.",
        "Dönmüş bireylerde ağrı reseptörü ve prefrontal korteks kapanıyor.",
        "Antidotun ikinci yarısı muhtemelen şifreli bir sunucuda.",
        "Karantina kuleleri sinyal bozucu ile kilitlenmiş, ama tüneller açık.",
        "Zombi köpekler insanlara göre %300 daha hızlı. Dikkatli ol.",
        "Patlayan zombiler yaklaşınca 1.5 saniye uyarı veriyor — kaç.",
        "Kalkan enerjisi manyetik bir alan; EMP bozabilir.",
        "Selim'in yeraltı laboratuvarı koordinatları elimde var.",
        "ARGUS'ın 'insani' PR kampanyası EDEN'i gizlemek için yapıldı.",
        "Zırhlı zombiler saldırı yönünde %70 hasar azaltması gösteriyor.",
        "Sniper zombiler ses bozukluğuna göre hedef seçiyor.",
        "Sürü halindeki zombilerin hareket koordinasyonu bilinçli değil — kimyasal.",
        "Reaktör odasına yaklaşırken radyasyon maskesi şart. Şanslıyım ki yanımda var.",
        "Vampir zombi genomunun %4'ü hâlâ insan. Bu beni rahatsız ediyor.",
        "EDEN'in tam antidotu; iki parça protein inhibitöründen oluşuyor.",
        "Selim Koç 2029'da zaten bu planı hazırlamaya başlamıştı.",
        "Dönüştürücü zombiler revenantomu kullanıyor — bu doğaüstü değil, biyokimya.",
        "Buz silahları özellikle patlayan zombilere karşı işe yaramıyor.",
        "Her 20 atışta namlum mükemmel senkrona giriyor. Bunu bir şekilde kullan.",
        "Formülün eksik parçası: İnhibitör + Katalitik Ajan = Antidot.",
        "İstanbul nüfusu 15 milyondu. Şimdi kaçı kaldı, bilmiyorum.",
        "Adrenalin sistemi gerçek — stres altında insan kapasitesinin üstüne çıkılabilir.",
        "ARGUS'ın en büyük korkusu: antidotun halka açık olması.",
        "Bu bitmeyecek. Ama bugün, bu dalga, bu an — benim kontrolümde.",
    ]
    i = 0
    while True:
        yield notes[i % len(notes)]
        i += 1
