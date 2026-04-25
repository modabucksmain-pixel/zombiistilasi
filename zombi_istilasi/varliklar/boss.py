# ============================================================
#  varliklar/boss.py — Boss Sistemi
#  Özel AI (faz geçişleri, özel saldırılar), giriş animasyonu,
#  can aşamaları, saldırı çeşitliliği.
# ============================================================
import pygame
import math
import random
from ayarlar import SIYAH, SARI, KIRMIZI, MOR, BEYAZ

# Boss tipleri - her birinin farklı rengi, özelliği ve saldırısı var
BOSS_TANIMLARI = {
    "et_gobegi": {
        "isim": "Et Göbeği",
        "can": 1800,
        "hiz": 55,
        "hasar": 45,
        "renk": (180, 50, 50),
        "ic_renk": (220, 90, 80),
        "yari_cap": 42,
        "skor": 1200,
        "para": 800,
        "ozel": "vurmak",       # Yakın mesafe büyük hasar
        "aciklama": "Koca gövdesiyle her şeyi ezer.",
    },
    "zehir_usta": {
        "isim": "Zehir Ustası",
        "can": 1400,
        "hiz": 70,
        "hasar": 25,
        "renk": (50, 180, 80),
        "ic_renk": (100, 255, 130),
        "yari_cap": 36,
        "skor": 1000,
        "para": 700,
        "ozel": "zehir_yagmuru",  # Etrafına zehir püskürtür
        "aciklama": "Zehir sisi içinde boğar.",
    },
    "firtina_lord": {
        "isim": "Fırtına Lordu",
        "can": 2000,
        "hiz": 45,
        "hasar": 60,
        "renk": (80, 100, 220),
        "ic_renk": (140, 160, 255),
        "yari_cap": 46,
        "skor": 1500,
        "para": 1000,
        "ozel": "elektrik_dalgasi",  # Etrafına şok dalgası gönderir
        "aciklama": "Yıldırımı emreder.",
    },
    "alev_kral": {
        "isim": "Alev Kral",
        "can": 1600,
        "hiz": 65,
        "hasar": 35,
        "renk": (220, 100, 20),
        "ic_renk": (255, 160, 50),
        "yari_cap": 38,
        "skor": 1100,
        "para": 750,
        "ozel": "alev_cemberi",  # Etrafında dönen ateş halkası
        "aciklama": "Her adımda alevler bırakır.",
    },
}

BOSS_SIRASI = ["et_gobegi", "zehir_usta", "alev_kral", "firtina_lord"]


