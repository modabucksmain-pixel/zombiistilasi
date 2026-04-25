# ============================================================
#  ekranlar/meta_ekran.py — Roguelite Meta Upgrade Menüsü
#  Run sonunda "Kan Kristali" ile kalıcı güçlenmeler satın al.
# ============================================================
import pygame
from sistemler.meta_progression import meta_sis, META_UPGRADELER
from ayarlar import BEYAZ, SIYAH, SARI, YESIL, KIRMIZI, MOR, ALTIN


class MetaEkran:
    def __init__(self):
        self.font_buyuk = pygame.font.SysFont("Consolas", 36, bold=True)
        self.font_orta  = pygame.font.SysFont("Consolas", 20, bold=True)
        self.font_kucuk = pygame.font.SysFont("Consolas", 15)
        self.secili_idx = 0
        self.kaydirma   = 0
        self._kazanilan_kristal = 0
        self._kazanilan_gosterim_sure = 3.0

    def baslat(self, kazanilan_kristal=0):
        self._kazanilan_kristal = kazanilan_kristal
        self._kazanilan_gosterim_sure = 3.0

    def tik_isle(self, event, genislik, yukseklik):
        """Return 'devam' veya None."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return "devam"
            elif event.key == pygame.K_UP:
                self.secili_idx = max(0, self.secili_idx - 1)
            elif event.key == pygame.K_DOWN:
                self.secili_idx = min(len(META_UPGRADELER) - 1, self.secili_idx + 1)
            elif event.key == pygame.K_SPACE or event.key == pygame.K_e:
                key = list(META_UPGRADELER.keys())[self.secili_idx]
                meta_sis.satin_al(key)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Butonlara tıklama
                my = event.pos[1]
                baslangic_y = 160
                satir_yuk = 72
                for i, key in enumerate(META_UPGRADELER.keys()):
                    satir_y = baslangic_y + i * satir_yuk - self.kaydirma
                    if satir_y < 80 or satir_y > yukseklik - 80:
                        continue
                    satin_al_x = genislik - 160
                    if satin_al_x <= event.pos[0] <= satin_al_x + 140 and satir_y <= my <= satir_y + 60:
                        self.secili_idx = i
                        meta_sis.satin_al(key)
                        break
                # Devam butonu
                devam_x = genislik // 2 - 100
                devam_y = yukseklik - 70
                if devam_x <= event.pos[0] <= devam_x + 200 and devam_y <= my <= devam_y + 50:
                    return "devam"

            elif event.button == 4:
                self.kaydirma = max(0, self.kaydirma - 20)
            elif event.button == 5:
                self.kaydirma = min(
                    max(0, len(META_UPGRADELER) * 72 - 400),
                    self.kaydirma + 20
                )
        return None

    def guncelle(self, dt):
        if self._kazanilan_gosterim_sure > 0:
            self._kazanilan_gosterim_sure -= dt

    def ciz(self, ekran, genislik, yukseklik):
        # Arkaplan
        ekran.fill((8, 5, 18))

        # Başlık
        baslik = self.font_buyuk.render("💎 META GELİŞTİRMELER", True, (180, 100, 255))
        ekran.blit(baslik, (genislik // 2 - baslik.get_width() // 2, 20))

        # Kristal sayısı
        kristal_surf = self.font_orta.render(
            f"Kan Kristali: {meta_sis.kristal} 💎", True, (160, 80, 255))
        ekran.blit(kristal_surf, (genislik // 2 - kristal_surf.get_width() // 2, 70))

        # Yeni kazanılan kristal bildirimi
        if self._kazanilan_gosterim_sure > 0 and self._kazanilan_kristal > 0:
            alpha = int(255 * min(1.0, self._kazanilan_gosterim_sure))
            kazan_surf = self.font_orta.render(
                f"+ {self._kazanilan_kristal} kristal kazandın! ✨", True, (255, 220, 80))
            kazan_surf.set_alpha(alpha)
            ekran.blit(kazan_surf, (genislik // 2 - kazan_surf.get_width() // 2, 100))

        # Upgrade listesi
        baslangic_y = 140
        satir_yuk = 72
        liste_genislik = min(genislik - 40, 900)
        liste_x = (genislik - liste_genislik) // 2

        # Kırpma alanı (kaydırma için)
        clip = pygame.Rect(0, 130, genislik, yukseklik - 200)
        ekran.set_clip(clip)

        for i, (key, u) in enumerate(META_UPGRADELER.items()):
            satir_y = baslangic_y + i * satir_yuk - self.kaydirma

            if satir_y < 80 or satir_y > yukseklik:
                continue

            secili = (i == self.secili_idx)
            sev = meta_sis.seviye(key)
            max_sev = u["max_seviye"]
            fiyat = meta_sis.upgrade_fiyati(key)
            alinabilir = meta_sis.satin_alinabilir_mi(key)
            maxlandı = (sev >= max_sev)

            # Kart arka planı
            kart = pygame.Surface((liste_genislik, satir_yuk - 6), pygame.SRCALPHA)
            if maxlandı:
                kart.fill((15, 40, 15, 200))
            elif secili:
                kart.fill((30, 20, 50, 220))
            else:
                kart.fill((15, 10, 30, 180))
            ekran.blit(kart, (liste_x, satir_y))

            # Çerçeve
            cerc_renk = (80, 220, 80) if maxlandı else ((180, 120, 255) if secili else (50, 30, 80))
            pygame.draw.rect(ekran, cerc_renk,
                             (liste_x, satir_y, liste_genislik, satir_yuk - 6), 1,
                             border_radius=5)

            # Emoji + isim
            isim_metin = f"{u['emoji']} {u['isim']}"
            isim_surf = self.font_orta.render(isim_metin, True,
                                               (200, 255, 200) if maxlandı else BEYAZ)
            ekran.blit(isim_surf, (liste_x + 12, satir_y + 6))

            # Açıklama
            ac_surf = self.font_kucuk.render(u["aciklama"], True, (160, 160, 200))
            ekran.blit(ac_surf, (liste_x + 12, satir_y + 32))

            # Seviye göstergesi (küçük kareler)
            for s in range(max_sev):
                renk_k = (150, 80, 255) if s < sev else (40, 30, 60)
                pygame.draw.rect(ekran, renk_k,
                                 (liste_x + 260 + s * 14, satir_y + 20, 10, 10),
                                 border_radius=2)

            # Sağ taraf: fiyat ve satın al butonu
            if maxlandı:
                max_surf = self.font_orta.render("MAX ✓", True, (80, 255, 80))
                ekran.blit(max_surf, (liste_x + liste_genislik - 100, satir_y + 18))
            else:
                # Fiyat
                fiyat_renk = (255, 220, 80) if alinabilir else (150, 80, 80)
                fiyat_surf = self.font_kucuk.render(f"{fiyat} 💎", True, fiyat_renk)
                ekran.blit(fiyat_surf, (liste_x + liste_genislik - 150, satir_y + 8))

                # Satın al butonu
                btn_renk = (80, 50, 150) if alinabilir else (40, 30, 50)
                btn_x = liste_x + liste_genislik - 140
                btn_y = satir_y + 26
                pygame.draw.rect(ekran, btn_renk, (btn_x, btn_y, 130, 30), border_radius=5)
                if alinabilir:
                    pygame.draw.rect(ekran, (130, 80, 220), (btn_x, btn_y, 130, 30), 1,
                                     border_radius=5)
                btn_metin = "AL [SPACE]" if secili else "SATIN AL"
                btn_surf = self.font_kucuk.render(btn_metin, True,
                                                   BEYAZ if alinabilir else (80, 80, 80))
                ekran.blit(btn_surf, (btn_x + 65 - btn_surf.get_width() // 2, btn_y + 7))

        ekran.set_clip(None)

        # Devam butonu
        devam_x = genislik // 2 - 110
        devam_y = yukseklik - 70
        pygame.draw.rect(ekran, (60, 20, 120), (devam_x, devam_y, 220, 50), border_radius=8)
        pygame.draw.rect(ekran, (140, 80, 255), (devam_x, devam_y, 220, 50), 2, border_radius=8)
        devam_surf = self.font_orta.render("DEVAM [ESC/ENTER]", True, BEYAZ)
        ekran.blit(devam_surf, (genislik // 2 - devam_surf.get_width() // 2, devam_y + 12))

        # Kontroller ipucu
        ipucu = self.font_kucuk.render("↑↓ Seçim   SPACE Satın Al   Fare ile de kullanabilirsin",
                                        True, (80, 80, 120))
        ekran.blit(ipucu, (genislik // 2 - ipucu.get_width() // 2, yukseklik - 95))
