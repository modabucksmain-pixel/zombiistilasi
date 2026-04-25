# ============================================================
#  ekranlar/ana_menu.py — Ana Menü + Log Akışı + Meta Bilgi
# ============================================================
import pygame
import math
import random
from ayarlar import (
    GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, KIRMIZI,
    YESIL, ACIK_GRI, ARKAPLAN, DURUM_OYUN, ALTIN, CAMGOBEGI, MOR
)


LORE_LOGLARI = [
    "Son iletişim: 14:32 — Bölge 7 karantinaya alındı",
    "ARGUS İç Hat: EDEN suşu stabil değil",
    "Saha Raporu: Nüfusun %70'i 48 saatte Dönmüş",
    "Dr. Kerem Aydın: antidotun yarısı elimde",
    "Direktör Selim Koç tüm yayınları ele geçirdi",
    "Metro çıkışları kapatıldı — tahliye yok",
    "EDEN virüsü sıcakta bozuluyor, UV'ye dayanıklı",
    "Yeraltı laboratuvarı koordinatları doğrulandı",
    "ARGUS güvenlik droneleri kuzeye çekildi",
    "Reaktör soğutması arızalı — kritik saat sayıyor",
    "Dr. Aydın erişim yetkisi iptal edildi — tek çıkış yok",
    "Dönmüş bireylerde ağrı reseptörü kapanmış",
    "Sıfır Noktası koordinatı şifreli — sunucu gerekli",
    "Selim Koç: 'Kaos yeni düzenin başlangıcıdır'",
    "Kerem Aydın: 'Bu gece, İstanbul'un kaderi belli olacak'",
    "ARGUS Protokolü devrede — tüm kapılar kilitli",
    "Son dönmüş dalgası şehir merkezine ulaştı",
    "Radyo: Hayatta kalanlar metro çıkışında toplansın",
    "Biyometrik kilit kırılmaya çalışılıyor...",
    "ARGUS_CORE sunucusu — erişim: SINIFLANDIRMA-1",
]


