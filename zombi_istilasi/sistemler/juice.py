# ============================================================
#  sistemler/juice.py — Görsel "Juice" Efektleri
#  Hit freeze, chromatic aberration, ekran sarsıntısı,
#  vignette efektleri, ekran yanması, dalga giriş efekti
# ============================================================
import pygame
import math
import random


class JuceSistemi:
    """Tüm görsel juice efektlerini yöneten merkezi sistem."""

    def __init__(self, genislik, yukseklik):
        self.genislik = genislik
        self.yukseklik = yukseklik

        # Sarsıntı
        self.sarsinti_guc = 0.0
        self.sarsinti_x = 0
        self.sarsinti_y = 0

        # Hit freeze (zaman donması hissi)
        self.freeze_sure = 0.0
        self.freeze_guc = 0.0   # 0=normal, 1=tam donma
        self.zaman_carpani = 1.0

        # Chromatic aberration (renk kayması)
        self.chroma_guc = 0.0
        self.chroma_sure = 0.0

        # Vignette (kenar kararması)
        self.vignette_alpha = 0
        self.vignette_hedef = 0
        self.vignette_renk = (0, 0, 0)

        # Ekran yanması (beyaz/renkli flash)
        self.flash_alpha = 0
        self.flash_renk = (255, 255, 255)
        self.flash_sure = 0.0

        # Slow-motion
        self.slowmo_sure = 0.0
        self.slowmo_guc = 0.4   # 0.4 = %40 hız

        # Önceden hazırlanmış yüzeyler (perf için)
        self._vignette_surf = None
        self._son_vignette_alpha = -1

        # Komboya göre hit sayisi efekti
        self.kombo_flash_sayac = 0.0
        self.kombo_renk = (255, 200, 0)

    def sarsinti_ekle(self, guc, sure=0.25):
        self.sarsinti_guc = max(self.sarsinti_guc, guc)

    def hit_freeze(self, sure=0.04, guc=0.7):
        """Vurma anında kısa zaman donması."""
        self.freeze_sure = max(self.freeze_sure, sure)
        self.freeze_guc = max(self.freeze_guc, guc)

    def chroma_ekle(self, guc=8.0, sure=0.3):
        self.chroma_guc = max(self.chroma_guc, guc)
        self.chroma_sure = max(self.chroma_sure, sure)

    def flash_ekle(self, renk=(255, 255, 255), alpha=120, sure=0.15):
        self.flash_renk = renk
        self.flash_alpha = alpha
        self.flash_sure = sure

    def slowmo_baslat(self, sure=2.0, guc=0.35):
        self.slowmo_sure = max(self.slowmo_sure, sure)
        self.slowmo_guc = guc

    def vignette_ayarla(self, alpha, renk=(0, 0, 0)):
        self.vignette_hedef = alpha
        self.vignette_renk = renk

    def kombo_efekti(self, kombo):
        """Yüksek komboda renkli flash ve sarsıntı."""
        if kombo >= 10:
            self.kombo_flash_sayac = 0.2
            self.kombo_renk = (255, 50, 50) if kombo >= 15 else (255, 180, 0)
            self.sarsinti_ekle(kombo * 0.15)

    def patlama_efekti(self, buyukluk=1.0):
        """Patlama anında tüm efektler."""
        self.sarsinti_ekle(8 * buyukluk)
        self.flash_ekle((255, 200, 80), int(80 * buyukluk), 0.1)
        self.chroma_ekle(12 * buyukluk, 0.4)

    def boss_olum_efekti(self):
        """Boss ölünce epik efekt."""
        self.flash_ekle((255, 80, 20), 200, 0.4)
        self.sarsinti_ekle(20)
        self.chroma_ekle(20, 0.8)
        self.slowmo_baslat(1.5, 0.2)

    def hasar_alindi_efekti(self):
        """Oyuncu hasar alınca efekt."""
        self.flash_ekle((255, 0, 0), 80, 0.12)
        self.sarsinti_ekle(5)
        self.chroma_ekle(6, 0.2)

    def guncelle(self, dt):
        # Hit freeze - dt'yi değiştir
        if self.freeze_sure > 0:
            self.freeze_sure -= dt
            self.zaman_carpani = max(0.0, 1.0 - self.freeze_guc)
        else:
            self.freeze_sure = 0.0
            # Slow-motion
            if self.slowmo_sure > 0:
                self.slowmo_sure -= dt
                self.zaman_carpani = self.slowmo_guc
            else:
                self.zaman_carpani = 1.0
            self.freeze_guc = max(0.0, self.freeze_guc - dt * 5)

        # Sarsıntı
        if self.sarsinti_guc > 0:
            self.sarsinti_x = random.randint(-1, 1) * int(self.sarsinti_guc)
            self.sarsinti_y = random.randint(-1, 1) * int(self.sarsinti_guc)
            self.sarsinti_guc = max(0.0, self.sarsinti_guc - dt * 40)
        else:
            self.sarsinti_x = self.sarsinti_y = 0

        # Chromatic aberration
        if self.chroma_sure > 0:
            self.chroma_sure -= dt
            self.chroma_guc = max(0.0, self.chroma_guc - dt * 30)
        else:
            self.chroma_guc = 0.0

        # Flash
        if self.flash_sure > 0:
            self.flash_sure -= dt
            oran = max(0.0, self.flash_sure / max(0.01, self.flash_sure + dt))
            self.flash_alpha = int(self.flash_alpha * oran)
        else:
            self.flash_alpha = 0

        # Vignette yumuşak geçiş
        self.vignette_alpha += (self.vignette_hedef - self.vignette_alpha) * min(1.0, dt * 5)
        self.vignette_hedef = 0  # Her frame'de sıfırlanacak, guncelle çağıranı tekrar set etmeli

        # Kombo flash
        if self.kombo_flash_sayac > 0:
            self.kombo_flash_sayac -= dt

    def oyun_dt(self, dt):
        """Juice modifiye edilmiş dt döndürür."""
        return dt * self.zaman_carpani

    def ciz(self, ekran):
        """Tüm ekran üstü efektleri çiz."""
        # Chromatic aberration
        if self.chroma_guc > 1.0:
            self._chroma_ciz(ekran)

        # Flash
        if self.flash_alpha > 10:
            fsurf = pygame.Surface((self.genislik, self.yukseklik), pygame.SRCALPHA)
            fsurf.fill((*self.flash_renk, self.flash_alpha))
            ekran.blit(fsurf, (0, 0))

        # Vignette
        if self.vignette_alpha > 5:
            self._vignette_ciz(ekran)

        # Kombo flash kenarı
        if self.kombo_flash_sayac > 0:
            alpha = int(150 * self.kombo_flash_sayac / 0.2)
            ksurf = pygame.Surface((self.genislik, self.yukseklik), pygame.SRCALPHA)
            pygame.draw.rect(ksurf, (*self.kombo_renk, alpha),
                             (0, 0, self.genislik, self.yukseklik), 12)
            ekran.blit(ksurf, (0, 0))

    def _chroma_ciz(self, ekran):
        """Chromatic aberration: ekranı 3 kanala ayır, kaydır."""
        offset = int(self.chroma_guc)
        if offset < 2:
            return
        # Ekran yüzeyini kopyala
        orijinal = ekran.copy()
        gen, yuk = ekran.get_size()

        # Kırmızı kanal
        r_surf = pygame.Surface((gen, yuk), pygame.SRCALPHA)
        r_surf.fill((0, 0, 0, 0))
        r_mask = pygame.Surface((gen, yuk), pygame.SRCALPHA)
        r_mask.blit(orijinal, (0, 0))
        # Sadece kırmızı kanalı tut (yaklaşık)
        r_surf.blit(orijinal, (offset, 0))
        r_surf.set_alpha(60)
        ekran.blit(r_surf, (-offset, 0), special_flags=pygame.BLEND_ADD)

        # Mavi kanal
        b_surf = orijinal.copy()
        b_surf.set_alpha(60)
        ekran.blit(b_surf, (offset, 0), special_flags=pygame.BLEND_ADD)

    def _vignette_ciz(self, ekran):
        """Kenar kararması."""
        alpha = int(self.vignette_alpha)
        if alpha < 5:
            return
        vsurf = pygame.Surface((self.genislik, self.yukseklik), pygame.SRCALPHA)
        # Köşelerden ortaya doğru gradient (4 kenarlı dikdörtgen vignette)
        kalinlik = min(200, self.genislik // 3)
        for i in range(kalinlik):
            a = int(alpha * (1.0 - i / kalinlik) ** 2)
            if a < 2:
                break
            pygame.draw.rect(vsurf, (*self.vignette_renk, a),
                             (i, i, self.genislik - i * 2, self.yukseklik - i * 2), 1)
        ekran.blit(vsurf, (0, 0))

    def sarsinti_offset(self):
        """Kamera sarsıntı offset'ini döndürür."""
        return self.sarsinti_x, self.sarsinti_y


class HitMarker:
    """Vurma anında ekranda görünen '+' işareti."""
    def __init__(self, x, y, kritik=False):
        self.x = x
        self.y = y
        self.omur = 0.35
        self.max_omur = 0.35
        self.kritik = kritik
        self.buyukluk = 14 if kritik else 8

    def update(self, dt):
        self.omur -= dt
        return self.omur > 0

    def ciz(self, ekran):
        oran = self.omur / self.max_omur
        alpha = int(255 * oran)
        buyukluk = int(self.buyukluk * (1.0 + (1.0 - oran) * 0.5))
        renk = (255, 50, 50) if self.kritik else (255, 255, 255)

        surf = pygame.Surface((buyukluk * 2 + 4, buyukluk * 2 + 4), pygame.SRCALPHA)
        cx = cy = buyukluk + 2
        kalinlik = 3 if self.kritik else 2
        pygame.draw.line(surf, (*renk, alpha), (cx - buyukluk, cy), (cx + buyukluk, cy), kalinlik)
        pygame.draw.line(surf, (*renk, alpha), (cx, cy - buyukluk), (cx, cy + buyukluk), kalinlik)
        ekran.blit(surf, (int(self.x) - buyukluk - 2, int(self.y) - buyukluk - 2))


class DalgaGirisAnimasyonu:
    """Dalga başında 'DALGA X' yazısı büyüyüp kaybolur."""
    def __init__(self, dalga_no, metin=None):
        self.dalga_no = dalga_no
        self.metin = metin or f"DALGA {dalga_no}"
        self.omur = 2.5
        self.max_omur = 2.5
        self.aktif = True

    def guncelle(self, dt):
        self.omur -= dt
        if self.omur <= 0:
            self.aktif = False

    def ciz(self, ekran, font_buyuk, font_kucuk, genislik, yukseklik):
        if not self.aktif:
            return
        oran = self.omur / self.max_omur
        # İlk 0.3s büyüyüp beliriyor, sonra soluklaşıyor
        if oran > 0.85:
            gecis = (1.0 - oran) / 0.15
            alpha = int(255 * gecis)
        else:
            alpha = int(255 * min(1.0, oran * 1.5))

        boyut_carpan = 1.0 + (1.0 - oran) * 0.15

        # Arka panel
        panel_h = 90
        panel = pygame.Surface((genislik, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, int(alpha * 0.6)))
        ekran.blit(panel, (0, yukseklik // 2 - panel_h // 2))

        # Dalga yazısı
        renk = (255, 220, 50) if self.dalga_no % 5 == 0 else (200, 220, 255)
        surf = font_buyuk.render(self.metin, True, renk)
        surf.set_alpha(alpha)
        w = int(surf.get_width() * boyut_carpan)
        h = int(surf.get_height() * boyut_carpan)
        surf = pygame.transform.scale(surf, (w, h))
        ekran.blit(surf, (genislik // 2 - w // 2, yukseklik // 2 - h // 2))
