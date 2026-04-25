# ============================================================
#  ekranlar/oyun_ekrani.py — Nişangah Konisi (Aim Cone) ve Devasa Grafikler
# ============================================================
import pygame
import math
import random
from ayarlar import (
    GENISLIK, YUKSEKLIK, ARKAPLAN, BEYAZ, SIYAH, KIRMIZI, YESIL, SARI, ALTIN, 
    SILAHLAR, SILAH_SIRASI, ZIRH_MAVI, CAMGOBEGI, PEMBE, MOR, TURUNCU
)
from varliklar.oyuncu  import Oyuncu
from varliklar.zombi   import Zombi
from varliklar.drop    import Drop
from varliklar.patlama import Patlama
from varliklar.parcacik import kan_parcaciklari, HarasarSayisi, BasarimBildirimi
from sistemler.dalga_sistemi import DalgaSistemi
from sistemler.puan_sistemi  import PuanSistemi
from sistemler.raycaster     import Raycaster
from sistemler.harita_sistemi import HaritaSistemi
from sistemler.cutscene import BossGirisBildirim, CutscenePlayer, chapter_from_wave, iter_loading_notes
from sistemler.juice import JuceSistemi, HitMarker, DalgaGirisAnimasyonu
from sistemler.gorev_sistemi import GorevSistemi
from sistemler.meta_progression import meta_sis
from varliklar.boss import Boss, BossGirisAnimasyonu

