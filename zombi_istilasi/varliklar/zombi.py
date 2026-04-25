# ============================================================
#  varliklar/zombi.py — Element Efektleri (Yanma, Donma, Şok) ve Gölgeler
# ============================================================
import pygame
import math
import random
from ayarlar import ZOMBI_TIPLER, SIYAH
from varliklar.drop import Drop

class Zombi(pygame.sprite.Sprite):
    def __init__(self, x, y, tip="normal"):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.tip = tip
        v = ZOMBI_TIPLER[tip]
        self.baz_hiz = float(v["hiz"])
        self.hiz = self.baz_hiz
        self.can = float(v["can"])
        self.max_can = float(v["can"])
        self.hasar = v["hasar"]
        self.skor = v["skor"]
        self.para = v["para"]
        self.yari_cap = v["r"]
        self.renk = v["renk"]
        self.ic_renk = v["ic"]
        
        self.hit_sayac = 0.0
        self.vx = self.vy = 0.0
        self.zehir_sayac = 0.0
        
        # Element Durumları
        self.yanma_sayac = 0.0
        self.donma_sayac = 0.0
        self.zehir_hasar_sayac = 0.0
        self.sok_sayac = 0.0

        self._image_olustur()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _image_olustur(self):
        r = self.yari_cap
        boyut = r * 2 + 10
        img = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        cx = cy = boyut // 2
        
        # Zombi Gölgesi
        pygame.draw.circle(img, (0, 0, 0, 80), (cx + 4, cy + 4), r)
        
        # Gövde
        pygame.draw.circle(img, self.renk, (cx, cy), r)
        pygame.draw.circle(img, self.ic_renk, (cx, cy), max(1, r - 6))
        
        # Yüz
        off = max(3, r // 3)
        pygame.draw.line(img, SIYAH, (cx-off, cy-off), (cx+off, cy+off), 2)
        pygame.draw.line(img, SIYAH, (cx+off, cy-off), (cx-off, cy+off), 2)
        
        if self.tip == "boss":
            pygame.draw.polygon(img, (255, 215, 0), [(cx, cy-r-5), (cx-7, cy-r+5), (cx+7, cy-r+5)])
        elif self.tip == "patlayan":
            for i in range(4):
                a = i * 90
                ar = math.radians(a)
                pygame.draw.line(img, (255, 200, 0),
                    (cx + int(math.cos(ar)*r*0.6), cy + int(math.sin(ar)*r*0.6)),
                    (cx + int(math.cos(ar+0.3)*r), cy + int(math.sin(ar+0.3)*r)), 2)
        elif self.tip == "zehirli":
            pygame.draw.circle(img, (0, 255, 100, 80), (cx, cy), r + 3)
            
        self._base_image = img.copy()
        
        hit = img.copy()
        hl = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        pygame.draw.circle(hl, (255, 60, 60, 150), (cx, cy), r)
        hit.blit(hl, (0, 0))
        self._hit_image = hit
        self.image = self._base_image

    def durum_guncelle(self, dt):
        """Element efektlerini işler."""
        if self.yanma_sayac > 0:
            self.yanma_sayac -= dt
            self.can -= 15 * dt # Saniyede 15 yanma hasarı
            
        if self.zehir_hasar_sayac > 0:
            self.zehir_hasar_sayac -= dt
            self.can -= 25 * dt # Saniyede 25 zehir hasarı
            self.hiz = self.baz_hiz * 0.8
            
        if self.donma_sayac > 0:
            self.donma_sayac -= dt
            self.hiz = self.baz_hiz * 0.4
        elif self.zehir_hasar_sayac <= 0:
            self.hiz = self.baz_hiz
            
        if self.sok_sayac > 0:
            self.sok_sayac -= dt
            self.hiz = 0.0

    def update(self, dt, ox, oy, hareket_cozucu=None):
        self.durum_guncelle(dt)
        
        if self.hiz > 0:
            dx = ox - self.x
            dy = oy - self.y
            uzak = math.hypot(dx, dy)
            if uzak > 0:
                self.vx = (dx / uzak) * self.hiz
                self.vy = (dy / uzak) * self.hiz
            yeni_x = self.x + self.vx * dt
            yeni_y = self.y + self.vy * dt
            if hareket_cozucu:
                yeni_x, yeni_y = hareket_cozucu(self.x, self.y, yeni_x, yeni_y, self.yari_cap)
            self.x = yeni_x
            self.y = yeni_y
            
        self.rect.center = (int(self.x), int(self.y))
        
        if self.hit_sayac > 0:
            self.hit_sayac -= dt
            self.image = self._hit_image
        else:
            self.image = self._base_image
            
        # Görsel Efekt Katmanları (Donma, Yanma vb.)
        if self.donma_sayac > 0:
            d_img = self.image.copy()
            s = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 200, 255, 100), (s.get_width()//2, s.get_height()//2), self.yari_cap)
            d_img.blit(s, (0, 0))
            self.image = d_img
        elif self.yanma_sayac > 0:
            y_img = self.image.copy()
            s = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 100, 0, 100), (s.get_width()//2, s.get_height()//2), self.yari_cap)
            y_img.blit(s, (0, 0))
            self.image = y_img
        elif self.sok_sayac > 0:
            # Şok için sarsıntı efekti
            self.rect.x += random.randint(-2, 2)
            self.rect.y += random.randint(-2, 2)

        if self.tip == "zehirli":
            self.zehir_sayac += dt

    def mermi_carpisma(self, mermi):
        mc, mr = mermi.get_circle()
        if math.hypot(mc[0]-self.x, mc[1]-self.y) < (self.yari_cap + mr):
            self.can -= mermi.hasar
            self.hit_sayac = 0.10
            
            # Efekt Uygulama
            if mermi.efekt == "yanma": self.yanma_sayac = 3.0
            elif mermi.efekt == "donma": self.donma_sayac = 2.0
            elif mermi.efekt == "zehir": self.zehir_hasar_sayac = 4.0
            elif mermi.efekt == "sok": self.sok_sayac = 1.0
            
            if mermi.tip != "delici":
                mermi.kill()
            return self.can <= 0
        return False

    def oyuncuya_yakin_mi(self, ox, oy):
        return math.hypot(ox-self.x, oy-self.y) < (self.yari_cap + 18)

    def patlama_hasar_mesafe(self, ox, oy):
        return math.hypot(ox-self.x, oy-self.y)

    def drop_olustur(self):
        return Drop.rastgele_olustur(self.x, self.y)

    def can_bar_ciz(self, ekran):
        if self.can >= self.max_can: return
        bar_gen = 50 if self.tip != "boss" else 90
        bar_yuk = 6
        dolu = int(bar_gen * max(0, self.can) / self.max_can)
        cx, cy = int(self.x), int(self.y)
        pygame.draw.rect(ekran, (0, 0, 0), (cx-bar_gen//2 - 1, cy-self.yari_cap-12, bar_gen + 2, bar_yuk + 2), border_radius=3)
        pygame.draw.rect(ekran, (80, 0, 0), (cx-bar_gen//2, cy-self.yari_cap-11, bar_gen, bar_yuk), border_radius=2)
        if dolu > 0:
            renk = (210, 50, 50)
            if self.donma_sayac > 0: renk = (50, 150, 255)
            elif self.zehir_hasar_sayac > 0: renk = (150, 255, 50)
            pygame.draw.rect(ekran, renk, (cx-bar_gen//2, cy-self.yari_cap-11, dolu, bar_yuk), border_radius=2)

    @staticmethod
    def rastgele_dogur(ekran_w, ekran_h, tip="normal"):
        kenar = random.randint(0, 3)
        off = 90
        if kenar == 0:   x, y = random.randint(0, ekran_w), -off
        elif kenar == 1: x, y = ekran_w+off, random.randint(0, ekran_h)
        elif kenar == 2: x, y = random.randint(0, ekran_w), ekran_h+off
        else:            x, y = -off, random.randint(0, ekran_h)
        return Zombi(x, y, tip)
