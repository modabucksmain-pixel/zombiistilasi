# ============================================================
#  varliklar/oyuncu.py — Nişangah Konisi (Aim Cone) ve Şarjör
# ============================================================
import pygame
import math
import random
from ayarlar import (
    OYUNCU_HIZ, OYUNCU_SPRINT_CARPAN, OYUNCU_STAMINA, OYUNCU_STAMINA_HARCAMA,
    OYUNCU_STAMINA_REGEN, OYUNCU_BASLANGIC_CAN, OYUNCU_YARI_CAP,
    OYUNCU_HASAR_GECIKME, OYUNCU_HASAR_FLASH, OYUNCU_BASLANGIC_KALKAN,
    OYUNCU_KALKAN_REGEN, OYUNCU_KALKAN_GECIKME, ULTIMATE_COOLDOWN,
    MAVI, BEYAZ, SILAHLAR, ZIRH_MAVI, SARI
)
from varliklar.mermi import Mermi
from sistemler.ses_sistemi import ses_sis

ZORLUK_CARPANI = 1.0

class Oyuncu(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.yari_cap = OYUNCU_YARI_CAP
        
        self.stamina = float(OYUNCU_STAMINA)
        self.max_stamina = float(OYUNCU_STAMINA)
        self.yoruldu_mu = False
        
        self.can = float(OYUNCU_BASLANGIC_CAN)
        self.max_can = float(OYUNCU_BASLANGIC_CAN)
        
        self.kalkan = float(OYUNCU_BASLANGIC_KALKAN)
        self.max_kalkan = float(OYUNCU_BASLANGIC_KALKAN)
        self.kalkan_yenilenme_sayaci = 0.0
        
        self.aci = 0.0
        self.ates_sayac = 0.0
        self.hasar_sayac = 0.0
        self.hasarli_sayac = 0.0
        self.oldu = False

        self.envanter = ["tabanca"]
        self.aktif_silah = "tabanca"
        self.mermiler = {"tabanca": -1}

        self.yukseltmeler = {
            "can": 0, "stamina": 0, "hiz": 0, "hasar": 0, 
            "kalkan": 0, "zirh": 0, "ult_cd": 0, "combo": 0, "mermi": 0
        }
        self.ult_bekleme = 0.0
        
        self.durbunler = ["red_dot"] # Varsayılan olarak Red Dot olsun
        self.aktif_durbun = "red_dot"
        self.guncel_zoom = 1.0
        self.recoil = 0.0
        self.guncel_yayilma = 0.0
        self.silah_sprite = None

        self._image_olustur()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _image_olustur(self):
        boyut = self.yari_cap * 2 + 10
        self.image = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        cx = cy = boyut // 2
        pygame.draw.circle(self.image, (0, 0, 0, 80), (cx + 3, cy + 3), self.yari_cap)
        pygame.draw.circle(self.image, MAVI, (cx, cy), self.yari_cap)
        pygame.draw.circle(self.image, (120, 180, 255), (cx, cy), self.yari_cap - 6)
        self._base_image = self.image.copy()
        self._silah_sprite_guncelle()

    def _silah_sprite_guncelle(self):
        """Aktif silaha göre oyuncunun elindeki silahın 2D görünümünü üret."""
        veri = self.silah_verisi
        tip = veri.get("tip", "normal")
        renk = veri.get("renk", BEYAZ)

        govde_uz = self.yari_cap + 12
        govde_yuk = 6

        if tip in ("roket", "seken_bomba", "delici_patlayan"):
            govde_uz, govde_yuk = self.yari_cap + 18, 9
        elif tip == "alev":
            govde_uz, govde_yuk = self.yari_cap + 14, 8
        elif tip == "delici":
            govde_uz, govde_yuk = self.yari_cap + 20, 5

        silah = pygame.Surface((govde_uz + 12, max(20, govde_yuk + 12)), pygame.SRCALPHA)
        merkez_y = silah.get_height() // 2

        # Namlu ve gövde
        pygame.draw.rect(silah, (25, 25, 35), (2, merkez_y - govde_yuk // 2, govde_uz, govde_yuk), border_radius=3)
        pygame.draw.rect(
            silah,
            (max(0, renk[0] - 40), max(0, renk[1] - 40), max(0, renk[2] - 40)),
            (2 + govde_uz // 3, merkez_y - govde_yuk // 2, govde_uz // 2, govde_yuk),
            border_radius=3
        )
        pygame.draw.circle(silah, renk, (govde_uz + 4, merkez_y), max(2, govde_yuk // 2))

        # Özel silah eki
        if tip == "alev":
            pygame.draw.circle(silah, (255, 120, 0, 160), (govde_uz + 7, merkez_y), govde_yuk + 2)
        elif tip in ("roket", "seken_bomba", "delici_patlayan"):
            pygame.draw.polygon(
                silah,
                (90, 90, 100),
                [(4, merkez_y), (0, merkez_y - 4), (0, merkez_y + 4)]
            )
        elif tip == "delici":
            pygame.draw.line(silah, (180, 220, 255), (govde_uz - 6, merkez_y), (govde_uz + 10, merkez_y), 1)

        self.silah_sprite = silah

    @property
    def gercek_hiz(self): return OYUNCU_HIZ + self.yukseltmeler["hiz"] * 30
    @property
    def hasar_carpani(self): return 1.0 + self.yukseltmeler["hasar"] * 0.30
    @property
    def zirh_carpani(self): return max(0.2, 1.0 - self.yukseltmeler["zirh"] * 0.12) * ZORLUK_CARPANI
    @property
    def max_kalkan_degeri(self): return self.max_kalkan + self.yukseltmeler["kalkan"] * 40
    @property
    def max_stamina_degeri(self): return self.max_stamina + self.yukseltmeler["stamina"] * 30
    @property
    def ult_max_cd(self): return max(5.0, ULTIMATE_COOLDOWN - self.yukseltmeler["ult_cd"] * 2.0)
    @property
    def silah_verisi(self): return SILAHLAR[self.aktif_silah]
    @property
    def hareket_ediyor_mu(self): return getattr(self, "_son_hareket", False)

    def _silah_max_mermi(self, s_key):
        b = SILAHLAR[s_key]["kapasite"]
        if b == -1: return -1
        return int(b * (1.0 + self.yukseltmeler["mermi"] * 0.2))

    def silah_al(self, silah_key):
        if silah_key not in self.envanter:
            self.envanter.append(silah_key)
            self.mermiler[silah_key] = self._silah_max_mermi(silah_key)
        self.aktif_silah = silah_key
        self._silah_sprite_guncelle()

    def silah_degistir(self, silah_key):
        if silah_key in self.envanter:
            self.aktif_silah = silah_key
            self._silah_sprite_guncelle()

    def mermileri_fulle(self):
        for s in self.envanter:
            if s != "tabanca":
                self.mermiler[s] = self._silah_max_mermi(s)

    def aktif_mermi_doldur(self):
        ak = self.aktif_silah
        if ak != "tabanca":
            max_m = self._silah_max_mermi(ak)
            self.mermiler[ak] = min(max_m, self.mermiler[ak] + max_m // 2)

    def siradaki_silah(self, yon=1):
        if not self.envanter: return
        idx = self.envanter.index(self.aktif_silah) if self.aktif_silah in self.envanter else 0
        self.aktif_silah = self.envanter[(idx + yon) % len(self.envanter)]
        self._silah_sprite_guncelle()

    def update(self, dt, tuslar, fare_pos, mermiler, ekran_w, ekran_h, serbest_bakis=False, hareket_cozucu=None):
        sprint = tuslar.get("sprint", False)
        nisan = tuslar.get("nisan", False)
        
        # Yayılma ve Nişan Mekaniği
        from ayarlar import DURBUNLER
        hedef_yayilma = self.silah_verisi["yayilma"]

        if nisan:
            hiz_carpani = 0.4
            d_veri = DURBUNLER.get(self.aktif_durbun, {"zoom": 1.0})
            self.guncel_zoom = d_veri["zoom"]
            hedef_yayilma = self.silah_verisi["yayilma"] * (0.2 / self.guncel_zoom)
        elif sprint and self.stamina > 0 and not self.yoruldu_mu:
            self.stamina -= OYUNCU_STAMINA_HARCAMA * dt
            if self.stamina <= 0:
                self.stamina = 0
                self.yoruldu_mu = True
            hiz_carpani = OYUNCU_SPRINT_CARPAN
            hedef_yayilma = self.silah_verisi["yayilma"] * 2.5 
            self.guncel_zoom = 1.0
        else:
            hiz_carpani = 1.0
            self.stamina = min(self.max_stamina_degeri, self.stamina + OYUNCU_STAMINA_REGEN * dt)
            if self.stamina > 25:
                self.yoruldu_mu = False
            self.guncel_zoom = 1.0
            if self.hareket_ediyor_mu:
                hedef_yayilma = self.silah_verisi["yayilma"] * 1.5

        # Recoil ekle ve yumuşak geçiş sağla (Sync Cone)
        hedef_yayilma += self.recoil
        self.guncel_yayilma += (hedef_yayilma - self.guncel_yayilma) * 15.0 * dt
        
        # Recoil'in zamanla azalması (Soğuma)
        self.recoil = max(0.0, self.recoil - (10.0 + self.recoil * 3.0) * dt)
        
        # 3D modunda hareket oyuncunun baktığı yöne göre olmalı!
        if serbest_bakis:
            self._hareket_3d(dt, tuslar, ekran_w, ekran_h, hiz_carpani, hareket_cozucu)
        else:
            self._hareket(dt, tuslar, ekran_w, ekran_h, hiz_carpani, hareket_cozucu)
            
        self._don(fare_pos, serbest_bakis)
        
        if self.ates_sayac > 0: self.ates_sayac -= dt
        if self.hasar_sayac > 0: self.hasar_sayac -= dt
        if self.hasarli_sayac > 0: self.hasarli_sayac -= dt
        if self.ult_bekleme > 0: self.ult_bekleme -= dt
        
        if self.kalkan_yenilenme_sayaci > 0:
            self.kalkan_yenilenme_sayaci -= dt
        elif self.kalkan < self.max_kalkan_degeri:
            self.kalkan = min(self.max_kalkan_degeri, self.kalkan + OYUNCU_KALKAN_REGEN * dt)

        if tuslar.get("ates") and self.ates_sayac <= 0:
            mevcut_mermi = self.mermiler.get(self.aktif_silah, -1)
            if mevcut_mermi > 0 or mevcut_mermi == -1:
                self._ates(mermiler)
            else:
                self.siradaki_silah()
            
        if tuslar.get("ult") and self.ult_bekleme <= 0:
            self._ultimate_kullan(mermiler)

    def _hareket(self, dt, tuslar, ekran_w, ekran_h, hiz_carpani, hareket_cozucu=None):
        dx = dy = 0
        if tuslar.get("yukari"):  dy -= 1
        if tuslar.get("asagi"):   dy += 1
        if tuslar.get("sol"):     dx -= 1
        if tuslar.get("sag"):     dx += 1
        if dx != 0 and dy != 0:
            dx *= 0.7071; dy *= 0.7071
        v = self.gercek_hiz * hiz_carpani
        yeni_x = self.x + dx * v * dt
        yeni_y = self.y + dy * v * dt
        self._son_hareket = (dx != 0 or dy != 0)
        yeni_x = max(self.yari_cap, min(ekran_w - self.yari_cap, yeni_x))
        yeni_y = max(self.yari_cap, min(ekran_h - self.yari_cap, yeni_y))
        if hareket_cozucu:
            yeni_x, yeni_y = hareket_cozucu(self.x, self.y, yeni_x, yeni_y, self.yari_cap)
        self.x, self.y = yeni_x, yeni_y

    def _hareket_3d(self, dt, tuslar, ekran_w, ekran_h, hiz_carpani, hareket_cozucu=None):
        # 3D Hareket: Baktığı yöne göre ileri/geri ve sağa/sola strafe
        aci_rad = math.radians(self.aci)
        v = self.gercek_hiz * hiz_carpani
        
        dx = dy = 0
        if tuslar.get("yukari"):
            dx += math.cos(aci_rad)
            dy += math.sin(aci_rad)
        if tuslar.get("asagi"):
            dx -= math.cos(aci_rad)
            dy -= math.sin(aci_rad)
        if tuslar.get("sol"):
            dx += math.sin(aci_rad)
            dy -= math.cos(aci_rad)
        if tuslar.get("sag"):
            dx -= math.sin(aci_rad)
            dy += math.cos(aci_rad)
            
        if dx != 0 or dy != 0:
            # Normalize movement vector
            mag = math.hypot(dx, dy)
            dx /= mag
            dy /= mag
            
        yeni_x = self.x + dx * v * dt
        yeni_y = self.y + dy * v * dt
        self._son_hareket = (dx != 0 or dy != 0)
        yeni_x = max(self.yari_cap, min(ekran_w - self.yari_cap, yeni_x))
        yeni_y = max(self.yari_cap, min(ekran_h - self.yari_cap, yeni_y))
        if hareket_cozucu:
            yeni_x, yeni_y = hareket_cozucu(self.x, self.y, yeni_x, yeni_y, self.yari_cap)
        self.x, self.y = yeni_x, yeni_y

    def _don(self, fare_pos, serbest_bakis=False):
        if not serbest_bakis:
            dx = fare_pos[0] - self.x
            dy = fare_pos[1] - self.y
            self.aci = math.degrees(math.atan2(dy, dx))
        
        img = self._base_image.copy()
        if self.silah_sprite:
            silah_y = img.get_height() // 2 - self.silah_sprite.get_height() // 2
            img.blit(self.silah_sprite, (img.get_width() // 2 - 2, silah_y))
        if self.kalkan > 0:
            alpha = int(100 * (self.kalkan / self.max_kalkan_degeri))
            hale = pygame.Surface((img.get_width(), img.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(hale, (*ZIRH_MAVI, alpha), (img.get_width()//2, img.get_height()//2), self.yari_cap + 4, 4)
            img.blit(hale, (0, 0))
        self.image = pygame.transform.rotate(img, -self.aci)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def ciz_nisangah(self, ekran, fare_pos, ox=0, oy=0):
        # Koni her zaman aktif, silahın ve hareketin durumuna göre dinamik değişecek
        veri = self.silah_verisi
        yayilma = getattr(self, "guncel_yayilma", veri["yayilma"])
        tip = veri.get("tip", "normal")
        uzunluk = min(1400, veri["mermi_hizi"])
        if tip == "alev":
            uzunluk = min(500, veri["mermi_hizi"] + 120)
        elif tip in ("roket", "seken_bomba", "delici_patlayan"):
            uzunluk = min(900, veri["mermi_hizi"] + 250)
        elif tip == "delici":
            uzunluk = min(1600, veri["mermi_hizi"] + 300)
        
        merkez_x = self.x + ox
        merkez_y = self.y + oy
        
        # Namlu ucunun (gun barrel) konumu
        namlu_x = merkez_x + math.cos(math.radians(self.aci)) * (self.yari_cap + 12)
        namlu_y = merkez_y + math.sin(math.radians(self.aci)) * (self.yari_cap + 12)
        
        koni_alpha = 28
        cizgi_alpha = 80
        if tip == "alev":
            koni_alpha = 55
        elif tip in ("roket", "seken_bomba", "delici_patlayan"):
            koni_alpha = 35
        elif tip == "delici":
            cizgi_alpha = 120

        # Eğer yayılma yoksa veya nişan alınıyorsa tek bir ince lazer çizgisi çiz
        if yayilma < 1.0:
            dx = math.cos(math.radians(self.aci)) * uzunluk
            dy = math.sin(math.radians(self.aci)) * uzunluk
            pygame.draw.line(ekran, (*veri["renk"], 160), (namlu_x, namlu_y), (namlu_x + dx, namlu_y + dy), 2)
        else:
            # Yayılma açısına göre yarı saydam bir üçgen/koni oluştur
            # Performans için özel bir Surface
            koni_s = pygame.Surface((uzunluk*2, uzunluk*2), pygame.SRCALPHA)
            cx, cy = uzunluk, uzunluk
            
            aci1 = math.radians(self.aci - yayilma/2)
            aci2 = math.radians(self.aci + yayilma/2)
            
            p1 = (cx, cy)
            p2 = (cx + math.cos(aci1)*uzunluk, cy + math.sin(aci1)*uzunluk)
            p3 = (cx + math.cos(aci2)*uzunluk, cy + math.sin(aci2)*uzunluk)
            
            pygame.draw.polygon(koni_s, (*veri["renk"], koni_alpha), [p1, p2, p3])
            
            # Koni kenarları
            pygame.draw.line(koni_s, (*veri["renk"], cizgi_alpha), p1, p2, 1)
            pygame.draw.line(koni_s, (*veri["renk"], cizgi_alpha), p1, p3, 1)
            
            ekran.blit(koni_s, (int(namlu_x - cx), int(namlu_y - cy)))

        # Namlu merkezine ufak hedef noktası
        pygame.draw.circle(ekran, veri["renk"], (int(namlu_x), int(namlu_y)), 2)

    def _ates(self, mermiler):
        veri = self.silah_verisi
        adeti = veri["mermi_adeti"]
        yayilma = getattr(self, "guncel_yayilma", veri["yayilma"])
        if self.aktif_silah != "tabanca":
            self.mermiler[self.aktif_silah] -= 1
            
        # Mermilerin çıkış noktası (Namlunun ucu)
        namlu_x = self.x + math.cos(math.radians(self.aci)) * (self.yari_cap + 12)
        namlu_y = self.y + math.sin(math.radians(self.aci)) * (self.yari_cap + 12)
            
        for i in range(adeti):
            # Artık tek mermi de olsa yayılma (recoil/hareket) etki ediyor
            aci_offset = random.uniform(-yayilma / 2, yayilma / 2)
            m = Mermi(namlu_x, namlu_y, self.aci + aci_offset, veri, self.hasar_carpani)
            mermiler.add(m)
            
        self.ates_sayac = veri["ates_hizi"]
        
        # Silaha göre Recoil (Geri tepme) ekle
        self.recoil += veri["yayilma"] * 0.8 + 2.0
        self.recoil = min(self.recoil, 45.0) # Maksimum recoil sınırı
        
        # Silah sesini tipine göre seç (Profesyonel Mapping)
        ses_anahtar = "ates"
        if "ak47" in self.aktif_silah:    ses_anahtar = "ates_ak"
        elif "smg" in self.aktif_silah or "minigun" in self.aktif_silah: ses_anahtar = "ates_smg"
        elif "shotgun" in self.aktif_silah: ses_anahtar = "ates_pom"
        elif "sniper" in self.aktif_silah:  ses_anahtar = "ates_sni"
        elif "lazer" in self.aktif_silah or "plazma" in self.aktif_silah: ses_anahtar = "ates_laz"
        elif "alev" in self.aktif_silah:   ses_anahtar = "ates_ale"
        elif "bomba" in self.aktif_silah or "roket" in self.aktif_silah: ses_anahtar = "ates_pat"
        
        ses_sis.oynat(ses_anahtar)

    def _ultimate_kullan(self, mermiler):
        self.ult_bekleme = self.ult_max_cd
        veri = SILAHLAR["roket_ateş"].copy() if "roket_ateş" in SILAHLAR else SILAHLAR["tabanca"].copy()
        veri["mermi_hizi"] = 700
        veri["tip"] = "delici_patlayan"
        veri["hasar"] = 200
        veri["renk"] = SARI
        veri["patlama_r"] = 120
        veri["efekt"] = "yanma"
        for i in range(16):
            aci = i * 22.5
            m = Mermi(self.x, self.y, aci, veri, self.hasar_carpani * 2.0)
            mermiler.add(m)

    def hasar_al(self, miktar):
        gercek = miktar * self.zirh_carpani
        if self.kalkan > 0:
            if self.kalkan >= gercek:
                self.kalkan -= gercek
                gercek = 0
            else:
                gercek -= self.kalkan
                self.kalkan = 0
        if gercek > 0:
            self.can -= gercek
            ses_sis.oynat("hasar")
            
        self.hasarli_sayac = OYUNCU_HASAR_FLASH
        self.kalkan_yenilenme_sayaci = OYUNCU_KALKAN_GECIKME
        if self.can <= 0:
            self.can = 0
            self.oldu = True

    def zombi_temas(self, dt, miktar):
        if self.hasar_sayac <= 0:
            self.hasar_al(miktar)
            self.hasar_sayac = 0.15

    def can_doldur(self, miktar=40):
        self.can = min(self.max_can + self.yukseltmeler["can"]*40, self.can + miktar)

    def kalkan_doldur(self, miktar=50):
        self.kalkan = min(self.max_kalkan_degeri, self.kalkan + miktar)

    def flash_ciz(self, ekran):
        if self.hasarli_sayac > 0:
            alpha = int(180 * (self.hasarli_sayac / OYUNCU_HASAR_FLASH))
            flash = pygame.Surface(ekran.get_size(), pygame.SRCALPHA)
            flash.fill((255, 0, 0, alpha) if self.kalkan <= 0 else (100, 150, 255, alpha))
            ekran.blit(flash, (0, 0))
            
        oran = self.can / (self.max_can + self.yukseltmeler["can"]*40)
        if oran < 0.35:
            alpha = int(255 * (1.0 - oran/0.35)) * abs(math.sin(pygame.time.get_ticks() / 150))
            vignette = pygame.Surface(ekran.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(vignette, (255, 0, 0, int(alpha*0.4)), vignette.get_rect(), 40)
            ekran.blit(vignette, (0, 0))