class BossGirisAnimasyonu:
    """Boss sahneye girerken kamerayı ve ekranı etkileyen animasyon."""
    def __init__(self, boss_isim):
        self.aktif = True
        self.sure = 0.0
        self.max_sure = 3.0
        self.boss_isim = boss_isim
        self.titreme = 1.5
        self.flas_alpha = 0

    def guncelle(self, dt):
        self.sure += dt
        self.titreme = max(0.0, 1.5 - self.sure * 1.5)
        if self.sure < 0.5:
            self.flas_alpha = int(255 * (0.5 - self.sure) / 0.5)
        else:
            self.flas_alpha = 0
        if self.sure >= self.max_sure:
            self.aktif = False

    def ciz(self, ekran, font_buyuk, font_kucuk, genislik, yukseklik):
        if not self.aktif:
            return
        ilerleme = self.sure / self.max_sure

        # Kırmızı flaş
        if self.flas_alpha > 0:
            flas = pygame.Surface((genislik, yukseklik), pygame.SRCALPHA)
            flas.fill((180, 0, 0, self.flas_alpha))
            ekran.blit(flas, (0, 0))

        # Boss isim yazısı - ortada, büyük, soluklaşarak
        if ilerleme < 0.85:
            alpha = int(255 * min(1.0, (1.0 - ilerleme) * 2))
            sallanma = int(self.titreme * 8)

            # Arka panel
            panel = pygame.Surface((genislik, 120), pygame.SRCALPHA)
            panel.fill((0, 0, 0, int(alpha * 0.7)))
            ekran.blit(panel, (0, yukseklik // 2 - 60))

            # Kırmızı çizgi
            pygame.draw.rect(ekran, (200, 20, 20),
                             (0, yukseklik // 2 - 62, genislik, 3))
            pygame.draw.rect(ekran, (200, 20, 20),
                             (0, yukseklik // 2 + 58, genislik, 3))

            # Boss yazısı
            uyari = font_kucuk.render("⚠ BOSS DALGASI ⚠", True, (255, 60, 60))
            uyari.set_alpha(alpha)
            ekran.blit(uyari, (genislik // 2 - uyari.get_width() // 2,
                                yukseklik // 2 - 55 + random.randint(-sallanma, sallanma)))

            isim_surf = font_buyuk.render(self.boss_isim, True, (255, 200, 50))
            isim_surf.set_alpha(alpha)
            ekran.blit(isim_surf, (genislik // 2 - isim_surf.get_width() // 2,
                                    yukseklik // 2 - 20 + random.randint(-sallanma, sallanma)))


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, boss_tipi="et_gobegi"):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.tip = "boss"
        self.boss_tipi = boss_tipi

        t = BOSS_TANIMLARI.get(boss_tipi, BOSS_TANIMLARI["et_gobegi"])
        self.isim = t["isim"]
        self.can = float(t["can"])
        self.max_can = float(t["can"])
        self.baz_hiz = float(t["hiz"])
        self.hiz = self.baz_hiz
        self.hasar = t["hasar"]
        self.yari_cap = t["yari_cap"]
        self.renk = t["renk"]
        self.ic_renk = t["ic_renk"]
        self.skor = t["skor"]
        self.para = t["para"]
        self.ozel_saldiri = t["ozel"]

        # Durum
        self.faz = 1           # 1=normal, 2=gazap (<50% can), 3=son nefes (<25%)
        self.hit_sayac = 0.0
        self.ozel_sayac = 0.0
        self.ozel_aralik = 4.0  # Özel saldırı arası
        self.vx = self.vy = 0.0
        self.aci = 0.0
        self.dalga_aci = 0.0   # Animasyon için
        self.ozel_efektler = []  # Sahneye bırakılan efektler (zehir lekeleri vb.)

        # Can aşamaları efektleri
        self._faz2_gosterildi = False
        self._faz3_gosterildi = False

        self._image_olustur()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _image_olustur(self):
        r = self.yari_cap
        boyut = r * 2 + 20
        img = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        cx = cy = boyut // 2

        # Gölge
        pygame.draw.circle(img, (0, 0, 0, 100), (cx + 6, cy + 6), r)

        # Faz rengine göre aura
        if self.faz == 3:
            pygame.draw.circle(img, (255, 50, 50, 60), (cx, cy), r + 8)
        elif self.faz == 2:
            pygame.draw.circle(img, (255, 150, 20, 50), (cx, cy), r + 5)

        # Gövde
        pygame.draw.circle(img, self.renk, (cx, cy), r)
        pygame.draw.circle(img, self.ic_renk, (cx, cy), r - 8)

        # Taç
        for i in range(5):
            a = math.radians(-90 + i * 72)
            tx = cx + int(math.cos(a) * (r + 6))
            ty = cy + int(math.sin(a) * (r + 6))
            pygame.draw.circle(img, SARI, (tx, ty), 5)

        # Yüz - kötü ifade
        gz_off = r // 3
        pygame.draw.circle(img, (255, 0, 0), (cx - gz_off, cy - gz_off // 2), 5)
        pygame.draw.circle(img, (255, 0, 0), (cx + gz_off, cy - gz_off // 2), 5)
        pygame.draw.circle(img, (0, 0, 0), (cx - gz_off, cy - gz_off // 2), 2)
        pygame.draw.circle(img, (0, 0, 0), (cx + gz_off, cy - gz_off // 2), 2)

        # Ağız
        for i in range(6):
            ax = cx - 10 + i * 4
            pygame.draw.line(img, SIYAH, (ax, cy + gz_off), (ax + 3, cy + gz_off + 4), 2)

        self._base_image = img.copy()
        # Hit versiyonu
        hit = img.copy()
        hl = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        pygame.draw.circle(hl, (255, 255, 255, 160), (cx, cy), r)
        hit.blit(hl, (0, 0))
        self._hit_image = hit
        self.image = self._base_image

    def _faz_guncelle(self):
        oran = self.can / self.max_can
        yeni_faz = 1
        if oran < 0.25:
            yeni_faz = 3
        elif oran < 0.5:
            yeni_faz = 2

        if yeni_faz != self.faz:
            self.faz = yeni_faz
            self.hiz = self.baz_hiz * (1.0 + (yeni_faz - 1) * 0.35)  # Faz 2: +35%, Faz 3: +70%
            self.ozel_aralik = max(1.5, 4.0 - yeni_faz * 0.8)
            self._image_olustur()  # Aura'yı güncelle
            return True  # Faz değişti
        return False

    def update(self, dt, ox, oy, hareket_cozucu=None):
        self.dalga_aci += dt * 120
        faz_degisti = self._faz_guncelle()

        # Özel saldırı sayacı
        self.ozel_sayac -= dt
        ozel_tetiklendi = False
        if self.ozel_sayac <= 0:
            self.ozel_sayac = self.ozel_aralik
            ozel_tetiklendi = True

        # Harekete oyuncu yönüne bak
        dx = ox - self.x
        dy = oy - self.y
        uzak = math.hypot(dx, dy)
        self.aci = math.degrees(math.atan2(dy, dx))

        if uzak > 0 and self.hiz > 0:
            # Faz 2'de zigzag hareket
            if self.faz >= 2:
                zig = math.sin(math.radians(self.dalga_aci)) * 80
                perp_x = -dy / uzak
                perp_y = dx / uzak
                self.vx = (dx / uzak) * self.hiz + perp_x * zig
                self.vy = (dy / uzak) * self.hiz + perp_y * zig
            else:
                self.vx = (dx / uzak) * self.hiz
                self.vy = (dy / uzak) * self.hiz

            yeni_x = self.x + self.vx * dt
            yeni_y = self.y + self.vy * dt
            if hareket_cozucu:
                yeni_x, yeni_y = hareket_cozucu(self.x, self.y, yeni_x, yeni_y, self.yari_cap)
            self.x = yeni_x
            self.y = yeni_y

        self.rect.center = (int(self.x), int(self.y))

        # Görsel
        if self.hit_sayac > 0:
            self.hit_sayac -= dt
            self.image = self._hit_image
        else:
            rotated = pygame.transform.rotate(self._base_image,
                                              math.sin(math.radians(self.dalga_aci * 0.5)) * 5)
            self.image = rotated
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        return ozel_tetiklendi, faz_degisti

    def mermi_carpisma(self, mermi):
        from varliklar.mermi import Mermi
        import math
        mc, mr = mermi.get_circle()
        if math.hypot(mc[0] - self.x, mc[1] - self.y) < (self.yari_cap + mr):
            self.can -= mermi.hasar
            self.hit_sayac = 0.08
            if mermi.efekt == "yanma":
                self.can -= 5  # Boss ateşe biraz dayanıklı
            elif mermi.efekt == "donma":
                self.hiz = max(self.baz_hiz * 0.6, self.hiz * 0.85)
            if mermi.tip != "delici":
                mermi.kill()
            return self.can <= 0
        return False

    def ozel_saldiri_uygula(self, oyuncu, parcaciklar_listesi, zehir_havuzlari=None):
        """Özel saldırıyı tetikle, etkileri dışarı döndür."""
        efektler = []
        if self.ozel_saldiri == "vurmak":
            # Yakına çok büyük hasar
            import math
            if math.hypot(oyuncu.x - self.x, oyuncu.y - self.y) < self.yari_cap + 60:
                oyuncu.hasar_al(self.hasar * 3)
                efektler.append(("sarsinti", 0.5))

        elif self.ozel_saldiri == "zehir_yagmuru" and zehir_havuzlari is not None:
            # 6 yönde zehir gönderir
            for i in range(6):
                a = math.radians(i * 60)
                for mesafe in range(40, 160, 40):
                    px = self.x + math.cos(a) * mesafe
                    py = self.y + math.sin(a) * mesafe
                    zehir_havuzlari.append([px, py, 20, 3.5, 3.5])
                efektler.append(("parcacik_patlama", (self.x, self.y, (50, 220, 80))))

        elif self.ozel_saldiri == "elektrik_dalgasi":
            # Herkese yakın olan oyuncuya şok hasarı
            import math
            uzak = math.hypot(oyuncu.x - self.x, oyuncu.y - self.y)
            if uzak < 200:
                hasar = int(80 * (1.0 - uzak / 200))
                oyuncu.hasar_al(hasar)
            efektler.append(("elektrik_dalgasi", (self.x, self.y)))
            efektler.append(("sarsinti", 0.3))

        elif self.ozel_saldiri == "alev_cemberi":
            # Etrafında dönen 8 alev noktası - zehir havuzu gibi hasar verir
            for i in range(8):
                a = math.radians(i * 45)
                px = self.x + math.cos(a) * (self.yari_cap + 30)
                py = self.y + math.sin(a) * (self.yari_cap + 30)
                if zehir_havuzlari is not None:
                    zehir_havuzlari.append([px, py, 15, 2.0, 10.0])  # Alev havuzu
                efektler.append(("parcacik_patlama", (px, py, (255, 120, 0))))

        return efektler

    def oyuncuya_yakin_mi(self, ox, oy):
        return math.hypot(ox - self.x, oy - self.y) < (self.yari_cap + 18)

    def patlama_hasar_mesafe(self, ox, oy):
        return math.hypot(ox - self.x, oy - self.y)

    def drop_olustur(self):
        from varliklar.drop import Drop
        # Boss her zaman can ve para dropar, ekstra %50 şans
        droplar = [Drop(self.x, self.y, "can"), Drop(self.x + 20, self.y, "mermi")]
        return droplar

    def can_bar_ciz(self, ekran, genislik, yukseklik, font):
        """Ekranın üstüne tam boss can barı çiz."""
        bar_gen = genislik - 100
        bar_yuk = 22
        bar_x = 50
        bar_y = 14

        # Arkaplan
        pygame.draw.rect(ekran, (20, 0, 0), (bar_x - 2, bar_y - 2, bar_gen + 4, bar_yuk + 4),
                         border_radius=6)
        pygame.draw.rect(ekran, (60, 0, 0), (bar_x, bar_y, bar_gen, bar_yuk), border_radius=5)

        # Doluluk
        oran = max(0, self.can / self.max_can)
        dolu = int(bar_gen * oran)
        # Fazlara göre renk
        if self.faz == 3:
            bar_renk = (255, 30, 30)
        elif self.faz == 2:
            bar_renk = (255, 140, 20)
        else:
            bar_renk = (180, 50, 50)

        if dolu > 0:
            pygame.draw.rect(ekran, bar_renk, (bar_x, bar_y, dolu, bar_yuk), border_radius=5)

        # Faz çizgileri
        for yuzde in [0.25, 0.50]:
            ix = bar_x + int(bar_gen * yuzde)
            pygame.draw.line(ekran, (255, 255, 255), (ix, bar_y), (ix, bar_y + bar_yuk), 2)

        # İsim + can
        isim_surf = font.render(f"☠ {self.isim}  FAZ {self.faz}", True, (255, 200, 50))
        ekran.blit(isim_surf, (bar_x, bar_y + bar_yuk + 3))

        # Çerçeve
        pygame.draw.rect(ekran, (200, 150, 0), (bar_x - 2, bar_y - 2, bar_gen + 4, bar_yuk + 4),
                         2, border_radius=6)

    @staticmethod
    def dalga_icin_boss_sec(dalga_no):
        """Dalga numarasına göre boss tipi seçer."""
        idx = (dalga_no // 5 - 1) % len(BOSS_SIRASI)
        return BOSS_SIRASI[idx]

    @staticmethod
    def kenar_spawn(ekran_w, ekran_h, boss_tipi="et_gobegi"):
        kenar = random.randint(0, 3)
        off = 120
        if kenar == 0:   x, y = ekran_w // 2, -off
        elif kenar == 1: x, y = ekran_w + off, ekran_h // 2
        elif kenar == 2: x, y = ekran_w // 2, ekran_h + off
        else:            x, y = -off, ekran_h // 2
        return Boss(x, y, boss_tipi)
