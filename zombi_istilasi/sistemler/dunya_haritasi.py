# ============================================================
#  sistemler/dunya_haritasi.py — Büyük Dünya Haritası
#  12000x8000 piksel, 4 bölge, kapılar, güvenli alanlar
# ============================================================
import math
import random
import pygame
from ayarlar import GENISLIK, YUKSEKLIK
from varliklar.npc import NPC

DUNYA_W = 12000
DUNYA_H = 8000


def _engel_listesi(rects_data):
    return [pygame.Rect(*r) for r in rects_data]


# ── Bölge Tanımları ──────────────────────────────────────────
BOLGELER = {
    "karantina": {
        "isim": "Karantina Mahallesi",
        "sinirlar": pygame.Rect(0, 0, 4000, 3500),
        "zemin": (14, 16, 21),
        "cizgi": (24, 28, 35),
        "karo": 72,
        "kilit": None,
        "tehlike": 1,
        "guvenli": False,
        "engeller": _engel_listesi([
            (300, 200, 280, 100), (800, 150, 200, 130), (500, 500, 350, 90),
            (1200, 300, 260, 120), (1000, 700, 250, 100), (200, 1000, 300, 80),
            (1500, 200, 180, 200), (700, 1200, 220, 90), (1800, 500, 200, 150),
            (400, 1600, 280, 100), (1100, 1500, 200, 120), (1600, 1000, 240, 80),
            (300, 2200, 250, 110), (900, 2000, 180, 140), (1500, 1800, 300, 90),
            (2000, 400, 200, 160), (2200, 900, 180, 120), (2500, 200, 260, 100),
            (2800, 600, 220, 90), (2400, 1300, 200, 130), (2000, 1700, 280, 100),
            (2600, 1600, 200, 110), (3000, 300, 180, 150), (3200, 800, 240, 100),
            (3000, 1400, 200, 120), (3400, 500, 180, 90), (3500, 1100, 220, 100),
            (2800, 2200, 260, 80), (3200, 2000, 200, 130), (3600, 1800, 180, 100),
        ]),
        "isiklar": [
            (400, 250, (255, 150, 120)), (1300, 350, (255, 220, 120)),
            (2100, 500, (255, 180, 100)), (3100, 400, (200, 180, 255)),
            (800, 1800, (255, 200, 150)), (2500, 1500, (180, 255, 200)),
        ],
        "landmarks": [
            (350, 240, "Gözetleme Kulesi", (255, 180, 120)),
            (1050, 750, "Sığınak Alpha", (100, 220, 255)),
            (2300, 1000, "Yıkık Hastane", (255, 100, 100)),
            (3300, 600, "Terk Edilmiş Okul", (200, 200, 150)),
            (1800, 2200, "Barikat Noktası", (255, 200, 80)),
        ],
        "gunluk_noktalari": [
            ((250, 130), "Kayıt-01: EDEN suşu bugün insan testine geçti."),
            ((500, 350), "Kayıt-02: Bölge 7 kapatıldı, ama geç kaldık."),
            ((800, 600), "Kayıt-03: Dönüşüm ölüm değil; nörolojik çöküş."),
            ((1400, 400), "Kayıt-04: Selim protokolü zorla onayladı."),
            ((2600, 800), "Kayıt-05: Kaçış tüneli bir saat içinde çökecek."),
        ],
        "terminaller": [
            {"id": "k1", "pos": (380, 250), "lines": [
                "ARGUS İç Yazışma — EDEN Serisi / Gizli",
                "Saha yayılımı planlandığı gibi.",
                "Halk panikteyken sözleşme imzaları hızlanıyor.",
                "Direktör S.K. onayı: EVET.",
            ]},
            {"id": "k2", "pos": (2350, 1050), "lines": [
                "Hastane Acil Servisi — Son Kayıt",
                "Hasta sayısı kontrol dışı.",
                "Personelin %40'ı dönüştü.",
                "Tahliye emri verildi ama çok geç.",
            ]},
            {"id": "k3", "pos": (3350, 650), "lines": [
                "Okul Müdürü Notu",
                "Çocukları bodruma sakladık.",
                "Dışarıdan gelen sesler durmuyor.",
                "ARGUS yardım göndereceğini söyledi. Yalan.",
            ]},
        ],
        "npcs_veri": [
            (1050, 700, "sivil", "lore"),
            (2300, 950, "saglikci", "lore"),
            (3300, 550, "muhendis", "lore"),
        ],
        "boss_noktasi": (2000, 1200, "et_gobegi"),
        "spawn_tipler": ["normal", "hizli", "kopek"],
    },

    "merkez": {
        "isim": "Merkez Meydan",
        "sinirlar": pygame.Rect(4200, 2500, 2000, 1500),
        "zemin": (18, 22, 28),
        "cizgi": (30, 38, 48),
        "karo": 64,
        "kilit": None,
        "tehlike": 0,
        "guvenli": True,
        "engeller": _engel_listesi([
            (4400, 2700, 200, 100), (4800, 2800, 150, 80),
            (5200, 2700, 180, 120), (5600, 2900, 200, 80),
            (4600, 3200, 250, 90), (5000, 3400, 200, 100),
            (5400, 3200, 180, 110), (4400, 3600, 220, 80),
        ]),
        "isiklar": [
            (5200, 3100, (100, 200, 255)), (4600, 3300, (200, 255, 200)),
            (5500, 3500, (255, 220, 150)),
        ],
        "landmarks": [
            (5200, 3100, "Komuta Merkezi", (100, 200, 255)),
            (4600, 3300, "Sığınak Girişi", (200, 255, 200)),
            (5500, 3500, "İkmal Deposu", (255, 220, 150)),
        ],
        "gunluk_noktalari": [],
        "terminaller": [],
        "npcs_veri": [
            (5200, 3050, "saglikci", "gorev"),    # Dr. Elif
            (4600, 3250, "muhendis", "gorev"),     # Mühendis Arda
            (5500, 3450, "sivil", "satici"),        # Karaborsacı Hakan
            (5000, 3100, "sivil", "gorev"),         # Komutan Deniz
        ],
        "boss_noktasi": None,
        "spawn_tipler": [],
    },

    "yeralti": {
        "isim": "Yeraltı Laboratuvarı",
        "sinirlar": pygame.Rect(2500, 4500, 3500, 3000),
        "zemin": (12, 24, 24),
        "cizgi": (35, 62, 62),
        "karo": 68,
        "kilit": "karantina_boss",
        "tehlike": 2,
        "guvenli": False,
        "engeller": _engel_listesi([
            (2700, 4700, 320, 100), (3100, 4800, 140, 320),
            (3400, 4650, 280, 100), (3800, 4900, 200, 250),
            (2800, 5200, 250, 90), (3300, 5300, 180, 200),
            (3700, 5100, 220, 120), (4100, 4700, 260, 100),
            (4400, 5000, 200, 180), (4800, 4800, 180, 120),
            (2700, 5700, 300, 80), (3200, 5800, 200, 150),
            (3600, 5600, 250, 100), (4000, 5500, 180, 200),
            (4500, 5400, 220, 120), (5000, 5000, 200, 160),
            (2800, 6200, 260, 100), (3300, 6400, 180, 120),
            (3800, 6100, 240, 90), (4200, 6300, 200, 130),
            (4700, 5900, 180, 150), (5100, 5600, 220, 100),
            (5300, 6200, 200, 110), (5500, 5200, 180, 140),
            (2900, 6800, 240, 100), (3500, 7000, 200, 120),
            (4000, 6800, 180, 100), (4600, 6600, 220, 90),
            (5000, 7000, 200, 130), (5400, 6700, 180, 100),
        ]),
        "isiklar": [
            (3000, 5000, (120, 255, 220)), (4500, 5500, (180, 255, 180)),
            (3500, 6500, (100, 255, 200)), (5200, 5800, (150, 200, 255)),
        ],
        "landmarks": [
            (3000, 5000, "Kontrol Terminali", (120, 255, 220)),
            (4500, 5500, "Asansör Şaftı", (220, 255, 220)),
            (5200, 5800, "Reaktör Odası", (255, 150, 100)),
            (3500, 6500, "Güvenli Oda", (100, 255, 150)),
        ],
        "gunluk_noktalari": [
            ((2800, 4800), "Kayıt-06: Server farm soğutması arızalı."),
            ((3400, 5400), "Kayıt-07: Selim, EDEN'i askeri lisansa açtı."),
            ((4200, 5100), "Kayıt-08: Antidot 2/2 dosyası 'ARGUS_CORE'."),
            ((4800, 5800), "Kayıt-09: Personel tahliyesi bilinçli geciktirildi."),
            ((5300, 6400), "Kayıt-10: Şehrin %70'i 48 saatte dönüştü."),
        ],
        "terminaller": [
            {"id": "l1", "pos": (4550, 5550), "lines": [
                "ARGUS İç Yazışma — Yedek Sunucu",
                "Kilidi sadece yönetici biyometrisiyle açılır.",
                "Dr. Kerem Aydın erişim listesinde pasife alındı.",
                "Operasyon adı: ARGUS Protokolü",
            ]},
            {"id": "l2", "pos": (5250, 5850), "lines": [
                "Reaktör Odası — Uyarı",
                "Radyasyon seviyesi kritik.",
                "Soğutma sistemi devre dışı.",
                "Acil tahliye protokolü: BAŞARISIZ.",
            ]},
        ],
        "npcs_veri": [
            (3500, 6450, "saglikci", "satici"),  # Lab teknisyeni
            (3000, 4950, "muhendis", "lore"),
            (4800, 5200, "sivil", "lore"),
        ],
        "boss_noktasi": (4000, 6000, "zehir_usta"),
        "spawn_tipler": ["normal", "zehirli", "zirhli", "elektrik", "sniper_zombi"],
    },

    "otoyol": {
        "isim": "Alevli Otoyol",
        "sinirlar": pygame.Rect(6500, 4000, 4500, 2500),
        "zemin": (20, 14, 12),
        "cizgi": (65, 48, 40),
        "karo": 78,
        "kilit": "yeralti_boss",
        "tehlike": 3,
        "guvenli": False,
        "engeller": _engel_listesi([
            (6700, 4200, 380, 90), (7200, 4300, 220, 350),
            (7700, 4200, 230, 100), (8100, 4400, 280, 120),
            (8600, 4200, 200, 160), (9000, 4500, 250, 100),
            (6800, 4800, 300, 80), (7400, 4900, 200, 200),
            (7900, 4700, 250, 120), (8400, 4800, 180, 150),
            (8900, 4700, 220, 100), (9400, 4400, 200, 180),
            (6900, 5300, 280, 100), (7300, 5500, 200, 120),
            (7800, 5200, 250, 90), (8300, 5400, 180, 140),
            (8700, 5100, 220, 110), (9200, 5300, 200, 100),
            (9600, 4800, 240, 120), (10000, 4500, 200, 160),
            (10200, 5000, 180, 130), (10500, 4300, 220, 100),
            (6800, 5800, 260, 80), (7500, 5900, 200, 120),
            (8200, 5800, 180, 100), (8800, 6000, 220, 90),
            (9400, 5800, 200, 130), (10000, 5600, 180, 100),
            (10400, 5400, 200, 120), (10700, 5000, 180, 150),
        ]),
        "isiklar": [
            (7000, 4300, (255, 130, 80)), (8500, 4600, (255, 160, 80)),
            (9500, 5000, (255, 100, 50)), (10300, 4800, (255, 180, 100)),
        ],
        "landmarks": [
            (7000, 4300, "Yakıt Deposu", (255, 140, 100)),
            (8500, 4600, "Devrilmiş Tanker", (255, 200, 80)),
            (9500, 5000, "Köprü Girişi", (255, 170, 120)),
            (10500, 5200, "Sıfır Noktası", (255, 50, 50)),
        ],
        "gunluk_noktalari": [
            ((6800, 4400), "Kayıt-11: Otoyol tahliyesi başarısız."),
            ((7500, 4600), "Kayıt-12: EDEN ateşle tamamen yok olmuyor."),
            ((8500, 5000), "Kayıt-13: Dönmüş sürüler sesle yönleniyor."),
            ((9500, 5300), "Kayıt-14: Selim şehir merkezinde son fazı bekliyor."),
            ((10500, 5400), "Kayıt-15: Sıfır Noktası koordinatı: burası."),
        ],
        "terminaller": [
            {"id": "h1", "pos": (9550, 5050), "lines": [
                "ARGUS Acil Kanal",
                "Sıfır Noktası reaktör kapısı kilitsiz.",
                "Direktör sahaya iniyor.",
                "Bütün droneler çekilsin. İmza: S.K.",
            ]},
        ],
        "npcs_veri": [
            (7000, 4250, "sivil", "lore"),
            (8500, 4550, "saglikci", "lore"),
            (10500, 5150, "muhendis", "lore"),
        ],
        "boss_noktasi": (9500, 5200, "alev_kral"),
        "spawn_tipler": ["normal", "hizli", "kosucu", "patlayan", "vampir", "donusturucu"],
    },
}

