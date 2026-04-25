# ============================================================
#  ayarlar.py — 60 Silah (Elementler) & Devasa Güncelleme
# ============================================================
import ctypes
import os


def _ekran_boyutu_al():
    """
    Mümkünse sistemin gerçek ekran çözünürlüğünü alır.
    Windows dışı ortamlarda güvenli varsayılan değere düşer.
    """
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    except Exception:
        return 1920, 1080


GENISLIK, YUKSEKLIK = _ekran_boyutu_al()

FPS = 60
BASLIK = "🧟 Zombi İstilası — 100+ Dev Güncelleme!"

# Renkler
SIYAH      = (0, 0, 0)
BEYAZ      = (255, 255, 255)
KIRMIZI    = (220, 50, 47)
YESIL      = (80, 220, 100)
MAVI       = (70, 130, 200)
SARI       = (255, 220, 0)
TURUNCU    = (255, 140, 0)
GRI        = (60, 60, 60)
KOYU_GRI   = (25, 25, 35)
ACIK_GRI   = (120, 120, 120)
ALTIN      = (255, 200, 0)
MOR        = (160, 60, 220)
CAMGOBEGI  = (80, 200, 255)
PEMBE      = (255, 100, 180)
ZIRH_MAVI  = (60, 140, 255)
ARKAPLAN   = (14, 18, 22)
ZOMBI_YESIL= (90, 160, 70)

# Oyuncu & Sistemler
OYUNCU_HIZ            = 210
OYUNCU_SPRINT_CARPAN  = 1.6
OYUNCU_STAMINA        = 100.0
OYUNCU_STAMINA_HARCAMA= 35.0
OYUNCU_STAMINA_REGEN  = 20.0
OYUNCU_BASLANGIC_CAN  = 150
OYUNCU_YARI_CAP       = 18
OYUNCU_HASAR_GECIKME  = 0.15
OYUNCU_HASAR_FLASH    = 0.3
OYUNCU_BASLANGIC_KALKAN= 80
OYUNCU_KALKAN_REGEN   = 10.0
OYUNCU_KALKAN_GECIKME = 3.0
ULTIMATE_COOLDOWN     = 18.0

MERMI_YARI_CAP = 5
ZOMBI_YARI_CAP = 18

_ZR = {
    "normal":   {"hiz": 80,  "can": 70,  "hasar": 10, "skor": 50,  "para": 50,  "r": 18, "renk": ZOMBI_YESIL,     "ic": (130, 190, 100)},
    "hizli":    {"hiz": 160, "can": 40,  "hasar": 8,  "skor": 80,  "para": 80,  "r": 16, "renk": (180, 220, 80),  "ic": (220, 255, 120)},
    "kosucu":   {"hiz": 240, "can": 25,  "hasar": 5,  "skor": 120, "para": 100, "r": 14, "renk": (255, 180, 50),  "ic": (255, 220, 120)},
    "patlayan": {"hiz": 70,  "can": 140, "hasar": 35, "skor": 150, "para": 130, "r": 22, "renk": (200, 80,  30),  "ic": (255, 130, 60)},
    "zehirli":  {"hiz": 75,  "can": 110, "hasar": 15, "skor": 140, "para": 120, "r": 20, "renk": (60,  200, 100), "ic": (120, 255, 150)},
    "boss":     {"hiz": 55,  "can": 1200,"hasar": 40, "skor": 800, "para": 600, "r": 38, "renk": (140, 50,  200), "ic": (180, 90,  240)},
}
ZOMBI_TIPLER = _ZR

XP_BAZA = 100
XP_CARPAN = 1.6
COMBO_MAX = 15
DALGA_ARASI_SURE = 3.0

