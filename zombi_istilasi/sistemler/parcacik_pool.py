# ============================================================
#  sistemler/parcacik_pool.py — Parçacık Pool Sistemi
#  Önceden 500 parçacık yaratıp geri dönüştürür.
#  FPS %15-20 artış bekleniyor.
# ============================================================
"""Object pool pattern ile yüksek performanslı parçacık sistemi."""
from __future__ import annotations
import math
import random
import pygame


class Parcacik:
    """Tek bir parçacık — poollanabilir."""

    __slots__ = (
        "x", "y", "vx", "vy", "omur", "max_omur",
        "renk", "r", "aktif", "yerçekimi",
    )

    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.omur = 0.0
        self.max_omur = 0.5
        self.renk = (255, 255, 255)
        self.r = 3
        self.aktif = False
        self.yerçekimi = 80.0

    def reset(
        self,
        x: float, y: float,
        vx: float, vy: float,
        omur: float,
        renk: tuple[int, int, int],
        r: int = 3,
        yercekimi: float = 80.0,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.omur = omur
        self.max_omur = omur
        self.renk = renk
        self.r = r
        self.aktif = True
        self.yerçekimi = yercekimi

    def guncelle(self, dt: float) -> bool:
        if not self.aktif:
            return False
        self.omur -= dt
        if self.omur <= 0:
            self.aktif = False
            return False
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.yerçekimi * dt
        return True

    def ciz(self, ekran: pygame.Surface) -> None:
        if not self.aktif or self.r <= 0:
            return
        alpha = int(255 * (self.omur / max(0.01, self.max_omur)))
        # Küçük SRCALPHA yüzeyi yerine direkt çiz (hızlı)
        if self.r == 1:
            ekran.set_at((int(self.x), int(self.y)), self.renk)
        else:
            pygame.draw.circle(ekran, self.renk, (int(self.x), int(self.y)), self.r)


class ParcacikPool:
    """
    Önceden yaratılmış parçacık havuzu.
    Yeni objeler yerine mevcut olanlar sıfırlanarak yeniden kullanılır.
    """

    HAVUZ_BOYUTU = 600

    def __init__(self) -> None:
        self._havuz: list[Parcacik] = [Parcacik() for _ in range(self.HAVUZ_BOYUTU)]
        self._indeks = 0

    def _al(self) -> Parcacik:
        """Havuzdan boş parçacık al (round-robin)."""
        p = self._havuz[self._indeks % self.HAVUZ_BOYUTU]
        self._indeks = (self._indeks + 1) % self.HAVUZ_BOYUTU
        return p

    def kan_fickirti(
        self,
        x: float, y: float,
        adet: int = 8,
        renk: tuple[int, int, int] = (180, 20, 20),
    ) -> None:
        for _ in range(adet):
            aci = random.uniform(0, math.tau)
            hiz = random.uniform(40, 180)
            omur = random.uniform(0.3, 0.8)
            r = random.randint(2, 5)
            p = self._al()
            p.reset(x, y, math.cos(aci) * hiz, math.sin(aci) * hiz, omur, renk, r)

    def patlama_parcacigi(
        self,
        x: float, y: float,
        adet: int = 16,
        renk: tuple[int, int, int] = (255, 160, 30),
    ) -> None:
        for _ in range(adet):
            aci = random.uniform(0, math.tau)
            hiz = random.uniform(80, 300)
            omur = random.uniform(0.2, 0.6)
            r = random.randint(2, 6)
            p = self._al()
            p.reset(x, y, math.cos(aci) * hiz, math.sin(aci) * hiz, omur, renk, r, yercekimi=120.0)

    def mermi_izi(
        self,
        x: float, y: float,
        aci: float,
        renk: tuple[int, int, int] = (255, 255, 100),
    ) -> None:
        for _ in range(3):
            spread = random.uniform(-0.3, 0.3)
        hiz = random.uniform(20, 60)
        omur = random.uniform(0.06, 0.18)
        p = self._al()
        p.reset(
            x + random.uniform(-3, 3),
            y + random.uniform(-3, 3),
            math.cos(aci + spread) * hiz,
            math.sin(aci + spread) * hiz,
            omur, renk, 2, yercekimi=0.0
        )

    def guncelle_ve_ciz(self, ekran: pygame.Surface, dt: float) -> None:
        for p in self._havuz:
            if p.aktif:
                p.guncelle(dt)
                if p.aktif:
                    p.ciz(ekran)

    @property
    def aktif_sayisi(self) -> int:
        return sum(1 for p in self._havuz if p.aktif)


# Singleton instance
parcacik_pool = ParcacikPool()
