import pygame
import math
from ayarlar import GENISLIK, YUKSEKLIK, SIYAH, ARKAPLAN, YESIL

class Raycaster:
    def __init__(self, ekran):
        self.ekran = ekran
        self.res = 1
        self.fov = 75
        self.max_derinlik = 1500
        self.duvar_yuksekligi = 50000
        self.sway_x = 0
        self.sway_y = 0
        self.sway_time = 0
        
        # FPS Modu (Kamera oyuncu ile aynı noktada)
        self.tps_offset = 0
        self.side_offset = 0

    def ciz(self, oyuncu, zombiler, mermiler, droplar, harita_veri=None):
        # ZOOM Mekaniği (Dürbün)
        zoom_seviyesi = oyuncu.guncel_zoom if hasattr(oyuncu, "guncel_zoom") else 1.0
        guncel_fov = 75.0 / zoom_seviyesi
        # 1. Atmosferik Gece Arkaplanı
        self.ekran.fill((5, 5, 10))
        for y in range(0, YUKSEKLIK // 2, 3):
            ton = min(70, 10 + int((y / (YUKSEKLIK // 2)) * 60))
            pygame.draw.line(self.ekran, (5 + ton // 3, 8 + ton // 4, 20 + ton), (0, y), (GENISLIK, y))
        for i in range(150):
            pygame.draw.circle(self.ekran, (200, 200, 255), (int(i*137)%GENISLIK, int(i*89)%(YUKSEKLIK//2)), 1)
        
        # Ay ve Ufuk
        pygame.draw.circle(self.ekran, (240, 240, 255), (GENISLIK - 200, 150), 40)
        pygame.draw.circle(self.ekran, (5, 5, 10), (GENISLIK - 180, 150), 35)
        
        pygame.draw.rect(self.ekran, (2, 2, 5), (0, YUKSEKLIK//2 - 20, GENISLIK, 20)) # Ufuk

        # Zemin
        for i in range(0, YUKSEKLIK // 2, 4):
            v = int(10 + (i / (YUKSEKLIK/2)) * 30)
            pygame.draw.rect(self.ekran, (v, v, v + 5), (0, YUKSEKLIK // 2 + i, GENISLIK, 4))
        for i in range(1, 18):
            y = YUKSEKLIK // 2 + int((i / 18) ** 1.7 * (YUKSEKLIK // 2))
            pygame.draw.line(self.ekran, (20, 20, 24), (0, y), (GENISLIK, y), 1)

        if harita_veri:
            self._ciz_harita_engelleri_3d(oyuncu, harita_veri, zoom_seviyesi)

        # 2. Nesneleri Çiz (Billboard)
        nesneler = []
        for z in zombiler:
            dist = math.hypot(z.x - oyuncu.x, z.y - oyuncu.y)
            if dist < self.max_derinlik: nesneler.append(("zombi", z, dist))
        for m in mermiler:
            dist = math.hypot(m.x - oyuncu.x, m.y - oyuncu.y)
            if dist < self.max_derinlik: nesneler.append(("mermi", m, dist))
        for d in droplar:
            dist = math.hypot(d.x - oyuncu.x, d.y - oyuncu.y)
            if dist < self.max_derinlik: nesneler.append(("drop", d, dist))

        nesneler.sort(key=lambda x: x[2], reverse=True)

        for tip, obj, dist in nesneler:
            rel_aci = math.atan2(obj.y - oyuncu.y, obj.x - oyuncu.x) - math.radians(oyuncu.aci)
            while rel_aci > math.pi: rel_aci -= 2 * math.pi
            while rel_aci < -math.pi: rel_aci += 2 * math.pi
            
            if abs(rel_aci) < math.radians(guncel_fov):
                ekran_x = (0.5 * (rel_aci / math.radians(guncel_fov / 2)) + 0.5) * GENISLIK
                # Zoom mesafeyi algısal olarak kısaltır (Büyütür)
                proj_yuk = (self.duvar_yuksekligi / (max(5.0, dist))) * zoom_seviyesi
                
                if tip == "zombi":
                    img = obj.image
                    # Maksimum boyut sınırı (Ekranın 4 katından büyük olmasın)
                    img_w = min(GENISLIK * 4, int(img.get_width() * (proj_yuk / 100)))
                    img_h = min(YUKSEKLIK * 4, int(img.get_height() * (proj_yuk / 100)))
                    
                    if img_w > 5 and img_h > 5:
                        scaled = pygame.transform.scale(img, (img_w, img_h))
                        self.ekran.blit(scaled, (ekran_x - img_w // 2, YUKSEKLIK // 2 - img_h // 2))
                elif tip == "mermi":
                    size = max(2, int(2000 / (dist + 1)))
                    pygame.draw.circle(self.ekran, obj.renk, (int(ekran_x), YUKSEKLIK // 2), size)
                elif tip == "drop":
                    img = obj.image
                    img_w = int(img.get_width() * (proj_yuk / 80))
                    img_h = int(img.get_height() * (proj_yuk / 80))
                    if img_w > 0 and img_h > 0:
                        scaled = pygame.transform.scale(img, (img_w, img_h))
                        self.ekran.blit(scaled, (ekran_x - img_w // 2, YUKSEKLIK // 2 + 20))

        # 3. FPS Silah ve Eller (POV)
        self._ciz_pov_silah(oyuncu, zoom_seviyesi)
        
        # 4. Dürbün Overlay (Eğer Zoom varsa)
        if zoom_seviyesi > 1.1:
            self._ciz_durbun_overlay(zoom_seviyesi)

    def _ciz_harita_engelleri_3d(self, oyuncu, harita_veri, zoom):
        duvarlar = []
        for rect in harita_veri.get("engeller", []):
            cx, cy = rect.centerx, rect.centery
            dist = math.hypot(cx - oyuncu.x, cy - oyuncu.y)
            if dist > self.max_derinlik:
                continue
            duvarlar.append((dist, rect))
        duvarlar.sort(reverse=True, key=lambda x: x[0])

        guncel_fov = 75.0 / max(1.0, zoom)
        for dist, rect in duvarlar:
            rel_aci = math.atan2(rect.centery - oyuncu.y, rect.centerx - oyuncu.x) - math.radians(oyuncu.aci)
            while rel_aci > math.pi:
                rel_aci -= 2 * math.pi
            while rel_aci < -math.pi:
                rel_aci += 2 * math.pi
            if abs(rel_aci) > math.radians(guncel_fov):
                continue

            ekran_x = (0.5 * (rel_aci / math.radians(guncel_fov / 2)) + 0.5) * GENISLIK
            boy = int(max(80, min(YUKSEKLIK * 1.1, 70000 / (dist + 1))))
            en = int(max(18, min(GENISLIK * 0.5, rect.width * 650 / (dist + 80))))
            y = YUKSEKLIK // 2 - boy // 2
            renk = (38, 38, 46)
            pygame.draw.rect(self.ekran, renk, (ekran_x - en // 2, y, en, boy), border_radius=4)
            pygame.draw.rect(self.ekran, (70, 70, 85), (ekran_x - en // 2, y, en, boy), 2, border_radius=4)

    def _ciz_durbun_overlay(self, zoom):
        # Siyah kenarlar (Scope Mask)
        mask = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
        pygame.draw.rect(mask, (0, 0, 0, 255), (0, 0, GENISLIK, YUKSEKLIK))
        
        # Ortadaki delik (Scope lens)
        r = int(YUKSEKLIK * 0.4)
        pygame.draw.circle(mask, (0, 0, 0, 0), (GENISLIK // 2, YUKSEKLIK // 2), r)
        self.ekran.blit(mask, (0, 0))
        
        # Dürbün Kıl Çizgileri
        pygame.draw.circle(self.ekran, (0, 0, 0), (GENISLIK // 2, YUKSEKLIK // 2), r, 8)
        pygame.draw.line(self.ekran, (0, 0, 0), (GENISLIK // 2 - r, YUKSEKLIK // 2), (GENISLIK // 2 + r, YUKSEKLIK // 2), 4)
        pygame.draw.line(self.ekran, (0, 0, 0), (GENISLIK // 2, YUKSEKLIK // 2 - r), (GENISLIK // 2, YUKSEKLIK // 2 + r), 4)
        
        # Zoom Yazısı
        font = pygame.font.SysFont("Arial", 24, bold=True)
        txt = font.render(f"{zoom:.0f}X", True, (255, 255, 255))
        self.ekran.blit(txt, (GENISLIK // 2 - txt.get_width() // 2, YUKSEKLIK // 2 + r + 20))

    def _ciz_pov_silah(self, oyuncu, zoom=1.0):
        # Zoom yaparken silahı aşağı çek (Daha gerçekçi)
        zoom_offset = (zoom - 1.0) * 150
        
        silah_v = oyuncu.silah_verisi
        renk = silah_v["renk"]

        if oyuncu.hareket_ediyor_mu:
            self.sway_time += 0.15
            self.sway_x = math.sin(self.sway_time) * 20
            self.sway_y = abs(math.cos(self.sway_time)) * 15
        else:
            self.sway_x *= 0.9
            self.sway_y *= 0.9

        # FPS Silah Render
        s_gen, s_yuk = 500, 500
        silah_surf = pygame.Surface((s_gen, s_yuk), pygame.SRCALPHA)
        
        # Eller (POV)
        pygame.draw.ellipse(silah_surf, (80, 60, 50), (-50, 350, 200, 300)) # Sol el
        pygame.draw.ellipse(silah_surf, (80, 60, 50), (350, 350, 200, 300)) # Sağ el

        # Silah Gövdesi
        pygame.draw.rect(silah_surf, (20, 20, 25), (150, 250, 200, 250), border_radius=10)
        pygame.draw.rect(silah_surf, (10, 10, 12), (210, 50, 80, 250), border_radius=5)
        
        # Glow
        recoil = (oyuncu.ates_sayac / silah_v["ates_hizi"]) * 50 if oyuncu.ates_sayac > 0 else 0
        pygame.draw.circle(silah_surf, (*renk, 150 if recoil > 0 else 50), (250, 250), 60)
        
        pos_x = GENISLIK // 2 - s_gen // 2 + self.sway_x
        pos_y = YUKSEKLIK - s_yuk + 100 + self.sway_y + recoil + zoom_offset
        self.ekran.blit(silah_surf, (pos_x, pos_y))
        
        # Nişangah (Tam Merkez - Mermiler Buraya Gider)
        pygame.draw.circle(self.ekran, (255, 255, 255, 180), (GENISLIK // 2, YUKSEKLIK // 2), 4)
        pygame.draw.line(self.ekran, YESIL, (GENISLIK // 2 - 15, YUKSEKLIK // 2), (GENISLIK // 2 + 15, YUKSEKLIK // 2), 2)
        pygame.draw.line(self.ekran, YESIL, (GENISLIK // 2, YUKSEKLIK // 2 - 15), (GENISLIK // 2, YUKSEKLIK // 2 + 15), 2)