# =======================================================
# 60+ SİLAH ÜRETİM SİSTEMİ (Elementler: Normal, Ateş, Buz, Zehir, Elektrik)
# =======================================================
TEMEL_SILAHLAR = {
    "tabanca":  {"isim": "Tabanca", "hasar": 35, "hiz": 0.25, "mermi_hizi": 750, "yayilma": 2, "adet": 1, "kapasite": -1, "tip": "normal"},
    "cift":     {"isim": "Çift Tab.", "hasar": 25, "hiz": 0.15, "mermi_hizi": 800, "yayilma": 6, "adet": 2, "kapasite": 140, "tip": "normal"},
    "smg":      {"isim": "SMG", "hasar": 22, "hiz": 0.08, "mermi_hizi": 820, "yayilma": 8, "adet": 1, "kapasite": 300, "tip": "normal"},
    "ak47":     {"isim": "Saldırı T.", "hasar": 55, "hiz": 0.12, "mermi_hizi": 860, "yayilma": 5, "adet": 1, "kapasite": 180, "tip": "normal"},
    "shotgun":  {"isim": "Pompalı", "hasar": 28, "hiz": 0.85, "mermi_hizi": 600, "yayilma": 28,"adet": 8, "kapasite": 45, "tip": "normal"},
    "sniper":   {"isim": "Keskin N.", "hasar": 400, "hiz": 1.5, "mermi_hizi": 2200,"yayilma": 0, "adet": 1, "kapasite": 25, "tip": "delici"},
    "lazer":    {"isim": "Lazer", "hasar": 110, "hiz": 0.35, "mermi_hizi": 1400,"yayilma": 0, "adet": 1, "kapasite": 60, "tip": "delici"},
    "minigun":  {"isim": "Minigun", "hasar": 24, "hiz": 0.04, "mermi_hizi": 900, "yayilma": 15,"adet": 1, "kapasite": 600, "tip": "normal"},
    "alev":     {"isim": "Alev Mak.", "hasar": 12, "hiz": 0.03, "mermi_hizi": 400, "yayilma": 25,"adet": 2, "kapasite": 800, "tip": "alev"},
    "bomba":    {"isim": "Bomba Atar", "hasar": 180, "hiz": 1.2, "mermi_hizi": 500, "yayilma": 0, "adet": 1, "kapasite": 15, "tip": "seken_bomba", "r": 120},
    "roket":    {"isim": "Roket A.", "hasar": 280, "hiz": 2.0, "mermi_hizi": 550, "yayilma": 0, "adet": 1, "kapasite": 12, "tip": "roket", "r": 160},
    "plazma":   {"isim": "Plazma", "hasar": 150, "hiz": 0.6, "mermi_hizi": 1000,"yayilma": 4, "adet": 1, "kapasite": 40, "tip": "delici_patlayan"},
}

ELEMENTLER = {
    "Nrm": {"isim": "", "carpan": 1.0, "renk": (200, 200, 200), "efekt": "yok", "fiyat_c": 1.0, "emoji": "⚙️"},
    "Ateş": {"isim": "Ateşli ", "carpan": 1.2, "renk": (255, 60, 20), "efekt": "yanma", "fiyat_c": 1.5, "emoji": "🔥"},
    "Buz":  {"isim": "Buzlu ", "carpan": 0.9, "renk": (50, 200, 255), "efekt": "donma", "fiyat_c": 1.4, "emoji": "❄️"},
    "Zehir":{"isim": "Zehirli ", "carpan": 1.1, "renk": (120, 255, 50), "efekt": "zehir", "fiyat_c": 1.6, "emoji": "☣️"},
    "Şok":  {"isim": "Elektro ", "carpan": 1.4, "renk": (255, 255, 50), "efekt": "sok", "fiyat_c": 2.0, "emoji": "⚡"},
}

SILAHLAR = {}
SILAH_SIRASI = []

# Tabancayı her zaman Normal ve ücretsiz ekle
SILAHLAR["tabanca"] = {
    "isim": "Standart Tabanca", "emoji": "🔫", "fiyat": 0, "hasar": 40, "ates_hizi": 0.25,
    "mermi_hizi": 750, "yayilma": 2, "mermi_adeti": 1, "kapasite": -1, "renk": (200,200,200),
    "tip": "normal", "patlama_r": 0, "efekt": "yok", "aciklama": ["Sonsuz mermi", "Güvenilir"]
}
SILAH_SIRASI.append("tabanca")

