# ============================================================
#  sistemler/muzik.py — Dinamik Müzik Sistemi
# ============================================================
"""Tehdit seviyesine, boss durumuna göre müzik adaptasyonu."""
from __future__ import annotations
import pygame
import math


class MuzikSistemi:
    """
    Oyun içi müzik katmanlarını dinamik olarak yönetir.
    Gerçek ses dosyaları olmadığında sinyal üretmeden geçer.
    """

    TEHDİT_ESIGI_DUSUK = 3
    TEHDÍT_ESIGI_YUKSEK = 8

    def __init__(self) -> None:
        self.aktif_mod: str = "ambiyans"  # ambiyans | orta | yuksek | boss
        self.hedef_hacim: float = 0.4
        self.mevcut_hacim: float = 0.0
        self.zaman: float = 0.0
        self._ses_yuklendi: bool = False
        self._init_mixer()

    def _init_mixer(self) -> None:
        """Pygame mixer'ı başlatmaya çalış, hata durumunu yönet."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._ses_yuklendi = True
        except Exception:
            self._ses_yuklendi = False

    def tehdit_guncelle(self, zombi_sayisi: int, boss_var: bool, dalga_no: int) -> None:
        """Tehdit durumuna göre müzik modunu değiştir."""
        if boss_var:
            yeni_mod = "boss"
            self.hedef_hacim = 0.9
        elif zombi_sayisi >= self.TEHDÍT_ESIGI_YUKSEK:
            yeni_mod = "yuksek"
            self.hedef_hacim = 0.75
        elif zombi_sayisi >= self.TEHDİT_ESIGI_DUSUK:
            yeni_mod = "orta"
            self.hedef_hacim = 0.55
        else:
            yeni_mod = "ambiyans"
            self.hedef_hacim = 0.35

        if yeni_mod != self.aktif_mod:
            self.aktif_mod = yeni_mod

    def guncelle(self, dt: float) -> None:
        """Hacim fade in/out uygula."""
        self.zaman += dt
        self.mevcut_hacim += (self.hedef_hacim - self.mevcut_hacim) * min(1.0, dt * 1.5)

        if self._ses_yuklendi and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.mevcut_hacim)

    @property
    def tehdit_rengi(self) -> tuple[int, int, int]:
        """HUD'a tehdit seviyesi için renk döndür."""
        match self.aktif_mod:
            case "boss":
                return (255, 50, 50)
            case "yuksek":
                return (255, 140, 0)
            case "orta":
                return (255, 220, 0)
            case _:
                return (80, 200, 100)

    @property
    def tehdit_metin(self) -> str:
        """Tehdit seviyesi metni."""
        match self.aktif_mod:
            case "boss":
                return "TEHLİKE: BOSS"
            case "yuksek":
                return "TEHLİKE: YÜKSEK"
            case "orta":
                return "TEHLİKE: ORTA"
            case _:
                return "TEHLİKE: DÜŞÜK"


muzik_sis = MuzikSistemi()
