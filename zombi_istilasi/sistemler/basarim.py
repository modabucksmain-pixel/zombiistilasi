# ============================================================
#  sistemler/basarim.py — Başarım Sistemi (30 Başarım)
# ============================================================
"""Oyun içi başarımları takip eder ve kayıt eder."""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from typing import Callable
import pygame
from ayarlar import PROJE_DIZIN, ALTIN, BEYAZ, CAMGOBEGI, MOR


KAYIT_DOSYASI = os.path.join(PROJE_DIZIN, "kayitlar", "basarimlar.json")


@dataclass
class Basarim:
    """Tek bir başarım tanımı."""
    kimlik: str
    isim: str
    aciklama: str
    emoji: str
    koşul: Callable[[dict], bool]
    tamamlandi: bool = False
    bildirim_sure: float = 0.0


# Tüm başarımlar
BASARIMLAR_TANIM: list[dict] = [
    {"kimlik": "ilk_kan",      "isim": "İlk Kan",          "emoji": "🩸", "aciklama": "İlk zombiyi etkisiz hale getir"},
    {"kimlik": "onden_gun",    "isim": "Öndeyim!",          "emoji": "🔫", "aciklama": "İlk dalgayı tamamla"},
    {"kimlik": "sniper_100",   "isim": "Uzman Nişancı",     "emoji": "🎯", "aciklama": "100 headshot gerçekleştir"},
    {"kimlik": "oldurulen_50", "isim": "Temizleyici",       "emoji": "💀", "aciklama": "50 zombi öldür"},
    {"kimlik": "oldurulen_500","isim": "Halk Düşmanı",      "emoji": "☠️", "aciklama": "500 zombi öldür"},
    {"kimlik": "dalga_10",     "isim": "Karantina Sağ.",    "emoji": "🏙️", "aciklama": "Dalga 10'a ulaş"},
    {"kimlik": "dalga_20",     "isim": "Yeraltı Gazisi",    "emoji": "🔬", "aciklama": "Dalga 20'ye ulaş"},
    {"kimlik": "dalga_25",     "isim": "Antidot",           "emoji": "💉", "aciklama": "Dalga 25'i tamamla (Zafer!)"},
    {"kimlik": "boss_ilk",     "isim": "Boss Avcısı",       "emoji": "👑", "aciklama": "İlk bossu öldür"},
    {"kimlik": "boss_tum",     "isim": "Direktör Düştü",    "emoji": "🦠", "aciklama": "4 farklı boss tipi öldür"},
    {"kimlik": "hasarsiz_5",   "isim": "Hayalet",           "emoji": "👻", "aciklama": "5 dalgayı hasarsız geç"},
    {"kimlik": "hasarsiz_10",  "isim": "Ölümsüz",           "emoji": "🛡️", "aciklama": "10 dalgayı hasarsız geç"},
    {"kimlik": "kombo_10",     "isim": "Combo Ustası",      "emoji": "⚡", "aciklama": "10x kombo yap"},
    {"kimlik": "kombo_20",     "isim": "Durdurulamaz!",     "emoji": "🌪️", "aciklama": "20x kombo yap"},
    {"kimlik": "para_5000",    "isim": "Savaş Tüccarı",     "emoji": "💰", "aciklama": "5000$ biriktir"},
    {"kimlik": "silah_10",     "isim": "Cephane Deposu",   "emoji": "🔧", "aciklama": "10 farklı silah al"},
    {"kimlik": "zehirli_50",   "isim": "Kimyager",          "emoji": "☣️", "aciklama": "50 zehirli zombi öldür"},
    {"kimlik": "patlayan_20",  "isim": "Bomba İmhacısı",   "emoji": "💣", "aciklama": "20 patlayan zombi öldür"},
    {"kimlik": "ult_kullan",   "isim": "ARGUS Karşıtı",     "emoji": "🚀", "aciklama": "İlk kez Ultimate kullan"},
    {"kimlik": "sprint_km",    "isim": "Koşucu",            "emoji": "🏃", "aciklama": "Toplam 5000px sprint koş"},
    {"kimlik": "ates_ilk",     "isim": "Yangın Çıkartıcı",  "emoji": "🔥", "aciklama": "Ateşli silahla 30 zombi öldür"},
    {"kimlik": "donma_ilk",    "isim": "Buzul Operatörü",   "emoji": "❄️", "aciklama": "Buzlu silahla 30 zombi öldür"},
    {"kimlik": "sok_ilk",      "isim": "Elektrik Mühendisi","emoji": "⚡", "aciklama": "Elektro silahla 30 zombi öldür"},
    {"kimlik": "zehir_ilk",    "isim": "Zehirci",           "emoji": "🧪", "aciklama": "Zehirli silahla 30 zombi öldür"},
    {"kimlik": "dalga_5_tam",  "isim": "Boss Dalgası Gaz.", "emoji": "💀", "aciklama": "Boss dalgasını (5) tamamla"},
    {"kimlik": "dalga_tam_hiz","isim": "Hız Rekoru",        "emoji": "⏱️", "aciklama": "Bir dalgayı 30 saniyede bitir"},
    {"kimlik": "can_az",       "isim": "Sınırda",           "emoji": "❤️", "aciklama": "10 can altında 1 dalga geç"},
    {"kimlik": "terminal_3",   "isim": "Araştırmacı",       "emoji": "💻", "aciklama": "3 farklı terminal oku"},
    {"kimlik": "npc_5",        "isim": "Koruyucu",          "emoji": "🤝", "aciklama": "5 farklı NPC ile konuş"},
    {"kimlik": "tum_harita",   "isim": "Kaşif",             "emoji": "🗺️", "aciklama": "Tüm bölgeleri keşfet"},
]


