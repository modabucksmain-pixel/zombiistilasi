# ============================================================
#  ekranlar/ayarlar_menusu.py — Ayarlar Menüsü
#  Ses, fare, grafik, tam ekran — JSON'a kayıt
# ============================================================
"""Ayarlar menüsü: ses seviyesi, güçlük, grafik kalitesi, tam ekran."""
from __future__ import annotations
import json
import os
import pygame
from ayarlar import GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, KIRMIZI, YESIL, ALTIN, CAMGOBEGI, MOR, PROJE_DIZIN


AYARLAR_DOSYASI = os.path.join(PROJE_DIZIN, "kayitlar", "ayarlar.json")

VARSAYILAN_AYARLAR: dict[str, object] = {
    "ses_seviyesi": 0.7,
    "muzik_seviyesi": 0.5,
    "tam_ekran": False,
    "zorluk": "normal",
    "parcacik_kalite": "yuksek",
    "sarsinti_acik": True,
    "dil": "TR",
}


def ayarlari_yukle() -> dict:
    try:
        if os.path.exists(AYARLAR_DOSYASI):
            with open(AYARLAR_DOSYASI, "r", encoding="utf-8") as f:
                kayit = json.load(f)
                veri = VARSAYILAN_AYARLAR.copy()
                veri.update(kayit)
                return veri
    except Exception:
        pass
    return VARSAYILAN_AYARLAR.copy()


