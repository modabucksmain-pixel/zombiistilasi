import math
import random
import pygame
from ayarlar import GENISLIK, YUKSEKLIK


class HaritaSistemi:
    """Arena düzeni, çarpışma ve mini hikaye görevlerini yönetir."""

    def __init__(self):
        self.haritalar = self._haritalari_hazirla()
        self.aktif_harita_index = 0
        self.aktif_harita = self.haritalar[0]
        self._hikaye_reset()

    def _haritalari_hazirla(self):
        return [
            {
                "isim": "Karantina Mahallesi",
                "zemin": (14, 16, 21),
                "cizgi": (24, 28, 35),
                "karo": 72,
                "engeller": [
                    pygame.Rect(230, 180, 240, 90),
                    pygame.Rect(730, 150, 180, 120),
                    pygame.Rect(440, 420, 320, 85),
                    pygame.Rect(1120, 280, 240, 110),
                    pygame.Rect(900, 640, 230, 90),
                ],
                "isiklar": [(350, 230, (255, 150, 120)), (1200, 340, (255, 220, 120))],
                "landmarks": [
                    (300, 220, "Kule", (255, 180, 120)),
                    (980, 690, "Sığınak", (100, 220, 255)),
                ],
                "hikaye": {
                    "baslik": "BÖLGE-7: Son Sinyal",
                    "hedefler": [
                        {"tip": "nokta", "aciklama": "Sinyal kulesine ulaş", "konum": (300, 220), "yaricap": 80},
                        {"tip": "dalga", "aciklama": "Jeneratör online olana kadar DALGA 3'e dayan", "dalga": 3},
                        {"tip": "nokta", "aciklama": "Tahliye noktasına git", "konum": (980, 690), "yaricap": 90},
                    ],
                },
            },
            {
                "isim": "Yeraltı Laboratuvarı",
                "zemin": (12, 24, 24),
                "cizgi": (35, 62, 62),
                "karo": 68,
                "engeller": [
                    pygame.Rect(180, 260, 310, 95),
                    pygame.Rect(620, 220, 130, 310),
                    pygame.Rect(860, 150, 270, 95),
                    pygame.Rect(1050, 470, 280, 110),
                    pygame.Rect(370, 620, 340, 95),
                ],
                "isiklar": [(250, 300, (120, 255, 220)), (1120, 520, (180, 255, 180))],
                "landmarks": [
                    (250, 300, "Kontrol", (120, 255, 220)),
                    (1220, 520, "Asansör", (220, 255, 220)),
                ],
                "hikaye": {
                    "baslik": "ARGUS LAB: Kırılma Noktası",
                    "hedefler": [
                        {"tip": "nokta", "aciklama": "Kontrol terminaline eriş", "konum": (250, 300), "yaricap": 85},
                        {"tip": "dalga", "aciklama": "Veri transferi için DALGA 4'e kadar hayatta kal", "dalga": 4},
                        {"tip": "nokta", "aciklama": "Asansöre ulaşıp tahliye başlat", "konum": (1220, 520), "yaricap": 95},
                    ],
                },
            },
            {
                "isim": "Alevli Otoyol",
                "zemin": (20, 14, 12),
                "cizgi": (65, 48, 40),
                "karo": 78,
                "engeller": [
                    pygame.Rect(250, 180, 370, 85),
                    pygame.Rect(770, 220, 210, 340),
                    pygame.Rect(1100, 160, 220, 95),
                    pygame.Rect(350, 520, 240, 140),
                    pygame.Rect(980, 620, 270, 95),
                ],
                "isiklar": [(420, 210, (255, 130, 80)), (1080, 670, (255, 160, 80))],
                "landmarks": [
                    (420, 210, "Yakıt", (255, 140, 100)),
                    (1080, 670, "Köprü", (255, 170, 120)),
                ],
                "hikaye": {
                    "baslik": "KORİDOR-9: Kızıl Kaçış",
                    "hedefler": [
                        {"tip": "nokta", "aciklama": "Yakıt deposunu emniyete al", "konum": (420, 210), "yaricap": 85},
                        {"tip": "dalga", "aciklama": "Konvoy hazırlanırken DALGA 3'e kadar savun", "dalga": 3},
                        {"tip": "nokta", "aciklama": "Köprüye var ve konvoyu başlat", "konum": (1080, 670), "yaricap": 95},
                    ],
                },
            },
        ]

    def harita_degistir(self):
        self.aktif_harita_index = (self.aktif_harita_index + 1) % len(self.haritalar)
        self.aktif_harita = self.haritalar[self.aktif_harita_index]
        self._hikaye_reset()

    def _hikaye_reset(self):
        self.hikaye_asama = 0
        self.hikaye_tamamlandi = False
        self.hikaye_mesaj = ""

    @property
    def aktif_hikaye_baslik(self):
        return self.aktif_harita["hikaye"]["baslik"]

    @property
    def aktif_gorev(self):
        hedefler = self.aktif_harita["hikaye"]["hedefler"]
        if self.hikaye_asama >= len(hedefler):
            return "Görev tamamlandı: tahliye bekleniyor"
        return hedefler[self.hikaye_asama]["aciklama"]

    def hikaye_guncelle(self, oyuncu, dalga_no):
        if self.hikaye_tamamlandi:
            return None

        hedefler = self.aktif_harita["hikaye"]["hedefler"]
        if self.hikaye_asama >= len(hedefler):
            self.hikaye_tamamlandi = True
            return None

        hedef = hedefler[self.hikaye_asama]
        tamam = False
        if hedef["tip"] == "nokta":
            hx, hy = hedef["konum"]
            tamam = math.hypot(hx - oyuncu.x, hy - oyuncu.y) <= hedef["yaricap"]
        elif hedef["tip"] == "dalga":
            tamam = dalga_no >= hedef["dalga"]

        if tamam:
            mesaj = f"✓ Görev: {hedef['aciklama']}"
            self.hikaye_asama += 1
            if self.hikaye_asama >= len(hedefler):
                self.hikaye_tamamlandi = True
                return mesaj + " | Hikaye tamamlandı!"
            return mesaj
        return None

    def nokta_duvar_icinde(self, x, y, yaricap=0):
        for r in self.aktif_harita["engeller"]:
            if (
                x + yaricap > r.left
                and x - yaricap < r.right
                and y + yaricap > r.top
                and y - yaricap < r.bottom
            ):
                return True
        return False

    def hareketi_sinirla(self, eski_x, eski_y, yeni_x, yeni_y, yaricap):
        sinir_x = max(yaricap, min(GENISLIK - yaricap, yeni_x))
        sinir_y = max(yaricap, min(YUKSEKLIK - yaricap, yeni_y))

        if not self.nokta_duvar_icinde(sinir_x, sinir_y, yaricap):
            return sinir_x, sinir_y

        # Eksen bazlı çözüm: daha doğal kayma efekti
        only_x_ok = not self.nokta_duvar_icinde(sinir_x, eski_y, yaricap)
        only_y_ok = not self.nokta_duvar_icinde(eski_x, sinir_y, yaricap)
        if only_x_ok:
            return sinir_x, eski_y
        if only_y_ok:
            return eski_x, sinir_y
        return eski_x, eski_y

    def rastgele_guvenli_nokta(self, yaricap=24, deneme=40):
        for _ in range(deneme):
            x = random.randint(yaricap, GENISLIK - yaricap)
            y = random.randint(yaricap, YUKSEKLIK - yaricap)
            if not self.nokta_duvar_icinde(x, y, yaricap):
                return x, y
        return GENISLIK // 2, YUKSEKLIK // 2