baz_fiyatlar = {
    "cift": 500, "smg": 700, "ak47": 1100, "shotgun": 1000, "sniper": 1800,
    "lazer": 2500, "minigun": 3200, "alev": 2800, "bomba": 3500, "roket": 4200, "plazma": 5000
}

# 60 silahı oluştur
for s_key, s_veri in TEMEL_SILAHLAR.items():
    if s_key == "tabanca": continue
    for e_key, e_veri in ELEMENTLER.items():
        yeni_key = f"{s_key}_{e_key.lower()}"
        fiyat = int(baz_fiyatlar[s_key] * e_veri["fiyat_c"])
        tam_isim = f"{e_veri['isim']}{s_veri['isim']}"
        SILAHLAR[yeni_key] = {
            "isim": tam_isim[:16], "emoji": e_veri["emoji"], "fiyat": fiyat,
            "hasar": int(s_veri["hasar"] * e_veri["carpan"]), "ates_hizi": s_veri["hiz"],
            "mermi_hizi": s_veri["mermi_hizi"], "yayilma": s_veri["yayilma"],
            "mermi_adeti": s_veri["adet"], "kapasite": s_veri["kapasite"],
            "renk": e_veri["renk"], "tip": s_veri["tip"], "patlama_r": s_veri.get("r", 0),
            "efekt": e_veri["efekt"],
            "aciklama": [f"Hasar: {int(s_veri['hasar']*e_veri['carpan'])}", f"Kapasite: {s_veri['kapasite']}", f"Efekt: {e_veri['efekt'].upper()}"]
        }
        SILAH_SIRASI.append(yeni_key)

YUKSELTMELER = {
    "can":    {"isim": "Max Can",     "emoji": "❤️",  "aciklama": "+40 Max Can",        "fiyat": 400,  "max_seviye": 10},
    "stamina":{"isim": "Dayanıklılık","emoji": "🏃",  "aciklama": "+30 Stamina",        "fiyat": 300,  "max_seviye": 10},
    "hiz":    {"isim": "Hız",         "emoji": "👟",  "aciklama": "+25 Hareket Hızı",   "fiyat": 450,  "max_seviye": 6},
    "hasar":  {"isim": "Hasar",       "emoji": "⚔️",  "aciklama": "+%30 Tüm Hasar",     "fiyat": 600,  "max_seviye": 10},
    "kalkan": {"isim": "Kalkan",      "emoji": "🛡️",  "aciklama": "+40 Max Kalkan",     "fiyat": 500,  "max_seviye": 10},
    "zirh":   {"isim": "Zırh",        "emoji": "🔰",  "aciklama": "-%12 Alınan Hasar",  "fiyat": 700,  "max_seviye": 5},
    "mermi":  {"isim": "Geniş Şarjör","emoji": "📦",  "aciklama": "+%20 Cephane",       "fiyat": 650,  "max_seviye": 5},
}

DURBUNLER = {
    "red_dot": {"isim": "Red Dot (1x)", "zoom": 1.0, "fiyat": 200,  "emoji": "🔴"},
    "holo":    {"isim": "Holo (2x)",    "zoom": 2.0, "fiyat": 250,  "emoji": "🔘"},
    "4x":      {"isim": "Scope (4x)",   "zoom": 4.0, "fiyat": 350,  "emoji": "🔭"},
    "6x":      {"isim": "Sniper (6x)",  "zoom": 6.0, "fiyat": 400,  "emoji": "🎯"},
}

DURUM_MENU  = "menu"
DURUM_OYUN  = "oyun"
DURUM_PAUSE = "pause"
DURUM_SHOP  = "shop"
DURUM_BITTI = "bitti"
DURUM_GUNLUK = "gunluk"
DURUM_OZET = "ozet"
PROJE_DIZIN   = os.path.dirname(os.path.abspath(__file__))
KAYIT_DOSYASI = os.path.join(PROJE_DIZIN, "kayitlar", "highscore.json")
os.makedirs(os.path.dirname(KAYIT_DOSYASI), exist_ok=True)
