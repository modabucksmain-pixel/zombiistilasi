# ============================================================
#  varliklar/patlama.py — Roket Patlama Efekti
# ============================================================
import pygame
import math


class Patlama:
    def __init__(self, x, y, max_r):
        self.x = x
        self.y = y
        self.max_r = max_r
        self.r = 10.0
        self.sure = 0.45        # toplam süre
        self.gecen = 0.0
        self.hasar_verildi = False   # AoE hasarı yalnızca 1 kez verilir

    @property
    def bitti_mi(self):
        return self.gecen >= self.sure

    @property
    def ilerleme(self):
        return self.gecen / self.sure

    def update(self, dt):
        self.gecen += dt
        self.r = self.max_r * self.ilerleme

    def ciz(self, ekran):
        if self.bitti_mi:
            return
        alpha = int(255 * (1 - self.ilerleme))
        # Dış halka - turuncu
        surf = pygame.Surface((self.max_r * 2 + 20, self.max_r * 2 + 20), pygame.SRCALPHA)
        cx = cy = self.max_r + 10
        pygame.draw.circle(surf, (255, 120, 30, min(255, alpha + 60)),
                           (cx, cy), int(self.r), max(1, int(8 * (1 - self.ilerleme))))
        # İç dolgu - sarı
        pygame.draw.circle(surf, (255, 220, 50, alpha // 2), (cx, cy), max(1, int(self.r * 0.6)))
        ekran.blit(surf, (int(self.x) - self.max_r - 10, int(self.y) - self.max_r - 10))

    def zombi_hasari_ver(self, zombiler, hasar):
        """Patlama alanındaki tüm zombilere hasar ver. Yalnızca 1 kez çalışır."""
        if self.hasar_verildi:
            return []
        self.hasar_verildi = True
        oldukler = []
        for z in list(zombiler):
            dx = z.x - self.x
            dy = z.y - self.y
            if math.hypot(dx, dy) < self.max_r + z.yari_cap:
                z.can -= hasar
                z.hit_sayac = 0.2
                if z.can <= 0:
                    oldukler.append(z)
        return oldukler

    def zombi_hasari_ver_liste(self, hedefler, hasar):
        """Düz liste (zombiler + bosslar) üzerinde AoE hasar. Yalnızca 1 kez çalışır."""
        if self.hasar_verildi:
            return []
        self.hasar_verildi = True
        oldukler = []
        for z in hedefler:
            dx = z.x - self.x
            dy = z.y - self.y
            if math.hypot(dx, dy) < self.max_r + z.yari_cap:
                z.can -= hasar
                z.hit_sayac = 0.2
                if z.can <= 0:
                    oldukler.append(z)
        return oldukler
