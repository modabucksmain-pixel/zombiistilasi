# ============================================================
#  sistemler/mod_yukleyici.py — Mod Sistemi Temeli
# ============================================================
"""mods/ klasöründeki JSON modları okur ve oyuna entegre eder."""
from __future__ import annotations
import json
import os
from typing import Any
import pygame

PROJE_DIZIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD_DIZIN = os.path.join(PROJE_DIZIN, "mods")


def _mods_dizin_hazirla() -> None:
    os.makedirs(MOD_DIZIN, exist_ok=True)
    ornek = os.path.join(MOD_DIZIN, "ornek_mod.json")
    if not os.path.exists(ornek):
        _ornek_mod_yaz(ornek)


def _ornek_mod_yaz(dosya: str) -> None:
    ornek: dict[str, Any] = {
        "meta": {
            "isim": "Örnek Mod",
            "yazar": "Dr. Kerem Aydın",
            "versiyon": "1.0.0",
            "aciklama": "Zombi İstilası için örnek mod. Yeni zombi, silah ve harita ekler.",
        },
        "zombi_tipleri": {
            "cyber_zombi": {
                "hiz": 130,
                "can": 180,
                "hasar": 22,
                "skor": 250,
                "para": 220,
                "r": 20,
                "renk": [0, 200, 255],
                "ic": [100, 240, 255],
            }
        },
        "silahlar": {
            "plasma_rifle_nrm": {
                "isim": "Plazma Tüfeği",
                "emoji": "🔵",
                "fiyat": 6000,
                "hasar": 200,
                "ates_hizi": 0.4,
                "mermi_hizi": 1600,
                "yayilma": 2,
                "mermi_adeti": 1,
                "kapasite": 30,
                "renk": [0, 200, 255],
                "tip": "delici",
                "patlama_r": 0,
                "efekt": "sok",
                "aciklama": ["Plazma hasar", "Elektro efekt", "Zırh delici"],
            }
        },
        "haritalar": [
            {
                "isim": "Deprem Bölgesi",
                "zemin": [15, 12, 18],
                "cizgi": [30, 25, 38],
                "karo": 80,
                "engeller": [
                    [150, 200, 300, 80],
                    [600, 150, 200, 300],
                ],
            }
        ],
        "ayarlar": {
            "zombi_can_carpani": 1.1,
            "para_carpani": 1.2,
        },
    }
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(ornek, f, ensure_ascii=False, indent=2)


class ModYukleyici:
    """Mod dosyalarını yükler ve oyun verilerine entegre eder."""

    def __init__(self) -> None:
        _mods_dizin_hazirla()
        self.yuklenen_modlar: list[dict[str, Any]] = []
        self.hatalar: list[str] = []

    def tum_modlari_yukle(self) -> None:
        """mods/ dizinindeki tüm JSON modları yükle."""
        self.yuklenen_modlar.clear()
        self.hatalar.clear()

        if not os.path.exists(MOD_DIZIN):
            return

        for dosya_adi in os.listdir(MOD_DIZIN):
            if not dosya_adi.endswith(".json"):
                continue
            yol = os.path.join(MOD_DIZIN, dosya_adi)
            try:
                with open(yol, "r", encoding="utf-8") as f:
                    mod = json.load(f)
                    mod["_dosya"] = dosya_adi
                    self.yuklenen_modlar.append(mod)
            except Exception as e:
                self.hatalar.append(f"{dosya_adi}: {e}")

    def ayarlari_uygula(self, zombi_tipler: dict, silahlar: dict, silah_sirasi: list) -> None:
        """Yüklenen modlardan zombi/silah verilerini ana datalara ekle."""
        for mod in self.yuklenen_modlar:
            # Yeni zombi tipleri
            for tip, veri in mod.get("zombi_tipleri", {}).items():
                renk_veri = veri.copy()
                if isinstance(renk_veri.get("renk"), list):
                    renk_veri["renk"] = tuple(renk_veri["renk"])
                if isinstance(renk_veri.get("ic"), list):
                    renk_veri["ic"] = tuple(renk_veri["ic"])
                zombi_tipler[tip] = renk_veri

            # Yeni silahlar
            for silah_key, silah_veri in mod.get("silahlar", {}).items():
                if isinstance(silah_veri.get("renk"), list):
                    silah_veri["renk"] = tuple(silah_veri["renk"])
                silahlar[silah_key] = silah_veri
                if silah_key not in silah_sirasi:
                    silah_sirasi.append(silah_key)

    @property
    def mod_isim_listesi(self) -> list[str]:
        return [m.get("meta", {}).get("isim", m.get("_dosya", "?")) for m in self.yuklenen_modlar]

    @property
    def yuklu_mod_sayisi(self) -> int:
        return len(self.yuklenen_modlar)


mod_yukleyici = ModYukleyici()