class AnaMenu:
    def __init__(self):
        self.font_baslik = pygame.font.SysFont("Consolas", 58, bold=True)
        self.font_alt = pygame.font.SysFont("Consolas", 19)
        self.font_buton = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_lore = pygame.font.SysFont("Consolas", 14)
        self.font_kucuk = pygame.font.SysFont("Consolas", 15)
        self.zaman = 0.0
        self.log_ofset = [i * (GENISLIK // len(LORE_LOGLARI) + 300) for i in range(len(LORE_LOGLARI))]
        self.yildiz_pozlar = [(random.randint(0, GENISLIK), random.randint(0, YUKSEKLIK), random.uniform(0.3, 1.5)) for _ in range(120)]

        self.butonlar = [
            {"metin": "OYNA",  "durum": DURUM_OYUN, "renk": (60, 200, 80)},
            {"metin": "ÇIKIŞ", "durum": "cikis",    "renk": (180, 40, 40)},
        ]

    def guncelle(self, dt):
        self.zaman += dt

    def ciz(self, ekran):
        ekran.fill((8, 10, 15))
        self._ciz_yildizlar(ekran)
        self._ciz_arkaplan_detay(ekran)
        self._ciz_baslik(ekran)
        self._ciz_lore_panel(ekran)
        self._ciz_butonlar(ekran)
        self._ciz_lore_loglari(ekran)
        self._ciz_alt_bilgi(ekran)

    def _ciz_yildizlar(self, ekran):
        for sx, sy, parlaklik in self.yildiz_pozlar:
            a = int(80 + 80 * math.sin(self.zaman * parlaklik + sx * 0.01))
            c = (a, a, int(a * 1.1))
            pygame.draw.circle(ekran, c, (sx, sy), 1)

    def _ciz_arkaplan_detay(self, ekran):
        for i in range(0, GENISLIK + 80, 80):
            pygame.draw.line(ekran, (18, 28, 22), (i, 0), (i, YUKSEKLIK), 1)
        for j in range(0, YUKSEKLIK + 80, 80):
            pygame.draw.line(ekran, (18, 28, 22), (0, j), (GENISLIK, j), 1)

    def _ciz_baslik(self, ekran):
        sal = math.sin(self.zaman * 1.8) * 4

        # ARGUS / lore alt satır
        lore_f = self.font_kucuk.render("ARGUS Protokolü — 2031 İstanbul", True, (100, 160, 120))
        ekran.blit(lore_f, (GENISLIK // 2 - lore_f.get_width() // 2, 70))

        # Ana başlık
        golge = self.font_baslik.render("ZOMBİ İSTİLASI", True, (150, 0, 0))
        baslik = self.font_baslik.render("ZOMBİ İSTİLASI", True, BEYAZ)
        gx = GENISLIK // 2 - baslik.get_width() // 2
        gy = 100
        ekran.blit(golge, (gx + 4, gy + 4 + int(sal)))
        ekran.blit(baslik, (gx, gy + int(sal)))

        # İnce kırmızı çizgi
        pygame.draw.line(ekran, (180, 30, 30), (gx, gy + 72), (gx + baslik.get_width(), gy + 72), 2)

        alt = self.font_alt.render("Dr. Kerem Aydın'ın hikayesi • Dalgadan sonra dalga", True, (130, 180, 140))
        ekran.blit(alt, (GENISLIK // 2 - alt.get_width() // 2, gy + 82))

    def _ciz_lore_panel(self, ekran):
        """Sol panelde hikaye özeti."""
        panel = pygame.Surface((340, 180), pygame.SRCALPHA)
        pygame.draw.rect(panel, (8, 15, 20, 200), (0, 0, 340, 180), border_radius=12)
        pygame.draw.rect(panel, (50, 80, 60, 180), (0, 0, 340, 180), 1, border_radius=12)
        ekran.blit(panel, (40, 200))
        lines = [
            "📖 Dünya Durumu",
            "",
            "EDEN virüsü İstanbul'u aldı.",
            "Nüfusun %70'i Dönmüş.",
            "Antidot — iki parça, iki konum.",
            "Sen Dr. Kerem Aydın'sın.",
            "Hayatta kal. Şehri kurtar.",
        ]
        for i, line in enumerate(lines):
            c = CAMGOBEGI if i == 0 else (170, 210, 180)
            t = self.font_lore.render(line, True, c)
            ekran.blit(t, (56, 214 + i * 22))

    def _ciz_butonlar(self, ekran):
        fare = pygame.mouse.get_pos()
        for i, b in enumerate(self.butonlar):
            bx = GENISLIK // 2 - 160
            by = 240 + i * 90
            bw, bh = 320, 62

            uzerinde = pygame.Rect(bx, by, bw, bh).collidepoint(fare)
            renk = b["renk"]
            if uzerinde:
                renk = tuple(min(255, c + 50) for c in renk)

            # Gölge
            pygame.draw.rect(ekran, (0, 0, 0), (bx + 5, by + 5, bw, bh), border_radius=14)
            pygame.draw.rect(ekran, renk, (bx, by, bw, bh), border_radius=14)
            pygame.draw.rect(ekran, BEYAZ, (bx, by, bw, bh), 2, border_radius=14)

            metin = self.font_buton.render(b["metin"], True, SIYAH if i == 0 else BEYAZ)
            ekran.blit(metin, (bx + bw // 2 - metin.get_width() // 2,
                                by + bh // 2 - metin.get_height() // 2))

    def _ciz_lore_loglari(self, ekran):
        """Alt kısımda akan lore log satırları."""
        for i, log in enumerate(LORE_LOGLARI):
            x = int(GENISLIK - ((self.zaman * 65 + i * 340) % (GENISLIK + 1200)))
            alpha = max(0, min(200, int(200 * (x / GENISLIK))))
            surf = self.font_lore.render(f"● {log}", True, (90, 150, 110))
            surf.set_alpha(alpha)
            ekran.blit(surf, (x, YUKSEKLIK - 120 + (i % 3) * 18))

    def _ciz_alt_bilgi(self, ekran):
        ipucu = self.font_kucuk.render(
            "WASD: Hareket  |  Sol Tık: Ateş  |  Sağ Tık: Nişan  |  SHIFT: Sprint  |  SPACE: Ultimate  |  B: Shop",
            True, (80, 120, 90)
        )
        ekran.blit(ipucu, (GENISLIK // 2 - ipucu.get_width() // 2, YUKSEKLIK - 36))

        versiyon = self.font_kucuk.render("v3.0 — ARGUS Protokolü  |  © 2031 Kerem Aydın", True, (60, 80, 60))
        ekran.blit(versiyon, (GENISLIK // 2 - versiyon.get_width() // 2, YUKSEKLIK - 18))

    def tik_isle(self, event, yuksek_skor):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fare = pygame.mouse.get_pos()
            for i, b in enumerate(self.butonlar):
                bx = GENISLIK // 2 - 160
                by = 240 + i * 90
                if pygame.Rect(bx, by, 320, 62).collidepoint(fare):
                    return b["durum"]
        return None
