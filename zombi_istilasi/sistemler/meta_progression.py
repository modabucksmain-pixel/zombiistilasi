# ============================================================
#  sistemler/meta_progression.py — Roguelite Kalıcı Güçlenme
#  Run bitince kazanılan "Kan Kristali" ile kalıcı upgrade satın alınır.
#  Veriler kayitlar/meta.json'a yazılır.
# ============================================================
import json
import os

_DOSYA = os.path.join(os.path.dirname(__file__), "..", "kayitlar", "meta.json")

META_UPGRADELER = {
    "demir_yumruk": {
        "isim": "Demir Yumruk",
        "emoji": "👊",
        "aciklama": "Tüm hasar +%8 (kalıcı)",
        "max_seviye": 10,
        "baz_fiyat": 50,
        "fiyat_artan": 30,
        "efekt": "hasar_carpani",
        "deger_per_seviye": 0.08,
    },
    "celik_deri": {
        "isim": "Çelik Deri",
        "emoji": "🛡️",
        "aciklama": "Alınan hasar -%5 (kalıcı)",
        "max_seviye": 8,
        "baz_fiyat": 60,
        "fiyat_artan": 40,
        "efekt": "hasar_azaltma",
        "deger_per_seviye": 0.05,
    },
    "kan_icici": {
        "isim": "Kan İçici",
        "emoji": "🩸",
        "aciklama": "Her zombi ölümünde +2 can",
        "max_seviye": 5,
        "baz_fiyat": 80,
        "fiyat_artan": 60,
        "efekt": "vampir",
        "deger_per_seviye": 2,
    },
    "deli_bilim": {
        "isim": "Deli Bilim",
        "emoji": "🧪",
        "aciklama": "Element efekt süresi +%20",
        "max_seviye": 5,
        "baz_fiyat": 70,
        "fiyat_artan": 50,
        "efekt": "efekt_suresi",
        "deger_per_seviye": 0.20,
    },
    "kosucunun_mirasi": {
        "isim": "Koşucunun Mirası",
        "emoji": "💨",
        "aciklama": "Başlangıç hızı +10",
        "max_seviye": 6,
        "baz_fiyat": 55,
        "fiyat_artan": 35,
        "efekt": "baz_hiz",
        "deger_per_seviye": 10,
    },
    "kristal_kalkan": {
        "isim": "Kristal Kalkan",
        "emoji": "💠",
        "aciklama": "Başlangıç kalkanı +20",
        "max_seviye": 8,
        "baz_fiyat": 65,
        "fiyat_artan": 45,
        "efekt": "baz_kalkan",
        "deger_per_seviye": 20,
    },
    "servet_avcisi": {
        "isim": "Servet Avcısı",
        "emoji": "💰",
        "aciklama": "Zombilerden +%10 fazla para",
        "max_seviye": 5,
        "baz_fiyat": 45,
        "fiyat_artan": 30,
        "efekt": "para_carpani",
        "deger_per_seviye": 0.10,
    },
    "ultime_ustasi": {
        "isim": "Ultimate Ustası",
        "emoji": "⚡",
        "aciklama": "Ultimate bekleme -1.5s",
        "max_seviye": 5,
        "baz_fiyat": 90,
        "fiyat_artan": 70,
        "efekt": "ult_cd_azalt",
        "deger_per_seviye": 1.5,
    },
}


class MetaProgression:
    def __init__(self):
        self._veri = self._yukle()

    def _yukle(self):
        try:
            with open(_DOSYA, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"kristal": 0, "seviyeler": {k: 0 for k in META_UPGRADELER}}

    def _kaydet(self):
        os.makedirs(os.path.dirname(_DOSYA), exist_ok=True)
        with open(_DOSYA, "w", encoding="utf-8") as f:
            json.dump(self._veri, f, ensure_ascii=False, indent=2)

    @property
    def kristal(self):
        return self._veri.get("kristal", 0)

    def seviye(self, key):
        return self._veri.get("seviyeler", {}).get(key, 0)

    def upgrade_fiyati(self, key):
        sev = self.seviye(key)
        u = META_UPGRADELER[key]
        return u["baz_fiyat"] + sev * u["fiyat_artan"]

    def satin_alinabilir_mi(self, key):
        sev = self.seviye(key)
        if sev >= META_UPGRADELER[key]["max_seviye"]:
            return False
        return self.kristal >= self.upgrade_fiyati(key)

    def satin_al(self, key):
        if not self.satin_alinabilir_mi(key):
            return False
        self._veri["kristal"] -= self.upgrade_fiyati(key)
        self._veri.setdefault("seviyeler", {})[key] = self.seviye(key) + 1
        self._kaydet()
        return True

    def kristal_ekle(self, miktar):
        self._veri["kristal"] = self._veri.get("kristal", 0) + miktar
        self._kaydet()

    def efekt_degeri(self, efekt_adi):
        """Belirli bir efekt için toplam bonus değerini döner."""
        toplam = 0.0
        for key, u in META_UPGRADELER.items():
            if u["efekt"] == efekt_adi:
                toplam += self.seviye(key) * u["deger_per_seviye"]
        return toplam

    def run_sonu_kristal_hesapla(self, dalga_no, toplam_skor, toplam_oldurme):
        """Run sonunda kazanılacak kristalin hesabı."""
        baz = dalga_no * 5 + toplam_oldurme // 10 + toplam_skor // 500
        return max(1, baz)

    def oyuncu_bonuslarini_uygula(self, oyuncu):
        """Oyuncu oluşturulunca meta bonusları uygula."""
        from ayarlar import OYUNCU_BASLANGIC_CAN, OYUNCU_BASLANGIC_KALKAN
        # Hız bonusu
        oyuncu._meta_hiz_bonus = int(self.efekt_degeri("baz_hiz"))
        # Kalkan bonusu
        kalkan_bonus = int(self.efekt_degeri("baz_kalkan"))
        oyuncu.kalkan = min(999, oyuncu.kalkan + kalkan_bonus)
        oyuncu.max_kalkan += kalkan_bonus
        # Hasar azaltma
        oyuncu._meta_hasar_azaltma = self.efekt_degeri("hasar_azaltma")
        # Vampir
        oyuncu._meta_vampir = self.efekt_degeri("vampir")
        # Para çarpanı
        oyuncu._meta_para_carpani = 1.0 + self.efekt_degeri("para_carpani")
        # Hasar çarpanı (meta)
        oyuncu._meta_hasar_carpani = 1.0 + self.efekt_degeri("hasar_carpani")
        # Ultimate CD azaltma
        oyuncu._meta_ult_cd_azalt = self.efekt_degeri("ult_cd_azalt")
        # Efekt süresi
        oyuncu._meta_efekt_suresi = 1.0 + self.efekt_degeri("efekt_suresi")


# Global erişim için tekil örnek
meta_sis = MetaProgression()