class BasarimSistemi:
    """Oyun genelinde başarımları takip eden sistem."""

    def __init__(self) -> None:
        self.basarimlar: dict[str, Basarim] = {}
        self.tamamlanan_ids: set[str] = set()
        self.bildirim_kuyrugu: list[Basarim] = []
        self.font_baslik: pygame.font.Font | None = None
        self.font_metin: pygame.font.Font | None = None
        self._font_hazir = False
        self._istatistikler: dict[str, int] = {
            "oldurulen": 0,
            "headshot": 0,
            "max_kombo": 0,
            "boss_oldurulen": 0,
            "dalga": 0,
            "hasarsiz_dalga": 0,
            "para": 0,
            "silah_sayisi": 0,
            "zehirli_oldurulen": 0,
            "patlayan_oldurulen": 0,
            "ult_kullanildi": 0,
            "terminal_okunan": 0,
            "npc_konusulan": 0,
            "ates_oldurulen": 0,
            "donma_oldurulen": 0,
            "sok_oldurulen": 0,
            "zehir_efekt_oldurulen": 0,
            "boss_tipleri": 0,
        }
        self._yukle()

    def _font_hazirla(self) -> None:
        if not self._font_hazir:
            self.font_baslik = pygame.font.SysFont("Consolas", 18, bold=True)
            self.font_metin = pygame.font.SysFont("Consolas", 14)
            self._font_hazir = True

    def _yukle(self) -> None:
        try:
            if os.path.exists(KAYIT_DOSYASI):
                with open(KAYIT_DOSYASI, "r", encoding="utf-8") as f:
                    veri = json.load(f)
                    self.tamamlanan_ids = set(veri.get("tamamlanan", []))
                    self._istatistikler.update(veri.get("istatistikler", {}))
        except Exception:
            pass

    def _kaydet(self) -> None:
        try:
            os.makedirs(os.path.dirname(KAYIT_DOSYASI), exist_ok=True)
            with open(KAYIT_DOSYASI, "w", encoding="utf-8") as f:
                json.dump({
                    "tamamlanan": list(self.tamamlanan_ids),
                    "istatistikler": self._istatistikler,
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def istatistik_guncelle(self, anahtar: str, miktar: int = 1) -> None:
        if anahtar in self._istatistikler:
            self._istatistikler[anahtar] += miktar

    def istatistik_ayarla(self, anahtar: str, deger: int) -> None:
        if anahtar in self._istatistikler:
            self._istatistikler[anahtar] = max(self._istatistikler[anahtar], deger)

    def kontrol_et(self) -> None:
        """Tüm başarım koşullarını kontrol et."""
        st = self._istatistikler
        kontroller = {
            "ilk_kan":      st["oldurulen"] >= 1,
            "onden_gun":    st["dalga"] >= 1,
            "sniper_100":   st["headshot"] >= 100,
            "oldurulen_50": st["oldurulen"] >= 50,
            "oldurulen_500":st["oldurulen"] >= 500,
            "dalga_10":     st["dalga"] >= 10,
            "dalga_20":     st["dalga"] >= 20,
            "dalga_25":     st["dalga"] >= 25,
            "boss_ilk":     st["boss_oldurulen"] >= 1,
            "boss_tum":     st["boss_tipleri"] >= 4,
            "hasarsiz_5":   st["hasarsiz_dalga"] >= 5,
            "hasarsiz_10":  st["hasarsiz_dalga"] >= 10,
            "kombo_10":     st["max_kombo"] >= 10,
            "kombo_20":     st["max_kombo"] >= 20,
            "para_5000":    st["para"] >= 5000,
            "silah_10":     st["silah_sayisi"] >= 10,
            "zehirli_50":   st["zehirli_oldurulen"] >= 50,
            "patlayan_20":  st["patlayan_oldurulen"] >= 20,
            "ult_kullan":   st["ult_kullanildi"] >= 1,
            "ates_ilk":     st["ates_oldurulen"] >= 30,
            "donma_ilk":    st["donma_oldurulen"] >= 30,
            "sok_ilk":      st["sok_oldurulen"] >= 30,
            "zehir_ilk":    st["zehir_efekt_oldurulen"] >= 30,
            "dalga_5_tam":  st["dalga"] >= 5,
            "terminal_3":   st["terminal_okunan"] >= 3,
            "npc_5":        st["npc_konusulan"] >= 5,
            "can_az":       st.get("can_az_dalga", 0) >= 1,
        }

        for kimlik, kosul in kontroller.items():
            if kosul and kimlik not in self.tamamlanan_ids:
                self._tamamla(kimlik)

    def _tamamla(self, kimlik: str) -> None:
        self.tamamlanan_ids.add(kimlik)
        # Bildirim için tanimlari bul
        for t in BASARIMLAR_TANIM:
            if t["kimlik"] == kimlik:
                # Basit bildirim objesi oluştur
                self.bildirim_kuyrugu.append(t.copy())
                break
        self._kaydet()

    def bildirim_al(self) -> dict | None:
        if self.bildirim_kuyrugu:
            return self.bildirim_kuyrugu.pop(0)
        return None

    @property
    def tamamlanan_sayisi(self) -> int:
        return len(self.tamamlanan_ids)

    @property
    def toplam_sayisi(self) -> int:
        return len(BASARIMLAR_TANIM)


basarim_sis = BasarimSistemi()