class OyunEkrani:
    def __init__(self):
        self.font_hud    = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_buyuk  = pygame.font.SysFont("Consolas", 46, bold=True)
        self.font_kucuk  = pygame.font.SysFont("Consolas", 15, bold=True)
        self.font_sayi   = pygame.font.SysFont("Impact", 18)
        self.font_sayi_b = pygame.font.SysFont("Impact", 32)
        self.font_mermi  = pygame.font.SysFont("Impact", 56)
        
        # Grafik iyileştirme: Zemin Detayları (Kan ve Enkaz)
        self._zemin = []
        for _ in range(300):
            r = random.choice([2, 3, 5])
            c = random.choice([(30, 35, 40), (20, 25, 30), (45, 25, 25)]) # Kırmızımsı lekeler ve gri taşlar
            self._zemin.append((random.randint(-200, GENISLIK + 200), random.randint(-200, YUKSEKLIK + 200), r, c))

        self.harita_sis = HaritaSistemi()
        
        self.is_3d = False # Direkt 3D başlasın
        self.raycaster = Raycaster(pygame.display.get_surface())
        self.cutscene = CutscenePlayer()
        self.boss_giris = BossGirisBildirim()
        self.yukleme_notlari = iter_loading_notes()
        self.kerem_replikler = self._replikleri_hazirla()
        self.kerem_mesaj = ""
        self.kerem_mesaj_sure = 0.0
        self.radyo_mesajlari = self._radyo_hazirla()
        self.radyo_index = 0
        self.radyo_sure = 0.0
        self.radyo_metin = ""
        self.hikaye_secimi = None
        self.secim_sure = 0.0
        self.terminal_satirlari: list[str] = []
        self.terminal_sure = 0.0
        self.npc_satirlari: list[str] = []
        self.npc_sure = 0.0
        self.oyuncu_portre_durum = "normal"
        self._sifirla()

    def _sifirla(self):
        self.mermiler    = pygame.sprite.Group()
        self.zombiler    = pygame.sprite.Group()
        self.droplar     = pygame.sprite.Group()
        self.patlamalar  = []
        self.parcaciklar = []
        self.sayilar     = []
        self.basarimlar  = []
        self.zehir_havuzlari = []
        self.hit_markerlar = []
        self.bosslar = pygame.sprite.Group()
        self.boss_giris_animasyonu = None
        self.juice = JuceSistemi(GENISLIK, YUKSEKLIK)
        self.gorev_sis = GorevSistemi()
        self.dalga_giris_anim = None
        
        bas_x, bas_y = self.harita_sis.rastgele_guvenli_nokta(32)
        self.oyuncu      = Oyuncu(bas_x, bas_y)
        meta_sis.oyuncu_bonuslarini_uygula(self.oyuncu)
        self.dalga_sis   = DalgaSistemi(self.zombiler)
        self.puan_sis    = PuanSistemi()
        self.hikaye_bildirimi = ""
        self.hikaye_bildirim_sayaci = 0.0
        self.npc_liste = self.harita_sis.aktif_npc_listesi()
        self.gecilen_bolgeler = {self.harita_sis.aktif_harita["isim"]}
        self.oldurulen_zombi = 0
        
        self.sarsinti    = 0.0
        self.bitti       = False
        self.son_fare_pos = (0, 0)
        self._son_hasar_alindi = False

    def baslat(self):
        self._sifirla()
        self.cutscene.start(1, 10.0)
        if self.is_3d:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)

    def toggle_3d_mode(self):
        self.is_3d = not self.is_3d
        if self.is_3d:
            try:
                pygame.mouse.set_relative_mode(True)
            except:
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)
        else:
            try:
                pygame.mouse.set_relative_mode(False)
            except:
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)

    def harita_degistir(self):
        """2D mod için farklı arena temasına geç."""
        self.harita_sis.harita_degistir()
        self._sifirla()

    def _hareket_cozucu(self, eski_x, eski_y, yeni_x, yeni_y, yaricap):
        return self.harita_sis.hareketi_sinirla(eski_x, eski_y, yeni_x, yeni_y, yaricap)

    def _replikleri_hazirla(self):
        return {
            "combo": [f"Durdurulamam! ({i})" for i in range(1, 21)],
            "hasar": [
                "Ah!", "Dikkat Kerem!", "Bu canımı yaktı.", "Bunu hissettim.", "Dönmüşler çok yakın!",
                "Geri çekil.", "Kalkanım eriyor.", "Nefes al, odaklan.", "Ayağa kalk.", "Henüz bitmedi.",
                "Kan kaybediyorum.", "Dozu tutturmalıyım.", "Siper al.", "Tansiyon düşüyor.", "Daha hızlı ol.",
                "Bu saldırı planlı.", "Acı... iyiye işaret değil.", "Uyanık kal.", "Şimdi olmaz.", "Devam et.",
            ],
            "boss": [
                "O... o nedir?", "Selim bunu da mı hazırladı?", "Bu yaratık laboratuvardan kaçmış olmalı.",
                "Bunu tek başıma indireceğim.", "ARGUS'un son kartı bu mu?", "Gözünü üstümden ayırmıyor.",
                "Nabzım 140... sakin ol.", "Burası mezarım olmayacak.", "Sıfır noktasına giden yol bu.", "Hadi gel!",
                "Kerem, kontrol sende.", "Tetikte kal.", "Antidot için buna değer.", "Bu iş burada bitecek.", "Ya o ya ben.",
                "Nefesini dinle.", "Zayıf noktası olmalı.", "Dönmüşlerden farklı hareket ediyor.", "Geri adım yok.", "İnsanlık için.",
            ],
        }

    def _radyo_hazirla(self):
        return [
            "📻 Radyo: Bölge 7 bariyerleri düştü.", "📻 Radyo: ARGUS droneleri kuzeye çekildi.",
            "📻 Radyo: Hayatta kalanlar metro çıkışında toplansın.", "📻 Radyo: EDEN suşu mutasyon gösteriyor.",
            "📻 Radyo: Selim Koç yayın hattını ele geçirdi.", "📻 Radyo: Tıbbi destek birimi yok edildi.",
            "📻 Radyo: Yeraltı kapıları kısa süreli açıldı.", "📻 Radyo: Kontrol odasında sıcaklık artıyor.",
            "📻 Radyo: Karantina hattı tamamen çöktü.", "📻 Radyo: Sıfır Noktası koordinatı doğrulandı.",
            "📻 Radyo: Şehir merkezinde EMP kullanıldı.", "📻 Radyo: Sunucu yedeği aktif.",
            "📻 Radyo: Biyometrik kilit kırılmaya çalışılıyor.", "📻 Radyo: Güvenli oda 10 saniye içinde kapanacak.",
            "📻 Radyo: Dönmüş sürüsü otoyola yöneldi.", "📻 Radyo: Reaktör odasında radyasyon yükseliyor.",
            "📻 Radyo: Dr. Kerem için acil kanal açık.", "📻 Radyo: Tahliye koridoru 3 dakika erişilebilir.",
            "📻 Radyo: ARGUS iç yazışmaları sızdırıldı.", "📻 Radyo: Antidot protokolü yarım fakat çalışıyor.",
        ]

    def _kerem_mesaj_tetikle(self, tur: str):
        havuz = self.kerem_replikler.get(tur, [])
        if havuz:
            self.kerem_mesaj = random.choice(havuz)
            self.kerem_mesaj_sure = 2.5

    def guncelle(self, dt, tuslar, fare_pos):
        if self.bitti:
            return

        self.cutscene.update(dt)
        if self.cutscene.active:
            return
        
        if self.is_3d:
            # FPS Oyunlarındaki gibi akıcı fare kontrolü
            rel_x, _ = pygame.mouse.get_rel()
            
            # Hassasiyeti ayarla (Frame rate bağımsız - dt ile çarpım)
            # 0.15 baz hassasiyet, dt ile normalize ediyoruz
            hassasiyet = 15.0 
            self.oyuncu.aci += rel_x * hassasiyet * dt
            
            fare_pos = (GENISLIK // 2, YUKSEKLIK // 2)

        self.son_fare_pos = fare_pos
        # YENİ: Juice ve görev güncelleme
        juice_dt = self.juice.oyun_dt(dt)
        self.juice.guncelle(dt)
        self.gorev_sis.guncelle(dt, self._son_hasar_alindi)
        self._son_hasar_alindi = False
        # Boss giriş animasyonu
        if self.boss_giris_animasyonu and self.boss_giris_animasyonu.aktif:
            self.boss_giris_animasyonu.guncelle(dt)
        # Dalga giriş animasyonu
        if self.dalga_giris_anim and self.dalga_giris_anim.aktif:
            self.dalga_giris_anim.guncelle(dt)
        # Hit markerlar
        self.hit_markerlar = [h for h in self.hit_markerlar if h.update(dt)]
        # Görev combo güncelle
        self.gorev_sis.olay_isle("kombo", self.puan_sis.combo)
        # Juice vignette: düşük can
        can_oran = self.oyuncu.can / self.oyuncu.max_can
        if can_oran < 0.35:
            self.juice.vignette_ayarla(int(180 * (1.0 - can_oran / 0.35)), (150, 0, 0))
        self.oyuncu.update(
            dt,
            tuslar,
            fare_pos,
            self.mermiler,
            GENISLIK,
            YUKSEKLIK,
            self.is_3d,
            self._hareket_cozucu,
        )
        self.mermiler.update(dt, GENISLIK, YUKSEKLIK)
        self.puan_sis.update(dt)

        for zh in self.zehir_havuzlari[:]:
            zh[3] -= dt
            if zh[3] <= 0:
                self.zehir_havuzlari.remove(zh)
            elif math.hypot(zh[0] - self.oyuncu.x, zh[1] - self.oyuncu.y) < (zh[2] + self.oyuncu.yari_cap):
                self.oyuncu.zombi_temas(dt, 5)

        for z in list(self.zombiler):
            yakin_ayni = sum(1 for d in self.zombiler if d is not z and d.tip == z.tip and math.hypot(d.x - z.x, d.y - z.y) <= 80)
            z.update(dt, self.oyuncu.x, self.oyuncu.y, self._hareket_cozucu, yakin_ayni)
            if z.tip == "zehirli" and z.zehir_sayac >= 0.3:
                z.zehir_sayac = 0.0
                self.zehir_havuzlari.append([z.x, z.y, 16, 2.5, 2.5])
                
            if z.tip == "patlayan" and getattr(z, "patlamaya_hazir", False):
                self.patlamalar.append(Patlama(z.x, z.y, 120))
                if math.hypot(self.oyuncu.x - z.x, self.oyuncu.y - z.y) < 120 + self.oyuncu.yari_cap:
                    self.oyuncu.hasar_al(35)
                    z.kill()
                    self.oldurulen_zombi += 1
                    self.sarsinti = 0.3
                    self.juice.patlama_efekti(1.0)
                else:
                    onceki_can = self.oyuncu.can
                    self.oyuncu.zombi_temas(dt, z.hasar)
                    if random.random() < 0.12:
                        self._kerem_mesaj_tetikle("hasar")
                    if self.oyuncu.can < onceki_can:
                        self.juice.hasar_alindi_efekti()
                        self._son_hasar_alindi = True
                    
                if self.oyuncu.oldu:
                    self._bitis()
                    return

        for m in list(self.mermiler):
            if not m.alive(): continue
            if m.tip in ("roket", "seken_bomba", "delici_patlayan"):
                for z in list(self.zombiler):
                    if math.hypot(z.x - m.x, z.y - m.y) < (z.yari_cap + m.yari_cap):
                        self.patlamalar.append(Patlama(m.x, m.y, m.patlama_r))
                        m.kill()
                        break
            else:
                for z in list(self.zombiler):
                    if m.tip == "delici" and z in m.vurulan_zombiler:
                        continue
                        
                    oldu = z.mermi_carpisma(m)
                    
                    if m.tip == "delici":
                        if not m.alive():
                            m.add(self.mermiler)
                        m.vurulan_zombiler.add(z)
                        
                    if not m.alive() or m.tip == "delici":
                        # Element efekt parçacıkları
                        renk = m.renk if m.efekt != "yok" else (180, 20, 20)
                        self.parcaciklar.extend(kan_parcaciklari(z.x, z.y, 4, renk))
                        self.sayilar.append(HarasarSayisi(z.x, z.y, m.hasar, m.renk))
                        if oldu:
                            self._zombi_oldu(z)
                        if not m.alive():
                            break

        for m in list(self.mermiler):
            if not m.alive() and m.tip in ("roket", "seken_bomba", "delici_patlayan") and m.patlama_hazir:
                self.patlamalar.append(Patlama(m.x, m.y, m.patlama_r))

        for p in self.patlamalar[:]:
            p.update(dt)
            if not p.hasar_verildi:
                oldukler = p.zombi_hasari_ver(self.zombiler, self.oyuncu.hasar_carpani * p.r * 1.5)
                for z in oldukler:
                    self.sayilar.append(HarasarSayisi(z.x, z.y, self.oyuncu.hasar_carpani * p.r * 1.5, SARI, True))
                    self._zombi_oldu(z)
            if p.bitti_mi:
                self.patlamalar.remove(p)

        for d in list(self.droplar):
            d.update(dt)
            if d.alive() and d.oyuncuya_dokunan(self.oyuncu.x, self.oyuncu.y, self.oyuncu.yari_cap):
                if d.tip == "can":
                    self.oyuncu.can_doldur(40)
                    self.sayilar.append(HarasarSayisi(self.oyuncu.x, self.oyuncu.y, 40, YESIL, True))
                elif d.tip == "mermi":
                    self.oyuncu.aktif_mermi_doldur()
                    self.sayilar.append(HarasarSayisi(self.oyuncu.x, self.oyuncu.y, "+Mermi!", SARI, True))
                d.kill()

        for dm in self.dusman_mermileri[:]:
            dm["omur"] -= dt
            dm["x"] += dm["vx"] * dt
            dm["y"] += dm["vy"] * dt
            if dm["omur"] <= 0:
                self.dusman_mermileri.remove(dm)
                continue
            if math.hypot(dm["x"] - self.oyuncu.x, dm["y"] - self.oyuncu.y) <= self.oyuncu.yari_cap + dm["r"]:
                self.oyuncu.hasar_al(dm["hasar"])
                self.dusman_mermileri.remove(dm)
                self._kerem_mesaj_tetikle("hasar")
                if self.oyuncu.oldu:
                    self._bitis()
                    return

        self.parcaciklar = [p for p in self.parcaciklar if p.update(dt)]
        self.sayilar = [s for s in self.sayilar if s.update(dt)]
        self.basarimlar = [b for b in self.basarimlar if b.update(dt)]
        
        if self.puan_sis.yeni_seviye_flag:
            self.puan_sis.yeni_seviye_flag = False
            self.basarimlar.append(BasarimBildirimi(f"SEVİYE {self.puan_sis.seviye}!", "Tüm istatistiklerin artıyor!"))

        if self.oyuncu.yoruldu_mu:
            self.sayilar.append(HarasarSayisi(self.oyuncu.x, self.oyuncu.y, "Yoruldum!", KIRMIZI))

        if self.sarsinti > 0: self.sarsinti -= dt
        if self.hikaye_bildirim_sayaci > 0:
            self.hikaye_bildirim_sayaci -= dt
        mesaj = self.harita_sis.hikaye_guncelle(self.oyuncu, self.dalga_sis.dalga_no)
        if mesaj:
            self.hikaye_bildirimi = mesaj
            self.hikaye_bildirim_sayaci = 3.0
            self.puan_sis.para += 120
        prev_chapter = chapter_from_wave(max(1, self.dalga_sis.dalga_no))
        self.dalga_sis.guncelle(dt, GENISLIK, YUKSEKLIK)
        yeni = chapter_from_wave(max(1, self.dalga_sis.dalga_no))
        if yeni != prev_chapter:
            self.cutscene.start(yeni, 5.0)
            self.gecilen_bolgeler.add(self.harita_sis.aktif_harita["isim"])

        boss = self.dalga_sis.pop_boss_giris()
        if boss:
            self.boss_giris.trigger(boss[0], boss[1])
            self._kerem_mesaj_tetikle("boss")
        self.boss_giris.update(dt)

        self.kerem_mesaj_sure = max(0.0, self.kerem_mesaj_sure - dt)
        self.radyo_sure = max(0.0, self.radyo_sure - dt)
        if self.dalga_sis.dalga_no > 0 and self.dalga_sis.dalga_no % 2 == 0 and self.radyo_sure <= 0:
            self.radyo_metin = self.radyo_mesajlari[self.radyo_index % len(self.radyo_mesajlari)]
            self.radyo_index += 1
            self.radyo_sure = 4.0

        kayit = self.harita_sis.gunluk_kontrol(self.oyuncu.x, self.oyuncu.y)
        if kayit:
            self.hikaye_bildirimi = kayit
            self.hikaye_bildirim_sayaci = 3.0

        terminal = self.harita_sis.terminal_yakin(self.oyuncu.x, self.oyuncu.y)
        if terminal and tuslar.get("etkilesim"):
            self.terminal_satirlari = self.harita_sis.terminal_oku(terminal)
            self.terminal_sure = 4.0
        self.terminal_sure = max(0.0, self.terminal_sure - dt)

        for npc in self.npc_liste:
            if npc.yakin_mi(self.oyuncu.x, self.oyuncu.y) and tuslar.get("etkilesim"):
                self.npc_satirlari = [f"{s.speaker}: {s.text}" for s in npc.satirlar()]
                self.npc_sure = 4.0
                break
        self.npc_sure = max(0.0, self.npc_sure - dt)

        if self.dalga_sis.dalga_no > 0 and self.dalga_sis.dalga_no % 5 == 0 and self.hikaye_secimi is None and self.secim_sure <= 0:
            self.hikaye_secimi = "bekle"
            self.secim_sure = 7.0
        if self.hikaye_secimi is not None:
            if tuslar.get("secim1"):
                self.hikaye_secimi = "antidot"
                self.dalga_sis.secim_uygula("antidot")
            elif tuslar.get("secim2"):
                self.hikaye_secimi = "tahliye"
                self.dalga_sis.secim_uygula("tahliye")
            if self.hikaye_secimi in {"antidot", "tahliye"}:
                self.secim_sure = 0.0
            else:
                self.secim_sure -= dt
                if self.secim_sure <= 0:
                    self.hikaye_secimi = "denge"
                    self.dalga_sis.secim_uygula("denge")

        if self.oyuncu.can < self.oyuncu.max_can * 0.35:
            self.oyuncu_portre_durum = "kritik"
        elif self.oyuncu.can < self.oyuncu.max_can * 0.7:
            self.oyuncu_portre_durum = "yarali"
        else:
            self.oyuncu_portre_durum = "saglikli"


    def _zombi_oldu(self, z):
        if not z.alive(): return
        if z.tip == "patlayan":
            self.patlamalar.append(Patlama(z.x, z.y, 120))
            if z.patlama_hasar_mesafe(self.oyuncu.x, self.oyuncu.y) < 120 + self.oyuncu.yari_cap:
                self.oyuncu.hasar_al(40)
                
        self.parcaciklar.extend(kan_parcaciklari(z.x, z.y, 18))
        elde_puan, elde_para = self.puan_sis.zombi_oldu(z.skor, z.para, baz_xp=25, combo_suresi_ek=self.oyuncu.yukseltmeler["combo"]*0.5)
        self.sayilar.append(HarasarSayisi(z.x, z.y - 25, f"+{elde_para}$", ALTIN))
        
        self.sarsinti = 0.12 if z.tip != "boss" else 0.35
        drop = z.drop_olustur()
        if drop: self.droplar.add(drop)
        # Juice efektleri
        self.juice.hit_freeze(0.035, 0.65)
        self.hit_markerlar.append(HitMarker(z.x, z.y - 20))
        # Patlayan zombi için ekstra juice
        if z.tip == "patlayan":
            self.juice.patlama_efekti(0.8)
        # Görev olayları
        self.gorev_sis.olay_isle("oldurme")
        aktif_veri = self.oyuncu.silah_verisi
        if aktif_veri.get("efekt", "yok") != "yok":
            self.gorev_sis.olay_isle("element_oldurme", aktif_veri["efekt"])
        self.gorev_sis.silah_kullanildi(self.oyuncu.aktif_silah, True)
        # Meta vampir
        if hasattr(self.oyuncu, "_meta_vampir") and self.oyuncu._meta_vampir > 0:
            self.oyuncu.can_doldur(self.oyuncu._meta_vampir)
        z.kill()
        self.oldurulen_zombi += 1

    def _bitis(self):
        self.bitti = True
        self.puan_sis.kaydet()

    def ciz(self, ekran):
        if self.is_3d:
            self.raycaster.ciz(
                self.oyuncu,
                self.zombiler,
                self.mermiler,
                self.droplar,
                self.harita_sis.aktif_harita,
            )
            self._ciz_hud(ekran)
            self._ciz_bildirim(ekran)
            self._ciz_silah_bar(ekran)
            self._ciz_anlatim(ekran)
            return

        ox = random.randint(-4, 4) if self.sarsinti > 0 else 0
        oy = random.randint(-4, 4) if self.sarsinti > 0 else 0

        aktif_harita = self.harita_sis.aktif_harita
        ekran.fill(aktif_harita["zemin"])
        
        # Izgara çizgileri (Fayans Derzleri)
        kare = aktif_harita["karo"]
        for x in range(int(ox) % kare, GENISLIK, kare):
            pygame.draw.line(ekran, aktif_harita["cizgi"], (x, 0), (x, YUKSEKLIK), 2)
        for y in range(int(oy) % kare, YUKSEKLIK, kare):
            pygame.draw.line(ekran, aktif_harita["cizgi"], (0, y), (GENISLIK, y), 2)
            
        for (px, py, pr, pcolor) in self._zemin:
            pygame.draw.circle(ekran, pcolor, (px + ox, py + oy), pr)
        for r in aktif_harita.get("engeller", []):
            rr = pygame.Rect(r.x + ox, r.y + oy, r.width, r.height)
            pygame.draw.rect(ekran, (35, 38, 48), rr, border_radius=8)
            pygame.draw.rect(ekran, (82, 88, 106), rr, 3, border_radius=8)
        for lx, ly, renk in aktif_harita.get("isiklar", []):
            halo = pygame.Surface((180, 180), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*renk, 70), (90, 90), 80)
            ekran.blit(halo, (lx - 90 + ox, ly - 90 + oy))
        for lx, ly, isim, renk in aktif_harita.get("landmarks", []):
            pygame.draw.circle(ekran, renk, (int(lx + ox), int(ly + oy)), 8)
            lbl = self.font_kucuk.render(isim, True, renk)
            ekran.blit(lbl, (lx + 12 + ox, ly - 8 + oy))
        for npc in self.npc_liste:
            npc.ciz(ekran, ox, oy)
            if npc.yakin_mi(self.oyuncu.x, self.oyuncu.y):
                et = self.font_kucuk.render("E: Konuş", True, (255, 230, 180))
                ekran.blit(et, (npc.x - 20 + ox, npc.y - 30 + oy))
        terminal = self.harita_sis.terminal_yakin(self.oyuncu.x, self.oyuncu.y)
        if terminal:
            et = self.font_kucuk.render("E: Kaydı Oku", True, (170, 255, 170))
            tx, ty = terminal["pos"]
            ekran.blit(et, (tx - 30 + ox, ty - 30 + oy))
            
        for zh in self.zehir_havuzlari:
            alpha = int(90 * (zh[3] / zh[4]))
            s = pygame.Surface((zh[2]*2, zh[2]*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (50, 255, 80, alpha), (zh[2], zh[2]), zh[2])
            ekran.blit(s, (zh[0] - zh[2] + ox, zh[1] - zh[2] + oy))

        for d in self.droplar: ekran.blit(d.image, (d.rect.x + ox, d.rect.y + oy))
        
        # Nişangah (Cone) Çizimi (Sadece oyuncu yaşıyorsa)
        if not self.bitti:
            self.oyuncu.ciz_nisangah(ekran, self.son_fare_pos, ox, oy)

        for m in self.mermiler: ekran.blit(m.image, (m.rect.x + ox, m.rect.y + oy))
        for dm in self.dusman_mermileri:
            pygame.draw.circle(ekran, PEMBE, (int(dm["x"] + ox), int(dm["y"] + oy)), dm["r"])
        for p in self.patlamalar: p.ciz(ekran)
        for p in self.parcaciklar: p.ciz(ekran)

        for z in self.zombiler: ekran.blit(z.image, (z.rect.x + ox, z.rect.y + oy))
        for z in self.zombiler: z.can_bar_ciz(ekran)

        ekran.blit(self.oyuncu.image, (self.oyuncu.rect.x + ox, self.oyuncu.rect.y + oy))
        
        for s in self.sayilar: s.ciz(ekran, self.font_sayi, self.font_sayi_b)

        # 2D/3D ve Harita ipucu metni
        ipucu = self.font_kucuk.render(
            f"3: 2D/3D  |  M: Harita ({aktif_harita['isim']})",
            True,
            (200, 200, 200),
        )
        ekran.blit(ipucu, (GENISLIK - ipucu.get_width() - 20, YUKSEKLIK - ipucu.get_height() - 20))

        self._ciz_hud(ekran)
        self._ciz_bildirim(ekran)
        self._ciz_silah_bar(ekran)
        self._ciz_anlatim(ekran)
        self.oyuncu.flash_ciz(ekran)
        
        for b in self.basarimlar: b.ciz(ekran, self.font_kucuk, self.font_hud, GENISLIK, YUKSEKLIK)
        # YENİ: Hit markerlar
        for h in self.hit_markerlar:
            h.ciz(ekran)
        # YENİ: Görev paneli
        self.gorev_sis.ciz(ekran, self.font_kucuk, self.font_hud, GENISLIK, YUKSEKLIK)
        # YENİ: Juice efektleri (en üstte)
        self.juice.ciz(ekran)
        # YENİ: Dalga giriş animasyonu
        if self.dalga_giris_anim and self.dalga_giris_anim.aktif:
            self.dalga_giris_anim.ciz(ekran, self.font_buyuk, self.font_kucuk, GENISLIK, YUKSEKLIK)
        # YENİ: Boss giriş animasyonu
        if self.boss_giris_animasyonu and self.boss_giris_animasyonu.aktif:
            self.boss_giris_animasyonu.ciz(ekran, self.font_buyuk, self.font_kucuk, GENISLIK, YUKSEKLIK)

    def _ciz_hud(self, ekran):
        pygame.draw.rect(ekran, (10, 10, 15, 200), (20, 20, 300, 140), border_radius=12)
        pygame.draw.rect(ekran, (50, 50, 60), (20, 20, 300, 140), 2, border_radius=12)
        
        bx, by, bg, byk = 30, 30, 280, 16
        
        # 1. Can
        c_oran = self.oyuncu.can / self.oyuncu.max_can
        pygame.draw.rect(ekran, (60, 0, 0), (bx, by, bg, byk), border_radius=6)
        if c_oran > 0: pygame.draw.rect(ekran, (220, 50, 50), (bx, by, int(bg * c_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"HP: {int(self.oyuncu.can)}", True, BEYAZ), (bx + 8, by))
        
        # 2. Kalkan
        by += 22
        k_oran = self.oyuncu.kalkan / self.oyuncu.max_kalkan_degeri
        pygame.draw.rect(ekran, (0, 30, 80), (bx, by, bg, byk), border_radius=6)
        if k_oran > 0: pygame.draw.rect(ekran, ZIRH_MAVI, (bx, by, int(bg * k_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"SH: {int(self.oyuncu.kalkan)}", True, BEYAZ), (bx + 8, by))

        # 3. Stamina
        by += 22
        s_oran = self.oyuncu.stamina / self.oyuncu.max_stamina_degeri
        pygame.draw.rect(ekran, (60, 60, 60), (bx, by, bg, byk), border_radius=6)
        if s_oran > 0: pygame.draw.rect(ekran, (255, 255, 100), (bx, by, int(bg * s_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"STM: {int(self.oyuncu.stamina)}", True, SIYAH if s_oran > 0.5 else BEYAZ), (bx + 8, by))

        # 4. XP
        by += 22
        xp_oran = self.puan_sis.xp / self.puan_sis.xp_hedef
        pygame.draw.rect(ekran, (40, 40, 40), (bx, by, bg, byk), border_radius=6)
        if xp_oran > 0: pygame.draw.rect(ekran, MOR, (bx, by, int(bg * xp_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"SV: {self.puan_sis.seviye}", True, BEYAZ), (bx + 8, by))
        
        # 5. Ultimate
        by += 22
        u_oran = 1.0 - (self.oyuncu.ult_bekleme / self.oyuncu.ult_max_cd)
        pygame.draw.rect(ekran, (40, 40, 0), (bx, by, bg, byk), border_radius=6)
        if u_oran > 0: pygame.draw.rect(ekran, SARI, (bx, by, int(bg * u_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render("ULT [BOŞLUK]" if u_oran >= 1.0 else f"ULT: {self.oyuncu.ult_bekleme:.1f}s", True, SIYAH if u_oran >= 1.0 else BEYAZ), (bx + bg//2 - 45, by))

        # Sağ üst panel
        pygame.draw.rect(ekran, (10, 10, 15, 200), (GENISLIK - 240, 20, 220, 110), border_radius=12)
        pygame.draw.rect(ekran, (50, 50, 60), (GENISLIK - 240, 20, 220, 110), 2, border_radius=12)
        
        st = self.font_hud.render(f"PUAN: {self.puan_sis.puan}", True, BEYAZ)
        ekran.blit(st, (GENISLIK - st.get_width() - 35, 30))
        pt = self.font_hud.render(f"💰 {self.puan_sis.para}", True, ALTIN)
        ekran.blit(pt, (GENISLIK - pt.get_width() - 35, 60))
        dt2 = self.font_hud.render(f"DALGA: {self.dalga_sis.dalga_no}", True, (180, 255, 180))
        ekran.blit(dt2, (GENISLIK - dt2.get_width() - 35, 90))

        # Sağ alt panel - MERMİ GÖSTERGESİ (Büyütüldü)
        ak = self.oyuncu.aktif_silah
        mermi = self.oyuncu.mermiler.get(ak, -1)
        kapasite = self.oyuncu._silah_max_mermi(ak)
        
        m_metin = "∞" if kapasite == -1 else f"{mermi}/{kapasite}"
        renk = KIRMIZI if mermi == 0 else (SARI if mermi < kapasite * 0.3 else BEYAZ)
        
        pygame.draw.rect(ekran, (10, 10, 15, 200), (GENISLIK - 260, YUKSEKLIK - 120, 240, 100), border_radius=15)
        pygame.draw.rect(ekran, (50, 50, 60), (GENISLIK - 260, YUKSEKLIK - 120, 240, 100), 2, border_radius=15)
        
        t = self.font_mermi.render(m_metin, True, renk)
        ekran.blit(t, (GENISLIK - 140 - t.get_width()//2, YUKSEKLIK - 105))
        
        silah_isim = SILAHLAR[ak]["isim"]
        sit = self.font_kucuk.render(silah_isim, True, SILAHLAR[ak]["renk"])
        ekran.blit(sit, (GENISLIK - 140 - sit.get_width()//2, YUKSEKLIK - 45))

        # Combo
        if self.puan_sis.combo >= 5 and random.random() < 0.02:
            self._kerem_mesaj_tetikle("combo")

        if self.puan_sis.combo > 1:
            cx = GENISLIK // 2
            cy = 80
            ct = self.font_buyuk.render(f"{self.puan_sis.combo}x COMBO!", True, TURUNCU)
            ekran.blit(ct, (cx - ct.get_width() // 2, cy))

        # Hikaye paneli
        pygame.draw.rect(ekran, (10, 10, 16, 220), (20, YUKSEKLIK - 200, 470, 130), border_radius=12)
        pygame.draw.rect(ekran, (50, 70, 90), (20, YUKSEKLIK - 200, 470, 130), 2, border_radius=12)
        baslik = self.font_hud.render(self.harita_sis.aktif_hikaye_baslik, True, CAMGOBEGI)
        gorev = self.font_kucuk.render(f"Görev: {self.harita_sis.aktif_gorev}", True, BEYAZ)
        ekran.blit(baslik, (32, YUKSEKLIK - 188))
        ekran.blit(gorev, (32, YUKSEKLIK - 156))
        if self.hikaye_bildirim_sayaci > 0 and self.hikaye_bildirimi:
            bil = self.font_kucuk.render(self.hikaye_bildirimi, True, ALTIN)
            ekran.blit(bil, (32, YUKSEKLIK - 126))

    def _ciz_anlatim(self, ekran):
        self.cutscene.draw(ekran)
        self.boss_giris.draw(ekran)

        # Kerem portresi + diyalog
        px, py = GENISLIK - 430, YUKSEKLIK - 250
        pygame.draw.rect(ekran, (15, 15, 20, 220), (px, py, 390, 150), border_radius=10)
        pygame.draw.rect(ekran, (70, 70, 90), (px, py, 390, 150), 2, border_radius=10)
        self._ciz_kerem_portre(ekran, px + 55, py + 75)
        if self.kerem_mesaj_sure > 0 and self.kerem_mesaj:
            km = self.font_kucuk.render(f"Kerem: {self.kerem_mesaj}", True, BEYAZ)
            ekran.blit(km, (px + 95, py + 40))

        if self.radyo_sure > 0 and self.radyo_metin:
            r = self.font_kucuk.render(self.radyo_metin, True, (140, 255, 160))
            ekran.blit(r, (40, YUKSEKLIK - 36))

        if self.terminal_sure > 0 and self.terminal_satirlari:
            w, h = 700, 220
            x, y = GENISLIK // 2 - w // 2, YUKSEKLIK // 2 - h // 2
            pygame.draw.rect(ekran, (0, 18, 0, 240), (x, y, w, h), border_radius=8)
            pygame.draw.rect(ekran, (70, 180, 90), (x, y, w, h), 2, border_radius=8)
            for i, line in enumerate(self.terminal_satirlari[:7]):
                s = self.font_kucuk.render(line, True, (170, 255, 170))
                ekran.blit(s, (x + 20, y + 20 + i * 28))

        if self.npc_sure > 0 and self.npc_satirlari:
            for i, line in enumerate(self.npc_satirlari[:3]):
                s = self.font_kucuk.render(line, True, (255, 230, 180))
                ekran.blit(s, (40, 220 + i * 26))

        if self.hikaye_secimi == "bekle":
            p = self.font_hud.render("Seçim: [1] Önce Antidot  [2] Önce Tahliye", True, (255, 240, 120))
            ekran.blit(p, (GENISLIK // 2 - p.get_width() // 2, 26))

        # Bölüm hedef progress
        hedefler = self.harita_sis.aktif_harita["hikaye"]["hedefler"]
        oran = min(1.0, self.harita_sis.hikaye_asama / max(1, len(hedefler)))
        pygame.draw.rect(ekran, (35, 35, 45), (20, 170, 300, 14), border_radius=7)
        pygame.draw.rect(ekran, (90, 210, 180), (20, 170, int(300 * oran), 14), border_radius=7)

    def _ciz_kerem_portre(self, ekran, cx, cy):
        pygame.draw.circle(ekran, (220, 200, 170), (cx, cy), 30)
        pygame.draw.circle(ekran, (30, 30, 40), (cx - 10, cy - 8), 4)
        pygame.draw.circle(ekran, (30, 30, 40), (cx + 10, cy - 8), 4)
        if self.oyuncu_portre_durum == "saglikli":
            pygame.draw.arc(ekran, (20, 20, 20), (cx - 12, cy - 2, 24, 18), 0.2, 2.9, 2)
        elif self.oyuncu_portre_durum == "yarali":
            pygame.draw.line(ekran, (20, 20, 20), (cx - 12, cy + 10), (cx + 12, cy + 10), 2)
        else:
            pygame.draw.arc(ekran, (20, 20, 20), (cx - 12, cy + 4, 24, 14), 3.4, 6.0, 2)
            pygame.draw.circle(ekran, (180, 30, 30), (cx + 22, cy - 20), 7)

    def _ciz_silah_bar(self, ekran):
        bar_yuk = 80
        bar_y = YUKSEKLIK - bar_yuk - 20
        
        kart_gen, bosluk = 80, 10
        sahip = [k for k in SILAH_SIRASI if k in self.oyuncu.envanter]
        
        # Çok fazla silah varsa ekranın altına sığmayabilir, sadece seçili silaha en yakın olanları çizebiliriz.
        # Ya da basitçe hepsini çizelim (1920 ekranda 20-25 silah sığar).
        gosterilecek = sahip[-15:] # Ekrana sığması için son 15 silah
        
        toplam_gen = len(gosterilecek) * (kart_gen + bosluk) - bosluk
        start_x = GENISLIK // 2 - toplam_gen // 2
        
        # Arkaplan
        pygame.draw.rect(ekran, (10, 10, 15, 200), (start_x - 10, bar_y - 10, toplam_gen + 20, bar_yuk + 20), border_radius=15)

        for i, key in enumerate(gosterilecek):
            veri = SILAHLAR[key]
            aktif = self.oyuncu.aktif_silah == key
            kx, ky, kh = start_x + i * (kart_gen + bosluk), bar_y, bar_yuk

            bg = (50, 80, 50) if aktif else (30, 30, 40)
            border = veri["renk"] if aktif else (80, 80, 80)
            
            if aktif:
                hale = pygame.Surface((kart_gen+10, kh+10), pygame.SRCALPHA)
                pygame.draw.rect(hale, (*veri["renk"], 80), (0, 0, kart_gen+10, kh+10), border_radius=12)
                ekran.blit(hale, (kx-5, ky-5))

            pygame.draw.rect(ekran, bg, (kx, ky, kart_gen, kh), border_radius=10)
            pygame.draw.rect(ekran, border, (kx, ky, kart_gen, kh), 2, border_radius=10)

            pygame.draw.circle(ekran, veri["renk"], (kx + kart_gen//2, ky + 25), 12)
            isim_t = self.font_kucuk.render(veri["isim"][:9], True, BEYAZ if aktif else (160, 160, 160))
            ekran.blit(isim_t, (kx + kart_gen//2 - isim_t.get_width()//2, ky + 45))

    def _ciz_bildirim(self, ekran):
        metin, kalan = self.dalga_sis.bildirim_goster()
        if not metin: return
        alpha = min(255, int(255 * (kalan / 2.5)))
        surf = self.font_buyuk.render(metin, True, (255, 100, 100) if "BOSS" in metin else SARI)
        surf.set_alpha(alpha)
        ekran.blit(surf, (GENISLIK // 2 - surf.get_width() // 2, YUKSEKLIK // 2 - 120))

    def dalga_bitti_isle(self):
        """main.py shop'a geçmeden önce çağırır. Görev ödüllerini verir."""
        self.gorev_sis.dalga_bitti()
        para, kristal = self.gorev_sis.toplam_odulleri_topla()
        if para > 0:
            self.puan_sis.para += para
        if kristal > 0:
            meta_sis.kristal_ekle(kristal)
        self.gorev_sis.yeni_dalga_gorevi_ver(self.dalga_sis.dalga_no + 1)

    @property
    def oyuncu_oldu_mu(self): return self.bitti
    @property
    def dalga_bitti_mi(self): return self.dalga_sis.dalga_bitti
    @property
    def son_puan(self): return self.puan_sis.puan
    @property
    def dalga_no(self): return self.dalga_sis.dalga_no
    @property
    def yuksek_skorlar(self): return self.puan_sis.yuksek_skorlar
    @property
    def acilan_kayitlar(self): return list(self.harita_sis.acilan_kayitlar)
    @property
    def gecilen_bolge_listesi(self): return list(self.gecilen_bolgeler)
    @property
    def oldurulen_zombi_sayisi(self): return self.oldurulen_zombi
    @property
    def zafer_mi(self): return self.dalga_sis.dalga_no >= 25