def ayarlari_kaydet(ayarlar: dict) -> None:
    try:
        os.makedirs(os.path.dirname(AYARLAR_DOSYASI), exist_ok=True)
        with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(ayarlar, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class AyarlarMenusu:
    """Ayarlar menüsü ekranı."""

    ZORLUKLAR = ["kolay", "normal", "zor", "argus"]
    KALITELER = ["dusuk", "normal", "yuksek", "ultra"]

    def __init__(self) -> None:
        self.font_baslik = pygame.font.SysFont("Consolas", 38, bold=True)
        self.font_etiket = pygame.font.SysFont("Consolas", 20, bold=True)
        self.font_deger = pygame.font.SysFont("Consolas", 18)
        self.font_kucuk = pygame.font.SysFont("Consolas", 14)
        self.ayarlar = ayarlari_yukle()
        self.zaman = 0.0
        self.mesaj = ""
        self.mesaj_sayac = 0.0
        self._suruklenen: str | None = None

    def guncelle(self, dt: float) -> None:
        self.zaman += dt
        if self.mesaj_sayac > 0:
            self.mesaj_sayac -= dt

    def ciz(self, ekran: pygame.Surface) -> None:
        ekran.fill((8, 10, 16))

        # Arka plan
        for i in range(0, GENISLIK, 70):
            pygame.draw.line(ekran, (15, 18, 28), (i, 0), (i, YUKSEKLIK), 1)
        for j in range(0, YUKSEKLIK, 70):
            pygame.draw.line(ekran, (15, 18, 28), (0, j), (GENISLIK, j), 1)

        # Başlık
        pygame.draw.rect(ekran, (10, 14, 22), (0, 0, GENISLIK, 80))
        pygame.draw.line(ekran, CAMGOBEGI, (0, 80), (GENISLIK, 80), 2)
        t = self.font_baslik.render("⚙ AYARLAR", True, BEYAZ)
        ekran.blit(t, (50, 22))
        geri = self.font_deger.render("ESC: Geri  |  ENTER: Kaydet", True, (120, 140, 160))
        ekran.blit(geri, (GENISLIK - geri.get_width() - 30, 32))

        # Panel
        panel = pygame.Surface((900, 480), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 15, 22, 220), (0, 0, 900, 480), border_radius=16)
        pygame.draw.rect(panel, (50, 70, 100, 180), (0, 0, 900, 480), 2, border_radius=16)
        px, py = GENISLIK // 2 - 450, 110
        ekran.blit(panel, (px, py))

        satirlar = [
            ("ses_seviyesi",    "Efekt Ses Seviyesi", "slider"),
            ("muzik_seviyesi",  "Müzik Seviyesi", "slider"),
            ("zorluk",          "Zorluk", "secim"),
            ("parcacik_kalite", "Grafik Kalitesi", "secim2"),
            ("tam_ekran",       "Tam Ekran", "toggle"),
            ("sarsinti_acik",   "Kamera Sarsıntısı", "toggle"),
        ]

        for i, (anahtar, etiket, tip) in enumerate(satirlar):
            ry = py + 30 + i * 72

            et = self.font_etiket.render(etiket, True, (180, 200, 220))
            ekran.blit(et, (px + 40, ry))

            if tip == "slider":
                self._ciz_slider(ekran, px + 400, ry, anahtar)
            elif tip == "secim":
                self._ciz_secim(ekran, px + 400, ry, anahtar, self.ZORLUKLAR)
            elif tip == "secim2":
                self._ciz_secim(ekran, px + 400, ry, anahtar, self.KALITELER)
            elif tip == "toggle":
                self._ciz_toggle(ekran, px + 400, ry, anahtar)

        # Zorluk açıklaması
        zorluk_aciklamalari = {
            "kolay": "Zombiler %70 can, siz %130 hasar. Öğrenmek için ideal.",
            "normal": "Standart denge. Önerilen mod.",
            "zor": "Zombiler %130 can, hasar %80.",
            "argus": "ARGUS MODU: Zombiler 2x can, siz %50 hasar. ÇOK ZOR.",
        }
        zorluk_rengi = {"kolay": YESIL, "normal": CAMGOBEGI, "zor": ALTIN, "argus": KIRMIZI}
        z = str(self.ayarlar.get("zorluk", "normal"))
        ac = self.font_kucuk.render(zorluk_aciklamalari.get(z, ""), True, zorluk_rengi.get(z, BEYAZ))
        ekran.blit(ac, (px + 40, py + 260))

        # Kaydet butonu
        bx, by = GENISLIK // 2 - 150, YUKSEKLIK - 100
        fare = pygame.mouse.get_pos()
        renk = (60, 200, 80) if pygame.Rect(bx, by, 300, 55).collidepoint(fare) else (40, 160, 60)
        pygame.draw.rect(ekran, renk, (bx, by, 300, 55), border_radius=12)
        pygame.draw.rect(ekran, BEYAZ, (bx, by, 300, 55), 2, border_radius=12)
        bt = self.font_etiket.render("KAYDET VE KAPAT", True, SIYAH)
        ekran.blit(bt, (bx + 150 - bt.get_width() // 2, by + 27 - bt.get_height() // 2))

        if self.mesaj_sayac > 0:
            mt = self.font_deger.render(self.mesaj, True, YESIL)
            ekran.blit(mt, (GENISLIK // 2 - mt.get_width() // 2, YUKSEKLIK - 40))

    def _ciz_slider(self, ekran: pygame.Surface, x: int, y: int, anahtar: str) -> None:
        deger = float(self.ayarlar.get(anahtar, 0.5))
        genis = 300
        dolu = int(genis * deger)

        pygame.draw.rect(ekran, (40, 45, 55), (x, y + 8, genis, 16), border_radius=8)
        pygame.draw.rect(ekran, CAMGOBEGI, (x, y + 8, dolu, 16), border_radius=8)
        pygame.draw.circle(ekran, BEYAZ, (x + dolu, y + 16), 10)

        yt = self.font_deger.render(f"%{int(deger * 100)}", True, (200, 200, 200))
        ekran.blit(yt, (x + genis + 12, y + 4))

    def _ciz_secim(self, ekran: pygame.Surface, x: int, y: int, anahtar: str, secenekler: list[str]) -> None:
        mevcut = str(self.ayarlar.get(anahtar, secenekler[0]))
        for i, s in enumerate(secenekler):
            bx = x + i * 120
            aktif = s == mevcut
            renk = CAMGOBEGI if aktif else (50, 60, 70)
            pygame.draw.rect(ekran, renk, (bx, y, 110, 36), border_radius=8)
            pygame.draw.rect(ekran, (80, 100, 120), (bx, y, 110, 36), 1, border_radius=8)
            st = self.font_deger.render(s.upper(), True, BEYAZ if aktif else (150, 160, 170))
            ekran.blit(st, (bx + 55 - st.get_width() // 2, y + 18 - st.get_height() // 2))

    def _ciz_toggle(self, ekran: pygame.Surface, x: int, y: int, anahtar: str) -> None:
        aktif = bool(self.ayarlar.get(anahtar, False))
        renk = YESIL if aktif else KIRMIZI
        pygame.draw.rect(ekran, renk, (x, y, 80, 36), border_radius=18)
        top_x = x + 50 if aktif else x + 6
        pygame.draw.circle(ekran, BEYAZ, (top_x + 12, y + 18), 13)
        metin = self.font_deger.render("AÇIK" if aktif else "KAPALI", True, BEYAZ)
        ekran.blit(metin, (x + 92, y + 10))

    def tik_isle(self, event: pygame.event.Event, pencere: pygame.Surface | None = None) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "geri"
            if event.key == pygame.K_RETURN:
                ayarlari_kaydet(self.ayarlar)
                self.mesaj = "✓ Ayarlar kaydedildi!"
                self.mesaj_sayac = 2.0

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fare_x, fare_y = pygame.mouse.get_pos()
            px, py = GENISLIK // 2 - 450, 110

            # Slider tıklama
            for i, (anahtar, _, tip) in enumerate([
                ("ses_seviyesi", "", "slider"),
                ("muzik_seviyesi", "", "slider"),
            ]):
                ry = py + 30 + i * 72
                sx = px + 400
                if tip == "slider" and pygame.Rect(sx, ry + 4, 300, 24).collidepoint(fare_x, fare_y):
                    self.ayarlar[anahtar] = max(0.0, min(1.0, (fare_x - sx) / 300))

            # Toggle tıklama
            for i, (anahtar, _, tip) in enumerate([
                ("ses_seviyesi", "", "slider"),
                ("muzik_seviyesi", "", "slider"),
                ("zorluk", "", "secim"),
                ("parcacik_kalite", "", "secim2"),
                ("tam_ekran", "", "toggle"),
                ("sarsinti_acik", "", "toggle"),
            ]):
                ry = py + 30 + i * 72
                tx = px + 400
                if tip == "toggle" and pygame.Rect(tx, ry, 80, 36).collidepoint(fare_x, fare_y):
                    self.ayarlar[anahtar] = not bool(self.ayarlar.get(anahtar, False))

                elif tip == "secim":
                    seçenekler = self.ZORLUKLAR
                    for j, s in enumerate(seçenekler):
                        bx = tx + j * 120
                        if pygame.Rect(bx, ry, 110, 36).collidepoint(fare_x, fare_y):
                            self.ayarlar[anahtar] = s

                elif tip == "secim2":
                    seçenekler = self.KALITELER
                    for j, s in enumerate(seçenekler):
                        bx = tx + j * 120
                        if pygame.Rect(bx, ry, 110, 36).collidepoint(fare_x, fare_y):
                            self.ayarlar[anahtar] = s

            # Kaydet butonu
            if pygame.Rect(GENISLIK // 2 - 150, YUKSEKLIK - 100, 300, 55).collidepoint(fare_x, fare_y):
                ayarlari_kaydet(self.ayarlar)
                self.mesaj = "✓ Kaydedildi!"
                self.mesaj_sayac = 2.0
                return "geri"

        return None
