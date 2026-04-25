# ============================================================
#  varliklar/zombi.py — Gelişmiş tip davranışları
# ============================================================
from __future__ import annotations

import math
import random
import pygame

from ayarlar import SIYAH, ZOMBI_TIPLER
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

        # Element durumları
        self.yanma_sayac = 0.0
        self.donma_sayac = 0.0
        self.zehir_hasar_sayac = 0.0
        self.sok_sayac = 0.0

        # Davranış durumları
        self.suru_bonusu = False
        self.kacis_sure = 0.0
        self.patlama_sayac = -1.0
        self.patlamaya_hazir = False
        self.sniper_sayac = 1.2
        self.son_vurus_headshot = False

        # Idle/Aggro algılama sistemi
        _fark_tablosu = {
            "normal": 400, "hizli": 500, "kosucu": 600,
            "patlayan": 350, "zehirli": 400, "zirhli": 350,
            "kopek": 550, "sniper_zombi": 700, "elektrik": 400,
            "vampir": 450, "donusturucu": 400, "kalkan": 350,
            "mini_boss": 500,
        }
        self.fark_mesafe = float(_fark_tablosu.get(tip, 400))
        self.agresif = False      # Oyuncuyu fark etti mi?
        self.idle_yuruyus = 0.0   # Idle'da küçük yürüyüş sayacı
        self.idle_aci = random.uniform(0, math.tau)  # Idle yönü

        self._image_olustur()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _image_olustur(self):
        r = self.yari_cap
        boyut = r * 2 + 10
        img = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        cx = cy = boyut // 2

        pygame.draw.circle(img, (0, 0, 0, 80), (cx + 4, cy + 4), r)
        pygame.draw.circle(img, self.renk, (cx, cy), r)
        pygame.draw.circle(img, self.ic_renk, (cx, cy), max(1, r - 6))

        off = max(3, r // 3)
        pygame.draw.line(img, SIYAH, (cx - off, cy - off), (cx + off, cy + off), 2)
        pygame.draw.line(img, SIYAH, (cx + off, cy - off), (cx - off, cy + off), 2)

        if self.tip == "boss":
            pygame.draw.polygon(img, (255, 215, 0), [(cx, cy - r - 5), (cx - 7, cy - r + 5), (cx + 7, cy - r + 5)])
        elif self.tip == "patlayan":
            for i in range(4):
                a = i * 90
                ar = math.radians(a)
                pygame.draw.line(
                    img,
                    (255, 200, 0),
                    (cx + int(math.cos(ar) * r * 0.6), cy + int(math.sin(ar) * r * 0.6)),
                    (cx + int(math.cos(ar + 0.3) * r), cy + int(math.sin(ar + 0.3) * r)),
                    2,
                )
        elif self.tip == "zehirli":
            pygame.draw.circle(img, (0, 255, 100, 80), (cx, cy), r + 3)
        elif self.tip == "zirhli":
            pygame.draw.rect(img, (140, 150, 170), (cx - r + 3, cy - 5, r * 2 - 6, 10), border_radius=4)
        elif self.tip == "sniper_zombi":
            pygame.draw.circle(img, (220, 120, 255), (cx + r // 2, cy - r // 2), 4)
        elif self.tip == "kopek":
            pygame.draw.ellipse(img, (90, 70, 50), (cx - r, cy - r // 2, r * 2, r))

        self._base_image = img.copy()

        hit = img.copy()
        hl = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        pygame.draw.circle(hl, (255, 60, 60, 150), (cx, cy), r)
        hit.blit(hl, (0, 0))
        self._hit_image = hit
        self.image = self._base_image

    def durum_guncelle(self, dt):
        if self.yanma_sayac > 0:
            self.yanma_sayac -= dt
            self.can -= 15 * dt

        if self.zehir_hasar_sayac > 0:
            self.zehir_hasar_sayac -= dt
            self.can -= 25 * dt
            self.hiz = self.baz_hiz * 0.8

        if self.donma_sayac > 0:
            self.donma_sayac -= dt
            self.hiz = self.baz_hiz * 0.4
        elif self.zehir_hasar_sayac <= 0:
            self.hiz = self.baz_hiz

        if self.sok_sayac > 0:
            self.sok_sayac -= dt
            self.hiz = 0.0

    def update(self, dt, ox, oy, hareket_cozucu=None, yakin_ayni_tip=0):
        self.durum_guncelle(dt)
        self.sniper_sayac = max(0.0, self.sniper_sayac - dt)

        self.suru_bonusu = yakin_ayni_tip >= 2
        bonus = 1.15 if self.suru_bonusu else 1.0
        if self.suru_bonusu:
            self.hasar = ZOMBI_TIPLER[self.tip]["hasar"] * 1.15
        else:
            self.hasar = ZOMBI_TIPLER[self.tip]["hasar"]

        dx = ox - self.x
        dy = oy - self.y
        uzak = math.hypot(dx, dy) or 1.0

        # ── Idle / Aggro algılama ────────────────────────────
        # Hasar aldıysa hemen agresif ol
        if self.can < self.max_can:
            self.agresif = True
        # Oyuncu fark mesafesi içindeyse agresif ol
        elif uzak <= self.fark_mesafe:
            self.agresif = True
        # Oyuncu çok uzaklaştıysa (fark × 1.5) tekrar idle
        elif uzak > self.fark_mesafe * 1.5:
            self.agresif = False

        # ── IDLE: Oyuncuyu fark etmedi ───────────────────────
        if not self.agresif:
            self.idle_yuruyus -= dt
            if self.idle_yuruyus <= 0:
                self.idle_yuruyus = random.uniform(2.0, 5.0)
                self.idle_aci = random.uniform(0, math.tau)
            # Çok yavaş rastgele yürüyüş
            idle_hiz = self.baz_hiz * 0.15
            nx = math.cos(self.idle_aci)
            ny = math.sin(self.idle_aci)
            yeni_x = self.x + nx * idle_hiz * dt
            yeni_y = self.y + ny * idle_hiz * dt
            if hareket_cozucu:
                yeni_x, yeni_y = hareket_cozucu(self.x, self.y, yeni_x, yeni_y, self.yari_cap)
            self.x, self.y = yeni_x, yeni_y
            self.vx, self.vy = 0.0, 0.0
            self.rect.center = (int(self.x), int(self.y))
            # Görsel (idle durumda)
            if self.hit_sayac > 0:
                self.hit_sayac -= dt
                self.image = self._hit_image
            else:
                self.image = self._base_image
            return

        # ── AGGRO: Oyuncuyu kovalıyor ────────────────────────
        nx, ny = dx / uzak, dy / uzak

        if self.can <= self.max_can * 0.2:
            self.kacis_sure = max(self.kacis_sure, 1.8)
        if self.kacis_sure > 0:
            self.kacis_sure -= dt
            nx, ny = -nx, -ny

        # Sniper davranışı: 500 içinde atış, çok yakınsa geri kaç.
        if self.tip == "sniper_zombi":
            if uzak < 220:
                nx, ny = -nx, -ny
            elif 220 <= uzak <= 500:
                nx = ny = 0.0

        # Patlayan zombi 2.0: temas değil yaklaşınca sayaç
        if self.tip == "patlayan":
            if uzak <= 80 and self.patlama_sayac < 0:
                self.patlama_sayac = 1.5
            if self.patlama_sayac >= 0:
                self.patlama_sayac -= dt
                if self.patlama_sayac <= 0:
                    self.patlamaya_hazir = True

        hiz = self.hiz * bonus
        if self.hiz > 0 and (nx != 0 or ny != 0):
            self.vx, self.vy = nx * hiz, ny * hiz
            yeni_x = self.x + self.vx * dt
            yeni_y = self.y + self.vy * dt
            if hareket_cozucu:
                yeni_x, yeni_y = hareket_cozucu(self.x, self.y, yeni_x, yeni_y, self.yari_cap)
            self.x, self.y = yeni_x, yeni_y

        self.rect.center = (int(self.x), int(self.y))

        if self.hit_sayac > 0:
            self.hit_sayac -= dt
            self.image = self._hit_image
        else:
            self.image = self._base_image

        if self.donma_sayac > 0:
            d_img = self.image.copy()
            s = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 200, 255, 100), (s.get_width() // 2, s.get_height() // 2), self.yari_cap)
            d_img.blit(s, (0, 0))
            self.image = d_img
        elif self.yanma_sayac > 0:
            y_img = self.image.copy()
            s = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 100, 0, 100), (s.get_width() // 2, s.get_height() // 2), self.yari_cap)
            y_img.blit(s, (0, 0))
            self.image = y_img
        elif self.sok_sayac > 0:
            self.rect.x += random.randint(-2, 2)
            self.rect.y += random.randint(-2, 2)

        if self.tip == "zehirli":
            self.zehir_sayac += dt

        if self.tip == "patlayan" and self.patlama_sayac > 0:
            if int(self.patlama_sayac * 10) % 2 == 0:
                flash = self.image.copy()
                pygame.draw.circle(flash, (255, 60, 60, 150), (flash.get_width() // 2, flash.get_height() // 2), self.yari_cap)
                self.image = flash

    def mermi_carpisma(self, mermi):
        mc, mr = mermi.get_circle()
        if math.hypot(mc[0] - self.x, mc[1] - self.y) < (self.yari_cap + mr):
            hasar = mermi.hasar
            self.son_vurus_headshot = mc[1] <= self.y - self.yari_cap * 0.3
            if self.son_vurus_headshot:
                hasar *= 2.0
            if self.tip == "zirhli":
                # Önden %70 azaltma
                incoming_x = -mermi.vx
                incoming_y = -mermi.vy
                in_len = math.hypot(incoming_x, incoming_y) or 1.0
                incoming_x /= in_len
                incoming_y /= in_len
                f_len = math.hypot(self.vx, self.vy) or 1.0
                face_x = self.vx / f_len
                face_y = self.vy / f_len
                if incoming_x * face_x + incoming_y * face_y > 0.35:
                    hasar *= 0.3
            self.can -= hasar
            self.hit_sayac = 0.10

            if mermi.efekt == "yanma":
                self.yanma_sayac = 3.0
            elif mermi.efekt == "donma":
                self.donma_sayac = 2.0
            elif mermi.efekt == "zehir":
                self.zehir_hasar_sayac = 4.0
            elif mermi.efekt == "sok":
                self.sok_sayac = 1.0

            if mermi.tip != "delici":
                mermi.kill()
            return self.can <= 0
        return False

    def oyuncuya_yakin_mi(self, ox, oy):
        return math.hypot(ox - self.x, oy - self.y) < (self.yari_cap + 18)

    def patlama_hasar_mesafe(self, ox, oy):
        return math.hypot(ox - self.x, oy - self.y)

    def drop_olustur(self):
        return Drop.rastgele_olustur(self.x, self.y)

    def can_bar_ciz(self, ekran):
        if self.can >= self.max_can:
            return
        bar_gen = 50 if self.tip != "boss" else 90
        bar_yuk = 6
        dolu = int(bar_gen * max(0, self.can) / self.max_can)
        cx, cy = int(self.x), int(self.y)
        pygame.draw.rect(ekran, (0, 0, 0), (cx - bar_gen // 2 - 1, cy - self.yari_cap - 12, bar_gen + 2, bar_yuk + 2), border_radius=3)
        pygame.draw.rect(ekran, (80, 0, 0), (cx - bar_gen // 2, cy - self.yari_cap - 11, bar_gen, bar_yuk), border_radius=2)
        if dolu > 0:
            renk = (210, 50, 50)
            if self.donma_sayac > 0:
                renk = (50, 150, 255)
            elif self.zehir_hasar_sayac > 0:
                renk = (150, 255, 50)
            pygame.draw.rect(ekran, renk, (cx - bar_gen // 2, cy - self.yari_cap - 11, dolu, bar_yuk), border_radius=2)

        if self.suru_bonusu:
            aura = pygame.Surface((self.yari_cap * 4, self.yari_cap * 4), pygame.SRCALPHA)
            pygame.draw.circle(aura, (255, 150, 50, 60), (self.yari_cap * 2, self.yari_cap * 2), self.yari_cap + 12, 2)
            ekran.blit(aura, (self.x - self.yari_cap * 2, self.y - self.yari_cap * 2))

    @staticmethod
    def rastgele_dogur(ekran_w, ekran_h, tip="normal"):
        kenar = random.randint(0, 3)
        off = 90
        if kenar == 0:
            x, y = random.randint(0, ekran_w), -off
        elif kenar == 1:
            x, y = ekran_w + off, random.randint(0, ekran_h)
        elif kenar == 2:
            x, y = random.randint(0, ekran_w), ekran_h + off
        else:
            x, y = -off, random.randint(0, ekran_h)
        return Zombi(x, y, tip)
