"""Dalga üretimi ve olay bildirimleri."""

from __future__ import annotations

import random
from varliklar.zombi import Zombi
from varliklar.boss import Boss

BOSS_DIALOGS = {
    5: ("Direktör Selim Koç", "Dönüşüm bir felaket değil, ürün lansmanı."),
    10: ("Direktör Selim Koç", "Karantina bitti doktor. Sırada yeraltı var."),
    15: ("Direktör Selim Koç", "Antidot ararken ordumu büyütüyorsun."),
    20: ("Direktör Selim Koç", "Sıfır Noktası'na hoş geldin."),
    25: ("Selim Koç — Nihai Form", "ARGUS Protokolü benimle tamamlanacak."),
}


class DalgaSistemi:
    def __init__(self, zombiler_grubu, boss_grubu=None):
        self.zombiler = zombiler_grubu
        self.boss_grubu = boss_grubu
        self.dalga_no = 0
        self.spawn_listesi = []
        self.spawn_sayac = 0.0
        self.spawn_aralik = 0.8
        self.dalga_aktif = False
        self.dalga_bitti = False
        self.bildirim_sayac = 0.0
        self.bildirim_metni = ""
        self.son_boss_giris: tuple[str, str] | None = None
        self.hikaye_secim = "denge"

    def secim_uygula(self, secim: str) -> None:
        self.hikaye_secim = secim

    def _dalga_olustur(self, dalga_no):
        liste = []
        normal = 4 + dalga_no * 2
        hizli = max(0, dalga_no * 2 - 2)
        kosucu = max(0, dalga_no - 3) * 2
        patlayan = max(0, dalga_no - 4)
        zehirli = max(0, dalga_no - 6)
        zirhli = max(0, dalga_no - 4)
        kopek = max(0, dalga_no - 2)
        sniper = max(0, dalga_no - 5)

        if self.hikaye_secim == "antidot":
            zehirli += max(1, dalga_no // 2)
        elif self.hikaye_secim == "tahliye":
            hizli += max(1, dalga_no // 2)

        liste += ["normal"] * normal
        liste += ["hizli"] * hizli
        liste += ["kosucu"] * kosucu
        liste += ["patlayan"] * patlayan
        liste += ["zehirli"] * zehirli
        liste += ["zirhli"] * zirhli
        liste += ["kopek"] * kopek
        liste += ["sniper_zombi"] * sniper

        if dalga_no % 5 == 0:
            boss_sayisi = dalga_no // 5
            liste += ["boss"] * boss_sayisi
            liste += ["patlayan"] * boss_sayisi * 2
            self.son_boss_giris = BOSS_DIALOGS.get(dalga_no, ("ARGUS Komutan", "Protokol sürüyor."))

        random.shuffle(liste)
        return liste

    def guncelle(self, dt, ekran_w, ekran_h):
        if self.dalga_bitti:
            return

        if not self.dalga_aktif:
            self._yeni_dalga_baslat(ekran_w, ekran_h)
            return

        if self.spawn_listesi:
            self.spawn_sayac -= dt
            if self.spawn_sayac <= 0:
                tip = self.spawn_listesi.pop(0)
                if tip == "boss" and self.boss_grubu is not None:
                    boss_tipi = Boss.dalga_icin_boss_sec(self.dalga_no)
                    b = Boss.kenar_spawn(ekran_w, ekran_h, boss_tipi)
                    self.boss_grubu.add(b)
                else:
                    self.zombiler.add(Zombi.rastgele_dogur(ekran_w, ekran_h, tip))
                self.spawn_sayac = self.spawn_aralik
        elif len(self.zombiler) == 0 and (self.boss_grubu is None or len(self.boss_grubu) == 0):
            self.dalga_aktif = False
            self.dalga_bitti = True
            self.bildirim_metni = "✓ Dalga Temizlendi!"
            self.bildirim_sayac = 2.0

        if self.bildirim_sayac > 0:
            self.bildirim_sayac -= dt

    def _yeni_dalga_baslat(self, ekran_w, ekran_h):
        self.dalga_no += 1
        self.dalga_aktif = True
        self.dalga_bitti = False
        self.spawn_listesi = self._dalga_olustur(self.dalga_no)
        self.spawn_sayac = 0.5
        self.spawn_aralik = max(0.15, 0.7 - self.dalga_no * 0.05)

        self.bildirim_metni = f"DALGA {self.dalga_no}"
        if self.dalga_no % 5 == 0:
            self.bildirim_metni += " — BOSS DALGASI! 💀"
        self.bildirim_sayac = 2.5

    def yeni_dalga_hazirla(self):
        self.dalga_bitti = False
        self.dalga_aktif = False

    def pop_boss_giris(self) -> tuple[str, str] | None:
        boss = self.son_boss_giris
        self.son_boss_giris = None
        return boss

    def bildirim_goster(self):
        if self.bildirim_sayac > 0:
            return self.bildirim_metni, self.bildirim_sayac
        return None, 0