# ── Bölgeler arası geçitler ──────────────────────────────────
GECITLER = [
    {
        "id": "karantina_merkez",
        "baslangic": "karantina",
        "bitis": "merkez",
        "kapi_rect": pygame.Rect(3800, 2800, 400, 200),
        "kilit": None,
    },
    {
        "id": "merkez_yeralti",
        "baslangic": "merkez",
        "bitis": "yeralti",
        "kapi_rect": pygame.Rect(4200, 4000, 300, 500),
        "kilit": "karantina_boss",
    },
    {
        "id": "merkez_otoyol",
        "baslangic": "merkez",
        "bitis": "otoyol",
        "kapi_rect": pygame.Rect(6200, 3500, 300, 500),
        "kilit": "yeralti_boss",
    },
]

# ── Güvenli Bölge Tanımları ──────────────────────────────────
GUVENLI_BOLGELER = [
    {"isim": "Merkez Meydan", "rect": pygame.Rect(4200, 2500, 2000, 1500), "tip": "tam_shop"},
    {"isim": "Karantina Sığınağı", "rect": pygame.Rect(950, 600, 300, 250), "tip": "mini_shop"},
    {"isim": "Yeraltı Güvenli Oda", "rect": pygame.Rect(3400, 6350, 300, 250), "tip": "element_shop"},
]


