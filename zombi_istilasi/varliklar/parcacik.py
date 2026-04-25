# ============================================================
#  varliklar/parcacik.py — Parçacık + Uçan Hasar Sayısı
# ============================================================
import pygame
import math
import random


class Parcacik:
    """Kan/ateş parçacığı."""
    __slots__ = ("x", "y", "vx", "vy", "r", "renk", "omur", "max_omur")

    def __init__(self, x, y, renk, hiz=120, omur=0.6):
        self.x = float(x)
        self.y = float(y)
        aci = random.uniform(0, math.pi * 2)
        hiz2 = random.uniform(hiz * 0.3, hiz)
        self.vx = math.cos(aci) * hiz2
        self.vy = math.sin(aci) * hiz2
        self.r = random.randint(2, 5)
        self.renk = renk
        self.omur = float(omur)
        self.max_omur = float(omur)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.90
        self.vy *= 0.90
        self.omur -= dt
        return self.omur > 0

    def ciz(self, ekran):
        alpha = int(255 * (self.omur / self.max_omur))
        surf = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.renk, alpha), (self.r, self.r), self.r)
        ekran.blit(surf, (int(self.x) - self.r, int(self.y) - self.r))


class HarasarSayisi:
    """Zombiye vurulunca hasar değeri uçar."""
    __slots__ = ("x", "y", "metin", "omur", "max_omur", "renk", "buyuk")

    def __init__(self, x, y, deger, renk=(255, 80, 80), buyuk=False):
        self.x = float(x + random.randint(-15, 15))
        self.y = float(y - 10)
        self.metin = str(int(deger)) if isinstance(deger, (float, int)) else str(deger)
        self.renk = renk
        self.omur = 1.2
        self.max_omur = 1.2
        self.buyuk = buyuk

    def update(self, dt):
        self.y -= 55 * dt
        self.omur -= dt
        return self.omur > 0

    def ciz(self, ekran, font_kucuk, font_orta):
        alpha = int(255 * (self.omur / self.max_omur))
        font = font_orta if self.buyuk else font_kucuk
        surf = font.render(self.metin, True, self.renk)
        surf.set_alpha(alpha)
        ekran.blit(surf, (int(self.x) - surf.get_width() // 2, int(self.y)))


def kan_parcaciklari(x, y, n=12, renk=(180, 20, 20)):
    """Zombi öldüğünde kan parçacıkları üretir."""
    return [Parcacik(x, y, renk, hiz=130, omur=random.uniform(0.4, 0.8)) for _ in range(n)]


class BasarimBildirimi:
    """Ekranda kayarak gelen başarım bildirimi."""
    def __init__(self, isim, aciklama):
        self.isim = isim
        self.aciklama = aciklama
        self.omur = 3.5
        self.max_omur = 3.5
        self.slide_x = 320.0    # Başlangıç X (ekran dışı sağdan)

    def update(self, dt):
        self.omur -= dt
        # Kayarak giriş + çıkış
        hedef = 20 if self.omur > 1.0 else -320
        self.slide_x += (hedef - self.slide_x) * min(1.0, dt * 8)
        return self.omur > 0

    def ciz(self, ekran, font_k, font_m, ekran_w, ekran_h):
        bw, bh = 300, 60
        bx = int(ekran_w - bw - self.slide_x)
        by = 400
        surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        alpha = int(220 * min(1.0, self.omur / 1.0))
        surf.fill((30, 20, 50, alpha))
        ekran.blit(surf, (bx, by))
        pygame.draw.rect(ekran, (255, 200, 0), (bx, by, bw, bh), 2, border_radius=8)
        t1 = font_m.render(f"🏆 {self.isim}", True, (255, 200, 0))
        t2 = font_k.render(self.aciklama, True, (200, 200, 200))
        t1.set_alpha(alpha)
        t2.set_alpha(alpha)
        ekran.blit(t1, (bx + 8, by + 6))
        ekran.blit(t2, (bx + 8, by + 34))
