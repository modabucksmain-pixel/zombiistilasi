# ============================================================
#  sistemler/kamera.py — Dinamik Kamera Sistemi
#  Oyuncu takibi, yumuşak zoom, ekran-dünya koordinat dönüşümü
# ============================================================
import pygame
import math


class Kamera:
    """Büyük dünya haritası için kamera sistemi.

    Özellikler:
    - Oyuncuyu yumuşak takip (lerp)
    - Nişan alınca zoom in, sprint atınca zoom out
    - Ekran ↔ dünya koordinat dönüşümü
    - Görünür alan hesaplama (culling için)
    """

    def __init__(self, ekran_w: int, ekran_h: int, dunya_w: int, dunya_h: int):
        self.ekran_w = ekran_w
        self.ekran_h = ekran_h
        self.dunya_w = dunya_w
        self.dunya_h = dunya_h

        # Kamera merkez pozisyonu (dünya koordinatı)
        self.x = float(dunya_w // 2)
        self.y = float(dunya_h // 2)

        # Zoom
        self.zoom = 1.0
        self.hedef_zoom = 1.0
        self.MIN_ZOOM = 0.6
        self.MAX_ZOOM = 2.0

        # Takip yumuşaklığı
        self.takip_hizi = 5.0  # Lerp hızı

        # Sarsıntı
        self.sarsinti = 0.0

    def guncelle(self, dt: float, oyuncu_x: float, oyuncu_y: float,
                 nisan: bool = False, sprint: bool = False) -> None:
        """Her frame çağrılır. Kamerayı oyuncuya doğru hareket ettirir."""
        # Hedef zoom belirle
        if nisan:
            self.hedef_zoom = 1.3
        elif sprint:
            self.hedef_zoom = 0.85
        else:
            self.hedef_zoom = 1.0

        # Zoom'u yumuşak geçişle hedefe yaklaştır
        self.zoom += (self.hedef_zoom - self.zoom) * 4.0 * dt
        self.zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, self.zoom))

        # Oyuncuyu yumuşak takip et (lerp)
        hedef_x = oyuncu_x
        hedef_y = oyuncu_y
        self.x += (hedef_x - self.x) * self.takip_hizi * dt
        self.y += (hedef_y - self.y) * self.takip_hizi * dt

        # Kamerayı dünya sınırları içinde tut
        yari_w = (self.ekran_w / 2) / self.zoom
        yari_h = (self.ekran_h / 2) / self.zoom

        self.x = max(yari_w, min(self.dunya_w - yari_w, self.x))
        self.y = max(yari_h, min(self.dunya_h - yari_h, self.y))

        # Sarsıntı azalt
        if self.sarsinti > 0:
            self.sarsinti = max(0.0, self.sarsinti - dt)

    def sarsinti_ekle(self, miktar: float) -> None:
        """Ekran sarsıntısı ekle."""
        self.sarsinti = max(self.sarsinti, miktar)

    def dunya_to_ekran(self, dunya_x: float, dunya_y: float) -> tuple[int, int]:
        """Dünya koordinatını ekran koordinatına çevirir."""
        import random
        ox = random.randint(-4, 4) if self.sarsinti > 0 else 0
        oy = random.randint(-4, 4) if self.sarsinti > 0 else 0

        ekran_x = (dunya_x - self.x) * self.zoom + self.ekran_w / 2 + ox
        ekran_y = (dunya_y - self.y) * self.zoom + self.ekran_h / 2 + oy
        return int(ekran_x), int(ekran_y)

    def ekran_to_dunya(self, ekran_x: float, ekran_y: float) -> tuple[float, float]:
        """Ekran koordinatını dünya koordinatına çevirir."""
        dunya_x = (ekran_x - self.ekran_w / 2) / self.zoom + self.x
        dunya_y = (ekran_y - self.ekran_h / 2) / self.zoom + self.y
        return dunya_x, dunya_y

    def gorunur_alan(self) -> pygame.Rect:
        """Ekranda görünen dünya alanını Rect olarak döndürür (culling için)."""
        yari_w = (self.ekran_w / 2) / self.zoom
        yari_h = (self.ekran_h / 2) / self.zoom
        # Biraz pay bırak (spawn ve geçiş için)
        pay = 200
        return pygame.Rect(
            int(self.x - yari_w - pay),
            int(self.y - yari_h - pay),
            int(yari_w * 2 + pay * 2),
            int(yari_h * 2 + pay * 2),
        )

    def gorunur_mu(self, x: float, y: float, yaricap: float = 50) -> bool:
        """Bir nokta ekranda görünür mü? (Hızlı kontrol)"""
        alan = self.gorunur_alan()
        return alan.collidepoint(int(x), int(y))

    def rect_gorunur_mu(self, rect: pygame.Rect) -> bool:
        """Bir rect ekranda görünür mü?"""
        return self.gorunur_alan().colliderect(rect)

    @property
    def offset(self) -> tuple[float, float]:
        """Basit offset (eski sistemle uyumluluk için).
        Dünya (0,0) noktasının ekrandaki konumu."""
        import random
        ox = random.randint(-4, 4) if self.sarsinti > 0 else 0
        oy = random.randint(-4, 4) if self.sarsinti > 0 else 0
        return (
            -self.x * self.zoom + self.ekran_w / 2 + ox,
            -self.y * self.zoom + self.ekran_h / 2 + oy,
        )