class DunyaHaritasi:
    """Büyük dünya haritası yöneticisi."""

    def __init__(self):
        self.bolgeler = BOLGELER
        self.gecitler = GECITLER
        self.guvenli_bolgeler = GUVENLI_BOLGELER
        self.acilan_kayitlar: list[str] = []
        self.okunan_terminaller: set[str] = set()

        # Hikaye durumu
        self.hikaye_durum = {
            "karantina_terminaller": 0,
            "karantina_boss": False,
            "yeralti_boss": False,
            "otoyol_boss": False,
            "final_hazir": False,
        }

        # Tüm engelleri birleşik liste (çarpışma için)
        self._tum_engeller: list[pygame.Rect] = []
        for bolge in self.bolgeler.values():
            self._tum_engeller.extend(bolge["engeller"])

    def oyuncu_bolgesi(self, x: float, y: float) -> str | None:
        """Oyuncunun hangi bölgede olduğunu döndürür."""
        for key, bolge in self.bolgeler.items():
            if bolge["sinirlar"].collidepoint(int(x), int(y)):
                return key
        # Geçitlerde mi?
        for gecit in self.gecitler:
            if gecit["kapi_rect"].collidepoint(int(x), int(y)):
                return gecit["baslangic"]
        return None

    def bolge_tehlike(self, x: float, y: float) -> int:
        """Oyuncunun bulunduğu bölgenin tehlike seviyesini döndürür."""
        bolge_key = self.oyuncu_bolgesi(x, y)
        if bolge_key and bolge_key in self.bolgeler:
            return self.bolgeler[bolge_key].get("tehlike", 1)
        return 1

    def guvenli_mi(self, x: float, y: float) -> bool:
        """Koordinat güvenli bölgede mi?"""
        for gb in self.guvenli_bolgeler:
            if gb["rect"].collidepoint(int(x), int(y)):
                return True
        return False

    def kapi_acik_mi(self, kilit: str | None) -> bool:
        """Bir kapı açık mı kontrol eder."""
        if kilit is None:
            return True
        return self.hikaye_durum.get(kilit, False)

    def bolge_erisebilir_mi(self, bolge_key: str) -> bool:
        """Bölgeye erişim var mı?"""
        kilit = self.bolgeler[bolge_key].get("kilit")
        return self.kapi_acik_mi(kilit)

    def boss_oldu(self, bolge_key: str):
        """Boss öldürüldüğünde çağrılır, kapıları açar."""
        if bolge_key == "karantina":
            self.hikaye_durum["karantina_boss"] = True
        elif bolge_key == "yeralti":
            self.hikaye_durum["yeralti_boss"] = True
        elif bolge_key == "otoyol":
            self.hikaye_durum["otoyol_boss"] = True
            self.hikaye_durum["final_hazir"] = True

    def nokta_duvar_icinde(self, x, y, yaricap=0):
        """Hızlı çarpışma kontrolü."""
        for r in self._tum_engeller:
            if (x + yaricap > r.left and x - yaricap < r.right and
                    y + yaricap > r.top and y - yaricap < r.bottom):
                return True
        return False

    def hareketi_sinirla(self, eski_x, eski_y, yeni_x, yeni_y, yaricap):
        """Duvar çarpışma çözümü."""
        if not self.nokta_duvar_icinde(yeni_x, yeni_y, yaricap):
            return yeni_x, yeni_y
        only_x = not self.nokta_duvar_icinde(yeni_x, eski_y, yaricap)
        only_y = not self.nokta_duvar_icinde(eski_x, yeni_y, yaricap)
        if only_x:
            return yeni_x, eski_y
        if only_y:
            return eski_x, yeni_y
        return eski_x, eski_y

    def gunluk_kontrol(self, px: float, py: float) -> str | None:
        """Günlük noktası yakınlık kontrolü."""
        bolge_key = self.oyuncu_bolgesi(px, py)
        if not bolge_key or bolge_key not in self.bolgeler:
            return None
        for (gx, gy), text in self.bolgeler[bolge_key].get("gunluk_noktalari", []):
            if text in self.acilan_kayitlar:
                continue
            if math.hypot(gx - px, gy - py) <= 70:
                self.acilan_kayitlar.append(text)
                return text
        return None

    def terminal_yakin(self, px: float, py: float):
        """Terminal yakınlık kontrolü."""
        bolge_key = self.oyuncu_bolgesi(px, py)
        if not bolge_key or bolge_key not in self.bolgeler:
            return None
        for terminal in self.bolgeler[bolge_key].get("terminaller", []):
            tx, ty = terminal["pos"]
            if math.hypot(tx - px, ty - py) <= 85:
                return terminal
        return None

    def terminal_oku(self, terminal) -> list[str]:
        """Terminal okuma."""
        tid = str(terminal["id"])
        if tid not in self.okunan_terminaller:
            self.okunan_terminaller.add(tid)
            if f"Terminal[{tid}]" not in self.acilan_kayitlar:
                self.acilan_kayitlar.append(f"Terminal[{tid}] açıldı")
            # Karantina terminal sayacı
            if tid.startswith("k"):
                self.hikaye_durum["karantina_terminaller"] = min(
                    3, self.hikaye_durum["karantina_terminaller"] + 1
                )
        return list(terminal["lines"])

    def npc_listesi_olustur(self) -> list[NPC]:
        """Tüm dünya NPC'lerini oluşturur."""
        npcler = []
        for bolge in self.bolgeler.values():
            for x, y, tip, rol in bolge.get("npcs_veri", []):
                npc = NPC(x, y, tip)
                npc.rol = rol  # gorev / lore / satici
                npcler.append(npc)
        return npcler

    def spawn_tipleri(self, bolge_key: str) -> list[str]:
        """Bölge için uygun zombi tiplerini döndürür."""
        if bolge_key in self.bolgeler:
            return self.bolgeler[bolge_key].get("spawn_tipler", ["normal"])
        return ["normal"]

    def rastgele_guvenli_nokta(self, yaricap=24) -> tuple[int, int]:
        """Güvenli başlangıç noktası (Merkez Meydan)."""
        merkez = self.bolgeler["merkez"]["sinirlar"]
        for _ in range(40):
            x = random.randint(merkez.x + yaricap, merkez.right - yaricap)
            y = random.randint(merkez.y + yaricap, merkez.bottom - yaricap)
            if not self.nokta_duvar_icinde(x, y, yaricap):
                return x, y
        return merkez.centerx, merkez.centery

    def gorunur_engeller(self, gorunur_alan: pygame.Rect) -> list[pygame.Rect]:
        """Sadece ekranda görünen engelleri döndürür (performans)."""
        return [r for r in self._tum_engeller if gorunur_alan.colliderect(r)]

    def gorunur_isiklar(self, gorunur_alan: pygame.Rect) -> list:
        """Sadece ekranda görünen ışıkları döndürür."""
        sonuc = []
        for bolge in self.bolgeler.values():
            for lx, ly, renk in bolge.get("isiklar", []):
                if gorunur_alan.collidepoint(lx, ly):
                    sonuc.append((lx, ly, renk))
        return sonuc

    def gorunur_landmarks(self, gorunur_alan: pygame.Rect) -> list:
        """Sadece ekranda görünen landmark'ları döndürür."""
        sonuc = []
        for bolge in self.bolgeler.values():
            for lx, ly, isim, renk in bolge.get("landmarks", []):
                if gorunur_alan.collidepoint(lx, ly):
                    sonuc.append((lx, ly, isim, renk))
        return sonuc
