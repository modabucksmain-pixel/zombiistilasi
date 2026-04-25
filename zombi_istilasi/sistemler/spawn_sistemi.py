# ============================================================
#  sistemler/spawn_sistemi.py — Sürekli Zombi Spawn Sistemi
#  Dalga sistemi yerine bölge bazlı sürekli spawn + despawn
# ============================================================
import math
import random
import pygame
from varliklar.zombi import Zombi
from varliklar.boss import Boss


class SurekliSpawnSistemi:
    """Büyük harita için sürekli zombi spawn/despawn yöneticisi."""

    def __init__(self, zombiler_grubu, boss_grubu, dunya_haritasi):
        self.zombiler = zombiler_grubu
        self.boss_grubu = boss_grubu
        self.dunya = dunya_haritasi

        self.spawn_sayac = 0.0
        self.max_zombi = 40
        self.spawn_mesafe_min = 600   # Oyuncudan en az bu kadar uzakta spawn
        self.spawn_mesafe_max = 1400  # Oyuncudan en fazla bu kadar uzakta spawn
        self.despawn_mesafe = 2200    # Bu mesafeden uzak zombiler silinir

        # Boss durumları
        self.aktif_bosslar: dict[str, bool] = {}  # bolge_key -> uyanmış mı
        self.boss_uyandi_callback = None  # Dışarıdan set edilir

        # İstatistik
        self.toplam_spawn = 0

    def guncelle(self, dt: float, oyuncu_x: float, oyuncu_y: float):
        """Her frame çağrılır."""
        bolge_key = self.dunya.oyuncu_bolgesi(oyuncu_x, oyuncu_y)

        # Güvenli bölgedeyse spawn yapma
        if self.dunya.guvenli_mi(oyuncu_x, oyuncu_y):
            self._despawn_uzak(oyuncu_x, oyuncu_y)
            return

        tehlike = self.dunya.bolge_tehlike(oyuncu_x, oyuncu_y)
        self.max_zombi = 30 + tehlike * 15
        spawn_aralik = max(0.3, 1.5 - tehlike * 0.3)

        # Spawn sayacı
        self.spawn_sayac -= dt
        if self.spawn_sayac <= 0 and len(self.zombiler) < self.max_zombi:
            self.spawn_sayac = spawn_aralik
            self._spawn_zombi(oyuncu_x, oyuncu_y, bolge_key)

        # Despawn (uzak zombiler)
        self._despawn_uzak(oyuncu_x, oyuncu_y)

        # Boss kontrolü
        if bolge_key:
            self._boss_kontrol(oyuncu_x, oyuncu_y, bolge_key)

    def _spawn_zombi(self, ox: float, oy: float, bolge_key: str | None):
        """Oyuncudan belirli mesafede zombi oluşturur."""
        if not bolge_key or bolge_key not in self.dunya.bolgeler:
            return

        tipler = self.dunya.spawn_tipleri(bolge_key)
        if not tipler:
            return

        # Rastgele açı ve mesafe ile spawn noktası bul
        for _ in range(10):  # 10 deneme
            aci = random.uniform(0, math.tau)
            mesafe = random.uniform(self.spawn_mesafe_min, self.spawn_mesafe_max)
            sx = ox + math.cos(aci) * mesafe
            sy = oy + math.sin(aci) * mesafe

            # Duvar içinde mi kontrol et
            if self.dunya.nokta_duvar_icinde(sx, sy, 20):
                continue

            # Güvenli bölgede mi kontrol et
            if self.dunya.guvenli_mi(sx, sy):
                continue

            # Erişilebilir bölgede mi kontrol et
            spawn_bolge = self.dunya.oyuncu_bolgesi(sx, sy)
            if not spawn_bolge:
                continue
            if not self.dunya.bolge_erisebilir_mi(spawn_bolge):
                continue

            tip = random.choice(tipler)

            # Tehlike seviyesine göre nadir tipler ekle
            tehlike = self.dunya.bolgeler[bolge_key]["tehlike"]
            if tehlike >= 2 and random.random() < 0.1:
                tip = random.choice(["mini_boss", "kalkan"])
            if tehlike >= 3 and random.random() < 0.08:
                tip = random.choice(["mini_boss", "vampir", "donusturucu"])

            z = Zombi(sx, sy, tip)
            self.zombiler.add(z)
            self.toplam_spawn += 1
            return

    def _despawn_uzak(self, ox: float, oy: float):
        """Oyuncudan çok uzak zombileri siler (performans)."""
        for z in list(self.zombiler):
            mesafe = math.hypot(z.x - ox, z.y - oy)
            if mesafe > self.despawn_mesafe:
                z.kill()

    def _boss_kontrol(self, ox: float, oy: float, bolge_key: str):
        """Sabit boss noktası yakınındaysa boss'u uyandırır."""
        bolge = self.dunya.bolgeler.get(bolge_key)
        if not bolge or not bolge.get("boss_noktasi"):
            return

        boss_x, boss_y, boss_tipi = bolge["boss_noktasi"]

        # Zaten uyanmış mı?
        if bolge_key in self.aktif_bosslar:
            return

        # Boss öldürülmüş mü? (hikaye durumundan kontrol)
        kilit_key = f"{bolge_key}_boss"
        if self.dunya.hikaye_durum.get(kilit_key, False):
            return

        # Oyuncu yakın mı?
        mesafe = math.hypot(boss_x - ox, boss_y - oy)
        if mesafe < 300:
            boss = Boss(boss_x, boss_y, boss_tipi)
            self.boss_grubu.add(boss)
            self.aktif_bosslar[bolge_key] = True

            if self.boss_uyandi_callback:
                self.boss_uyandi_callback(boss, bolge_key)

    def boss_oldu(self, bolge_key: str):
        """Boss öldürüldüğünde çağrılır."""
        self.dunya.boss_oldu(bolge_key)
        if bolge_key in self.aktif_bosslar:
            del self.aktif_bosslar[bolge_key]

    @property
    def aktif_zombi_sayisi(self):
        return len(self.zombiler) + len(self.boss_grubu)
