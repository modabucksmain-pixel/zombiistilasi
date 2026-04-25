# ============================================================
#  ekranlar/oyun_ekrani.py — Büyük Dünya Haritası + Nişangah Konisi
# ============================================================
import pygame
import math
import random
from ayarlar import (
    GENISLIK, YUKSEKLIK, ARKAPLAN, BEYAZ, SIYAH, KIRMIZI, YESIL, SARI, ALTIN,
    SILAHLAR, SILAH_SIRASI, ZIRH_MAVI, CAMGOBEGI, PEMBE, MOR, TURUNCU,
    RADYO_MESAJLARI, ZOMBI_ZAYIFLIK
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
from sistemler.muzik import MuzikSistemi
from sistemler.basarim import BasarimSistemi, BASARIMLAR_TANIM
from sistemler.parcacik_pool import ParcacikPool
from varliklar.boss import Boss, BossGirisAnimasyonu
# ── Yeni Büyük Dünya Sistemleri ──
from sistemler.kamera import Kamera
from sistemler.dunya_haritasi import DunyaHaritasi, DUNYA_W, DUNYA_H
from sistemler.spawn_sistemi import SurekliSpawnSistemi
from sistemler.hikaye_yoneticisi import HikayeYoneticisi

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
        # ── Büyük dünya sistemi ──
        self.dunya = DunyaHaritasi()
        self.kamera = Kamera(GENISLIK, YUKSEKLIK, DUNYA_W, DUNYA_H)
        self.hikaye_yon = None  # _sifirla'da oluşturulacak
        
        self.is_3d = False # Direkt 3D başlasın
        self.raycaster = Raycaster(pygame.display.get_surface())
        self.cutscene = CutscenePlayer()
        self.boss_giris = BossGirisBildirim()
        self.yukleme_notlari = iter_loading_notes()
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
        self.dusman_mermileri = []
        self.hit_markerlar = []
        self.bosslar = pygame.sprite.Group()
        self.boss_giris_animasyonu = None
        self.juice = JuceSistemi(GENISLIK, YUKSEKLIK)
        self.gorev_sis = GorevSistemi()
        self.dalga_giris_anim = None
        self.muzik_sis = MuzikSistemi()
        self.basarim_sis = BasarimSistemi()
        self.parcacik_pool = ParcacikPool()
        self.radyo_sayac = 0.0
        self.radyo_aralik = random.uniform(18.0, 35.0)
        self.radyo_aktif_sure = 0.0
        self.radyo_aktif_metin = ""
        self.dalga_sure_sayac = 0.0
        self.basarim_bildirim_sayac = 0.0
        self.basarim_bildirim_veri: dict | None = None
        self._hasarsiz_dalga_sayisi = 0
        self._dalga_hasar_alindi = False

        # ── Büyük dünya: spawn noktası Merkez Meydan ──
        self.dunya = DunyaHaritasi()
        bas_x, bas_y = self.dunya.rastgele_guvenli_nokta(32)
        self.oyuncu = Oyuncu(bas_x, bas_y)
        meta_sis.oyuncu_bonuslarini_uygula(self.oyuncu)
        self.dalga_sis = DalgaSistemi(self.zombiler, self.bosslar)
        self.spawn_sis = SurekliSpawnSistemi(self.zombiler, self.bosslar, self.dunya)
        self.hikaye_yon = HikayeYoneticisi(self.dunya)
        self.spawn_sis.boss_uyandi_callback = self._boss_uyandi
        self.puan_sis = PuanSistemi()
        self.hikaye_bildirimi = ""
        self.hikaye_bildirim_sayaci = 0.0
        self.npc_liste = self.dunya.npc_listesi_olustur()
        self.gecilen_bolgeler = {"Merkez Meydan"}
        self.oldurulen_zombi = 0
        self.level_anim_sure = 0.0

        # Kamerayı oyuncu başlangıcına ayarla
        self.kamera = Kamera(GENISLIK, YUKSEKLIK, DUNYA_W, DUNYA_H)
        self.kamera.x = float(bas_x)
        self.kamera.y = float(bas_y)

        self.sarsinti = 0.0
        self.bitti = False
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
        """Büyük dünyada harita değiştirme devre dışı."""
        pass

    def _hareket_cozucu(self, eski_x, eski_y, yeni_x, yeni_y, yaricap):
        return self.dunya.hareketi_sinirla(eski_x, eski_y, yeni_x, yeni_y, yaricap)

    def _boss_uyandi(self, boss, bolge_key):
        """SurekliSpawnSistemi boss uyandığında çağırır."""
        self.boss_giris_animasyonu = BossGirisAnimasyonu(boss.isim)
        self.sarsinti = 0.5

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
            DUNYA_W,
            DUNYA_H,
            self.is_3d,
            self._hareket_cozucu,
        )
        self.mermiler.update(dt, DUNYA_W, DUNYA_H)
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
                continue

            if z.tip == "sniper_zombi":
                uzak = math.hypot(self.oyuncu.x - z.x, self.oyuncu.y - z.y)
                if 220 <= uzak <= 500 and z.sniper_sayac <= 0:
                    aci = math.atan2(self.oyuncu.y - z.y, self.oyuncu.x - z.x)
                    self.dusman_mermileri.append({"x": z.x, "y": z.y, "vx": math.cos(aci) * 280, "vy": math.sin(aci) * 280, "r": 6, "omur": 2.8, "hasar": 10})
                    z.sniper_sayac = 2.0

            # Element DoT ile ölen zombiler
            if z.can <= 0:
                self._zombi_oldu(z)
                continue

            if z.oyuncuya_yakin_mi(self.oyuncu.x, self.oyuncu.y) and z.tip != "sniper_zombi":
                onceki_can = self.oyuncu.can
                self.oyuncu.zombi_temas(dt, z.hasar)
                if self.oyuncu.can < onceki_can:
                    self.juice.hasar_alindi_efekti()
                    self._son_hasar_alindi = True
                    
                if self.oyuncu.oldu:
                    self._bitis()
                    return

        # --- Boss güncelleme ---
        for b in list(self.bosslar):
            ozel_tetik, faz_degisti = b.update(dt, self.oyuncu.x, self.oyuncu.y, self._hareket_cozucu)
            if ozel_tetik:
                efektler = b.ozel_saldiri_uygula(self.oyuncu, self.parcaciklar, self.zehir_havuzlari)
                for ef in efektler:
                    if ef[0] == "sarsinti":
                        self.sarsinti = max(self.sarsinti, ef[1])
                    elif ef[0] == "parcacik_patlama":
                        px, py, renk = ef[1]
                        self.parcaciklar.extend(kan_parcaciklari(px, py, 10, renk))
                    elif ef[0] == "elektrik_dalgasi":
                        self.juice.patlama_efekti(0.6)
            if faz_degisti:
                self.sarsinti = max(self.sarsinti, 0.25)
            # Boss temas hasarı
            if b.oyuncuya_yakin_mi(self.oyuncu.x, self.oyuncu.y):
                onceki_can = self.oyuncu.can
                self.oyuncu.zombi_temas(dt, b.hasar)
                if self.oyuncu.can < onceki_can:
                    self.juice.hasar_alindi_efekti()
                    self._son_hasar_alindi = True
                if self.oyuncu.oldu:
                    self._bitis()
                    return

        # Tüm hedefler (zombi + boss) birleştirilerek mermi çarpışması kontrol ediliyor
        tum_hedefler = list(self.zombiler) + list(self.bosslar)

        for m in list(self.mermiler):
            if not m.alive(): continue
            if m.tip in ("roket", "seken_bomba", "delici_patlayan"):
                for z in tum_hedefler:
                    if math.hypot(z.x - m.x, z.y - m.y) < (z.yari_cap + m.yari_cap):
                        self.patlamalar.append(Patlama(m.x, m.y, m.patlama_r))
                        m.kill()
                        break
            else:
                for z in tum_hedefler:
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
                        if getattr(z, "son_vurus_headshot", False):
                            self.sayilar.append(HarasarSayisi(z.x, z.y - 22, "HEADSHOT!", (255, 30, 30), True))
                        if oldu:
                            if z in self.bosslar.sprites():
                                self._boss_oldu(z)
                            else:
                                self._zombi_oldu(z)
                        if not m.alive():
                            break

        # Ömrü biten patlayıcı mermiler için patlama oluştur
        # (Bu mermiler update() içinde kill() edilip patlama_hazir=True olmuş olabilir)
        # Not: kill() sonrası mermiler listeden çıkar, bu yüzden update döngüsünde yakalanmalı

        for p in self.patlamalar[:]:
            p.update(dt)
            if not p.hasar_verildi:
                tum_canlilar = list(self.zombiler) + list(self.bosslar)
                oldukler = p.zombi_hasari_ver_liste(tum_canlilar, self.oyuncu.hasar_carpani * p.r * 1.5)
                for z in oldukler:
                    self.sayilar.append(HarasarSayisi(z.x, z.y, self.oyuncu.hasar_carpani * p.r * 1.5, SARI, True))
                    if z in self.bosslar.sprites():
                        self._boss_oldu(z)
                    else:
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
                if self.oyuncu.oldu:
                    self._bitis()
                    return

        self.parcaciklar = [p for p in self.parcaciklar if p.update(dt)]
        self.sayilar = [s for s in self.sayilar if s.update(dt)]
        self.basarimlar = [b for b in self.basarimlar if b.update(dt)]
        # Pool parçacıkları güncelle (draw'da dt=0 yerine burada)
        for p in self.parcacik_pool._havuz:
            if p.aktif:
                p.guncelle(dt)

        
        if self.puan_sis.yeni_seviye_flag:
            self.puan_sis.yeni_seviye_flag = False
            self.basarimlar.append(BasarimBildirimi(f"SEVİYE {self.puan_sis.seviye}!", "Tüm istatistiklerin artıyor!"))
            self.level_anim_sure = 0.8

        if self.oyuncu.yoruldu_mu:
            self.sayilar.append(HarasarSayisi(self.oyuncu.x, self.oyuncu.y, "Yoruldum!", KIRMIZI))

        if self.sarsinti > 0: self.sarsinti -= dt
        if self.hikaye_bildirim_sayaci > 0:
            self.hikaye_bildirim_sayaci -= dt

        # ── Büyük Dünya: Sürekli spawn + Hikaye + Kamera ──
        self.spawn_sis.guncelle(dt, self.oyuncu.x, self.oyuncu.y)
        self.hikaye_yon.guncelle(dt)

        # Günlük noktaları
        mesaj = self.dunya.gunluk_kontrol(self.oyuncu.x, self.oyuncu.y)
        if mesaj:
            self.hikaye_bildirimi = mesaj
            self.hikaye_bildirim_sayaci = 3.0
            self.puan_sis.para += 120
            self.basarim_sis.istatistik_guncelle("terminal_okunan")
            self.basarim_sis.kontrol_et()

        # Bölge takibi
        bolge_key = self.dunya.oyuncu_bolgesi(self.oyuncu.x, self.oyuncu.y)
        if bolge_key and bolge_key in self.dunya.bolgeler:
            self.gecilen_bolgeler.add(self.dunya.bolgeler[bolge_key]["isim"])

        self.boss_giris.update(dt)

        self.radyo_sure = max(0.0, self.radyo_sure - dt)

        # Terminal
        terminal = self.dunya.terminal_yakin(self.oyuncu.x, self.oyuncu.y)
        if terminal and tuslar.get("etkilesim"):
            self.terminal_satirlari = self.dunya.terminal_oku(terminal)
            self.terminal_sure = 4.0
            self.basarim_sis.istatistik_guncelle("terminal_okunan")
            self.hikaye_yon.olay_isle("terminal_oku")
        self.terminal_sure = max(0.0, self.terminal_sure - dt)

        for npc in self.npc_liste:
            npc.guncelle(dt)
            if npc.yakin_mi(self.oyuncu.x, self.oyuncu.y) and tuslar.get("etkilesim"):
                satir = npc.konusmaya_gir()
                if satir:
                    self.npc_satirlari = [f"{satir.speaker}: {satir.text}"]
                    self.npc_sure = 4.0
                    self.basarim_sis.istatistik_guncelle("npc_konusulan")
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

        self.level_anim_sure = max(0.0, self.level_anim_sure - dt)

         # --- Müzik sistemi: tehdit seviyesine göre ---
        bolge_tehlike = self.dunya.bolge_tehlike(self.oyuncu.x, self.oyuncu.y)
        self.muzik_sis.tehdit_guncelle(
            len(self.zombiler) + len(self.bosslar),
            len(self.bosslar) > 0,
            bolge_tehlike,
        )
        self.muzik_sis.guncelle(dt)

        # --- Radyo sistemi ---
        self.radyo_sayac += dt
        if self.radyo_aktif_sure > 0:
            self.radyo_aktif_sure -= dt
        if self.radyo_sayac >= self.radyo_aralik:
            self.radyo_sayac = 0.0
            self.radyo_aralik = random.uniform(18.0, 35.0)
            idx = random.randint(0, len(RADYO_MESAJLARI) - 1)
            self.radyo_aktif_metin = RADYO_MESAJLARI[idx]
            self.radyo_aktif_sure = 4.5

        # --- Başarım çıktısı ---
        veri = self.basarim_sis.bildirim_al()
        if veri:
            self.basarim_bildirim_veri = veri
            self.basarim_bildirim_sayac = 3.5
        if self.basarim_bildirim_sayac > 0:
            self.basarim_bildirim_sayac -= dt

        # --- Başarım istatistikleri sürekli güncelleme ---
        self.basarim_sis.istatistik_ayarla("dalga", bolge_tehlike)
        self.basarim_sis.istatistik_ayarla("para", self.puan_sis.para)
        self.basarim_sis.istatistik_ayarla("max_kombo", self.puan_sis.combo)
        self.basarim_sis.istatistik_ayarla("oldurulen", self.oldurulen_zombi)
        self.dalga_sure_sayac += dt

        # ── Kamera güncelleme (her frame sonunda) ──
        is_sprinting = tuslar.get("sprint", False)
        is_aiming = pygame.mouse.get_pressed()[2]  # Sağ tık
        self.kamera.guncelle(dt, self.oyuncu.x, self.oyuncu.y, is_aiming, is_sprinting)
        if self.sarsinti > 0:
            self.kamera.sarsinti_ekle(self.sarsinti)

        # Zafer kontrolü
        if self.hikaye_yon.zafer:
            self._bitis(zafer=True)


    def _zombi_oldu(self, z):
        if not z.alive(): return
        if z.tip == "patlayan":
            self.patlamalar.append(Patlama(z.x, z.y, 120))
            if z.patlama_hasar_mesafe(self.oyuncu.x, self.oyuncu.y) < 120 + self.oyuncu.yari_cap:
                self.oyuncu.hasar_al(40)
                
        self.parcaciklar.extend(kan_parcaciklari(z.x, z.y, 18))
        # Pool tabanlı parçacıklar
        self.parcacik_pool.kan_fickirti(z.x, z.y, 12, z.renk)
        elde_puan, elde_para = self.puan_sis.zombi_oldu(z.skor, z.para, baz_xp=25, combo_suresi_ek=self.oyuncu.yukseltmeler.get("combo", 0)*0.5)
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
        efekt = aktif_veri.get("efekt", "yok")
        if efekt != "yok":
            self.gorev_sis.olay_isle("element_oldurme", efekt)
        self.gorev_sis.silah_kullanildi(self.oyuncu.aktif_silah, True)
        # Meta vampir
        if hasattr(self.oyuncu, "_meta_vampir") and self.oyuncu._meta_vampir > 0:
            self.oyuncu.can_doldur(self.oyuncu._meta_vampir)
        # Başarım istatistikleri
        self.basarim_sis.istatistik_guncelle("oldurulen")
        if z.tip == "zehirli":
            self.basarim_sis.istatistik_guncelle("zehirli_oldurulen")
        elif z.tip == "patlayan":
            self.basarim_sis.istatistik_guncelle("patlayan_oldurulen")
        if efekt == "yanma":
            self.basarim_sis.istatistik_guncelle("ates_oldurulen")
        elif efekt == "donma":
            self.basarim_sis.istatistik_guncelle("donma_oldurulen")
        elif efekt == "sok":
            self.basarim_sis.istatistik_guncelle("sok_oldurulen")
        elif efekt == "zehir":
            self.basarim_sis.istatistik_guncelle("zehir_efekt_oldurulen")
        if getattr(z, "son_vurus_headshot", False):
            self.basarim_sis.istatistik_guncelle("headshot")
        self.basarim_sis.kontrol_et()
        z.kill()
        self.oldurulen_zombi += 1

    def _boss_oldu(self, b):
        """Boss öldüğünde özel ödül ve efekt."""
        if not b.alive(): return
        self.parcaciklar.extend(kan_parcaciklari(b.x, b.y, 40, b.renk))
        elde_puan, elde_para = self.puan_sis.zombi_oldu(b.skor, b.para, baz_xp=100, combo_suresi_ek=self.oyuncu.yukseltmeler["combo"]*0.5)
        self.sayilar.append(HarasarSayisi(b.x, b.y - 30, f"+{elde_para}$", ALTIN, True))
        self.sarsinti = 0.5
        self.juice.patlama_efekti(1.5)
        self.juice.hit_freeze(0.08, 0.8)
        self.hit_markerlar.append(HitMarker(b.x, b.y - 20))
        self.gorev_sis.olay_isle("oldurme")
        self.gorev_sis.olay_isle("boss_oldurme")
        # Hikaye: boss öldü bildirimi
        bolge_key = self.dunya.oyuncu_bolgesi(b.x, b.y)
        if bolge_key:
            self.spawn_sis.boss_oldu(bolge_key)
            self.hikaye_yon.olay_isle("boss_oldu", b.boss_tipi)
        # Boss drop (birden fazla)
        droplar = b.drop_olustur()
        if droplar:
            for d in droplar:
                self.droplar.add(d)
        # Meta vampir
        if hasattr(self.oyuncu, "_meta_vampir") and self.oyuncu._meta_vampir > 0:
            self.oyuncu.can_doldur(self.oyuncu._meta_vampir * 3)
        self.basarimlar.append(BasarimBildirimi(f"BOSS YOK EDİLDİ!", f"{b.isim} düşürüldü!"))
        b.kill()
        self.oldurulen_zombi += 1

    def _bitis(self, zafer=False):
        self.bitti = True
        self._zafer = zafer
        self.puan_sis.kaydet()

    def ciz(self, ekran):
        if self.is_3d:
            self.raycaster.ciz(
                self.oyuncu,
                self.zombiler,
                self.mermiler,
                self.droplar,
                self.dunya.bolgeler.get(
                    self.dunya.oyuncu_bolgesi(self.oyuncu.x, self.oyuncu.y) or "karantina",
                    self.dunya.bolgeler["karantina"]
                ),
            )
            self._ciz_hud(ekran)
            self._ciz_bildirim(ekran)
            self._ciz_silah_bar(ekran)
            self._ciz_anlatim(ekran)
            return

        # ── KAMERA TABANLI ÇİZİM ──────────────────────────────
        cam_ox, cam_oy = self.kamera.offset
        zoom = self.kamera.zoom
        gorunur = self.kamera.gorunur_alan()

        # Arkaplan: Oyuncunun bulunduğu bölgenin zemin rengi
        bolge_key = self.dunya.oyuncu_bolgesi(self.oyuncu.x, self.oyuncu.y)
        bolge = self.dunya.bolgeler.get(bolge_key, self.dunya.bolgeler["karantina"])
        ekran.fill(bolge["zemin"])

        # Izgara çizgileri
        kare = bolge.get("karo", 72)
        grid_ox = int(cam_ox) % int(kare * zoom)
        grid_oy = int(cam_oy) % int(kare * zoom)
        grid_step = max(1, int(kare * zoom))
        for x in range(grid_ox, GENISLIK, grid_step):
            pygame.draw.line(ekran, bolge.get("cizgi", (24, 28, 35)), (x, 0), (x, YUKSEKLIK), 1)
        for y in range(grid_oy, YUKSEKLIK, grid_step):
            pygame.draw.line(ekran, bolge.get("cizgi", (24, 28, 35)), (0, y), (GENISLIK, y), 1)

        # Zemin detayları (kan/enkaz lekeleri) — kamera offset ile
        for (px, py, pr, pcolor) in self._zemin:
            sx = int(px * zoom + cam_ox)
            sy = int(py * zoom + cam_oy)
            if 0 <= sx <= GENISLIK and 0 <= sy <= YUKSEKLIK:
                pygame.draw.circle(ekran, pcolor, (sx, sy), max(1, int(pr * zoom)))

        # Engeller (sadece görünür olanlar)
        for r in self.dunya.gorunur_engeller(gorunur):
            rx = int(r.x * zoom + cam_ox)
            ry = int(r.y * zoom + cam_oy)
            rw = int(r.width * zoom)
            rh = int(r.height * zoom)
            rr = pygame.Rect(rx, ry, rw, rh)
            pygame.draw.rect(ekran, (35, 38, 48), rr, border_radius=max(1, int(8 * zoom)))
            pygame.draw.rect(ekran, (82, 88, 106), rr, max(1, int(3 * zoom)), border_radius=max(1, int(8 * zoom)))

        # Işıklar
        for lx, ly, renk in self.dunya.gorunur_isiklar(gorunur):
            sx, sy = self.kamera.dunya_to_ekran(lx, ly)
            halo_r = int(80 * zoom)
            halo = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*renk, 70), (halo_r, halo_r), halo_r)
            ekran.blit(halo, (sx - halo_r, sy - halo_r))

        # Landmark'lar
        for lx, ly, isim, renk in self.dunya.gorunur_landmarks(gorunur):
            sx, sy = self.kamera.dunya_to_ekran(lx, ly)
            pygame.draw.circle(ekran, renk, (sx, sy), max(3, int(8 * zoom)))
            lbl = self.font_kucuk.render(isim, True, renk)
            ekran.blit(lbl, (sx + 12, sy - 8))

        # Güvenli bölge sınırları (yeşil çerçeve)
        for gb in self.dunya.guvenli_bolgeler:
            gr = gb["rect"]
            gx = int(gr.x * zoom + cam_ox)
            gy = int(gr.y * zoom + cam_oy)
            gw = int(gr.width * zoom)
            gh = int(gr.height * zoom)
            screen_rect = pygame.Rect(gx, gy, gw, gh)
            if screen_rect.colliderect(pygame.Rect(0, 0, GENISLIK, YUKSEKLIK)):
                pygame.draw.rect(ekran, (50, 200, 100), screen_rect, 2, border_radius=6)
                gt = self.font_kucuk.render(f"🛡 {gb['isim']}", True, (100, 255, 150))
                ekran.blit(gt, (gx + 8, gy - 18))

        # Kilitli kapılar gösterimi
        for gecit in self.dunya.gecitler:
            if not self.dunya.kapi_acik_mi(gecit.get("kilit")):
                kr = gecit["kapi_rect"]
                kx = int(kr.x * zoom + cam_ox)
                ky = int(kr.y * zoom + cam_oy)
                kw = int(kr.width * zoom)
                kh = int(kr.height * zoom)
                screen_rect = pygame.Rect(kx, ky, kw, kh)
                if screen_rect.colliderect(pygame.Rect(0, 0, GENISLIK, YUKSEKLIK)):
                    pygame.draw.rect(ekran, (180, 50, 50, 180), screen_rect, 3, border_radius=4)
                    lt = self.font_kucuk.render("🔒 KİLİTLİ", True, (255, 100, 100))
                    ekran.blit(lt, (kx + kw // 2 - lt.get_width() // 2, ky + kh // 2 - 8))

        # NPC'ler
        for npc in self.npc_liste:
            if self.kamera.gorunur_mu(npc.x, npc.y):
                sx, sy = self.kamera.dunya_to_ekran(npc.x, npc.y)
                npc.ciz(ekran, sx - npc.x, sy - npc.y)
                if npc.yakin_mi(self.oyuncu.x, self.oyuncu.y):
                    et = self.font_kucuk.render("E: Konuş", True, (255, 230, 180))
                    ekran.blit(et, (sx - 20, sy - 30))

        # Terminal ipucu
        terminal = self.dunya.terminal_yakin(self.oyuncu.x, self.oyuncu.y)
        if terminal:
            tx, ty = terminal["pos"]
            sx, sy = self.kamera.dunya_to_ekran(tx, ty)
            et = self.font_kucuk.render("E: Kaydı Oku", True, (170, 255, 170))
            ekran.blit(et, (sx - 30, sy - 30))

        # Zehir havuzları
        for zh in self.zehir_havuzlari:
            if self.kamera.gorunur_mu(zh[0], zh[1]):
                sx, sy = self.kamera.dunya_to_ekran(zh[0], zh[1])
                zr = int(zh[2] * zoom)
                alpha = int(90 * (zh[3] / zh[4]))
                s = pygame.Surface((zr * 2, zr * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (50, 255, 80, alpha), (zr, zr), zr)
                ekran.blit(s, (sx - zr, sy - zr))

        # Droplar
        for d in self.droplar:
            if self.kamera.gorunur_mu(d.rect.centerx, d.rect.centery):
                sx, sy = self.kamera.dunya_to_ekran(d.rect.centerx, d.rect.centery)
                ekran.blit(d.image, (sx - d.image.get_width() // 2, sy - d.image.get_height() // 2))

        # Nişangah
        if not self.bitti:
            self.oyuncu.ciz_nisangah(ekran, self.son_fare_pos, int(cam_ox), int(cam_oy))

        # Mermiler
        for m in self.mermiler:
            if self.kamera.gorunur_mu(m.x, m.y):
                sx, sy = self.kamera.dunya_to_ekran(m.x, m.y)
                ekran.blit(m.image, (sx - m.image.get_width() // 2, sy - m.image.get_height() // 2))

        # Düşman mermileri
        for dm in self.dusman_mermileri:
            if self.kamera.gorunur_mu(dm["x"], dm["y"]):
                sx, sy = self.kamera.dunya_to_ekran(dm["x"], dm["y"])
                pygame.draw.circle(ekran, PEMBE, (sx, sy), max(2, int(dm["r"] * zoom)))

        # Patlamalar ve parçacıklar
        for p in self.patlamalar: p.ciz(ekran)
        for p in self.parcaciklar: p.ciz(ekran)

        # Zombiler
        for z in self.zombiler:
            if self.kamera.gorunur_mu(z.x, z.y, z.yari_cap):
                sx, sy = self.kamera.dunya_to_ekran(z.x, z.y)
                ekran.blit(z.image, (sx - z.image.get_width() // 2, sy - z.image.get_height() // 2))
                # Can barı
                if z.can < z.max_can:
                    bar_gen = int(50 * zoom)
                    bar_yuk = max(2, int(6 * zoom))
                    dolu = int(bar_gen * max(0, z.can) / z.max_can)
                    pygame.draw.rect(ekran, (80, 0, 0), (sx - bar_gen // 2, sy - int(z.yari_cap * zoom) - 12, bar_gen, bar_yuk), border_radius=2)
                    if dolu > 0:
                        pygame.draw.rect(ekran, (210, 50, 50), (sx - bar_gen // 2, sy - int(z.yari_cap * zoom) - 12, dolu, bar_yuk), border_radius=2)

        # Bosslar
        for b in self.bosslar:
            if self.kamera.gorunur_mu(b.x, b.y, b.yari_cap):
                sx, sy = self.kamera.dunya_to_ekran(b.x, b.y)
                ekran.blit(b.image, (sx - b.image.get_width() // 2, sy - b.image.get_height() // 2))
            b.can_bar_ciz(ekran, GENISLIK, YUKSEKLIK, self.font_hud)

        # Oyuncu
        osx, osy = self.kamera.dunya_to_ekran(self.oyuncu.x, self.oyuncu.y)
        ekran.blit(self.oyuncu.image, (osx - self.oyuncu.image.get_width() // 2, osy - self.oyuncu.image.get_height() // 2))

        # Hasar sayıları
        for s in self.sayilar: s.ciz(ekran, self.font_sayi, self.font_sayi_b)

        # Bölge ismi göstergesi
        if bolge_key and bolge_key in self.dunya.bolgeler:
            bolge_isim = self.dunya.bolgeler[bolge_key]["isim"]
            bi = self.font_kucuk.render(f"📍 {bolge_isim}", True, (200, 200, 200))
            ekran.blit(bi, (GENISLIK - bi.get_width() - 20, YUKSEKLIK - bi.get_height() - 20))

        # Görev paneli (hikaye yöneticisinden)
        gorev_veri = self.hikaye_yon.gorev_paneli_verisi()
        if gorev_veri:
            gp_y = 140
            gpanel = pygame.Surface((350, 50), pygame.SRCALPHA)
            pygame.draw.rect(gpanel, (10, 15, 20, 180), (0, 0, 350, 50), border_radius=10)
            pygame.draw.rect(gpanel, (100, 200, 150, 150), (0, 0, 350, 50), 2, border_radius=10)
            ekran.blit(gpanel, (15, gp_y))
            gt = self.font_kucuk.render(gorev_veri["aciklama"][:45], True, (200, 255, 220))
            ekran.blit(gt, (25, gp_y + 5))
            # İlerleme barı
            bar_w = 320
            pygame.draw.rect(ekran, (30, 40, 35), (25, gp_y + 28, bar_w, 10), border_radius=4)
            dolu_w = int(bar_w * gorev_veri["yuzde"])
            if dolu_w > 0:
                pygame.draw.rect(ekran, (80, 220, 130), (25, gp_y + 28, dolu_w, 10), border_radius=4)
            if gorev_veri.get("ilerleme"):
                pt = self.font_kucuk.render(gorev_veri["ilerleme"], True, (180, 220, 200))
                ekran.blit(pt, (25 + bar_w - pt.get_width(), gp_y + 28))

        # Hikaye bildirimleri
        for metin, sure in self.hikaye_yon.bildirimler:
            alpha = min(255, int(sure * 100))
            nt = self.font_hud.render(metin, True, (100, 255, 150))
            nt.set_alpha(alpha)
            ekran.blit(nt, (GENISLIK // 2 - nt.get_width() // 2, 200))

        self._ciz_hud(ekran)
        self._ciz_bildirim(ekran)
        self._ciz_silah_bar(ekran)
        self._ciz_anlatim(ekran)
        self.oyuncu.flash_ciz(ekran)

        for b in self.basarimlar: b.ciz(ekran, self.font_kucuk, self.font_hud, GENISLIK, YUKSEKLIK)
        for h in self.hit_markerlar:
            h.ciz(ekran)
        self.gorev_sis.ciz(ekran, self.font_kucuk, self.font_hud, GENISLIK, YUKSEKLIK)
        for p in self.parcacik_pool._havuz:
            if p.aktif:
                p.ciz(ekran)

        # Juice efektleri (en üstte)
        self.juice.ciz(ekran)
        # Tehlike göstergesi
        self._ciz_tehlike_gostergesi(ekran)
        # Başarım bildirimi
        self._ciz_basarim_bildirimi(ekran)
        # Mini harita
        self._ciz_mini_harita(ekran)
        # Dalga giriş animasyonu
        if self.dalga_giris_anim and self.dalga_giris_anim.aktif:
            self.dalga_giris_anim.ciz(ekran, self.font_buyuk, self.font_kucuk, GENISLIK, YUKSEKLIK)
        # Boss giriş animasyonu
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

        # 6. Namlu ısısı
        by += 22
        isi_oran = self.oyuncu.namlu_isi / 100.0
        pygame.draw.rect(ekran, (40, 20, 20), (bx, by, bg, byk), border_radius=6)
        if isi_oran > 0:
            pygame.draw.rect(ekran, (255, 120, 40), (bx, by, int(bg * isi_oran), byk), border_radius=6)
        txt = "AŞIRI ISINMA" if self.oyuncu.namlu_kilit_sure > 0 else f"ISI: {int(self.oyuncu.namlu_isi)}"
        ekran.blit(self.font_kucuk.render(txt, True, BEYAZ), (bx + 8, by))

        # 7. Silah ısınma verimi (minigun/lazer)
        by += 22
        verim = 1.0
        if "minigun" in self.oyuncu.aktif_silah or "lazer" in self.oyuncu.aktif_silah:
            verim = 0.4 + 0.6 * max(0.0, min(1.0, self.oyuncu.ates_seri_sure / 2.0))
        pygame.draw.rect(ekran, (20, 35, 20), (bx, by, bg, byk), border_radius=6)
        pygame.draw.rect(ekran, (80, 220, 120), (bx, by, int(bg * verim), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"Isınma Verimi: %{int(verim*100)}", True, SIYAH if verim > 0.6 else BEYAZ), (bx + 8, by))

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
        
        pygame.draw.rect(ekran, (10, 10, 15, 200), (GENISLIK - 400, YUKSEKLIK - 120, 200, 100), border_radius=15)
        pygame.draw.rect(ekran, (50, 50, 60), (GENISLIK - 400, YUKSEKLIK - 120, 200, 100), 2, border_radius=15)
        
        t = self.font_mermi.render(m_metin, True, renk)
        ekran.blit(t, (GENISLIK - 300 - t.get_width()//2, YUKSEKLIK - 105))
        
        silah_isim = SILAHLAR[ak]["isim"]
        sit = self.font_kucuk.render(silah_isim, True, SILAHLAR[ak]["renk"])
        ekran.blit(sit, (GENISLIK - 300 - sit.get_width()//2, YUKSEKLIK - 45))

        if self.puan_sis.combo > 1:
            cx = GENISLIK // 2
            cy = 80
            ct = self.font_buyuk.render(f"{self.puan_sis.combo}x COMBO!", True, TURUNCU)
            ekran.blit(ct, (cx - ct.get_width() // 2, cy))

        # Hikaye paneli
        pygame.draw.rect(ekran, (10, 10, 16, 220), (20, YUKSEKLIK - 150, 450, 130), border_radius=12)
        pygame.draw.rect(ekran, (50, 70, 90), (20, YUKSEKLIK - 150, 450, 130), 2, border_radius=12)
        baslik = self.font_hud.render(self.harita_sis.aktif_hikaye_baslik, True, CAMGOBEGI)
        gorev = self.font_kucuk.render(f"Görev: {self.harita_sis.aktif_gorev}", True, BEYAZ)
        ekran.blit(baslik, (32, YUKSEKLIK - 138))
        ekran.blit(gorev, (32, YUKSEKLIK - 106))
        if self.hikaye_bildirim_sayaci > 0 and self.hikaye_bildirimi:
            bil = self.font_kucuk.render(self.hikaye_bildirimi, True, ALTIN)
            ekran.blit(bil, (32, YUKSEKLIK - 76))

    def _ciz_anlatim(self, ekran):
        self.cutscene.draw(ekran)
        self.boss_giris.draw(ekran)

        if self.radyo_aktif_sure > 0 and self.radyo_aktif_metin:
            alpha = min(255, int(255 * min(1.0, self.radyo_aktif_sure / 0.5)))
            r = self.font_kucuk.render(self.radyo_aktif_metin, True, (140, 255, 160))
            r.set_alpha(alpha)
            ekran.blit(r, (40, YUKSEKLIK - 180))

        if self.terminal_sure > 0 and self.terminal_satirlari:
            w, h = 700, 220
            x, y = GENISLIK // 2 - w // 2, YUKSEKLIK - h - 130
            pygame.draw.rect(ekran, (0, 18, 0, 240), (x, y, w, h), border_radius=8)
            pygame.draw.rect(ekran, (70, 180, 90), (x, y, w, h), 2, border_radius=8)
            for i, line in enumerate(self.terminal_satirlari[:7]):
                s = self.font_kucuk.render(line, True, (170, 255, 170))
                ekran.blit(s, (x + 20, y + 20 + i * 28))

        if self.npc_sure > 0 and self.npc_satirlari:
            w, h = 600, 100
            x, y = GENISLIK // 2 - w // 2, YUKSEKLIK - 230
            pygame.draw.rect(ekran, (20, 20, 30, 200), (x, y, w, h), border_radius=8)
            pygame.draw.rect(ekran, (200, 180, 50), (x, y, w, h), 2, border_radius=8)
            for i, line in enumerate(self.npc_satirlari[:3]):
                s = self.font_kucuk.render(line, True, (255, 230, 180))
                ekran.blit(s, (x + 20, y + 15 + i * 26))

        if self.hikaye_secimi == "bekle":
            p = self.font_hud.render("Seçim: [1] Önce Antidot  [2] Önce Tahliye", True, (255, 240, 120))
            ekran.blit(p, (GENISLIK // 2 - p.get_width() // 2, 26))

        # Bölüm hedef progress
        hedefler = self.harita_sis.aktif_harita["hikaye"]["hedefler"]
        oran = min(1.0, self.harita_sis.hikaye_asama / max(1, len(hedefler)))
        pygame.draw.rect(ekran, (35, 35, 45), (30, 165, 280, 10), border_radius=5)
        pygame.draw.rect(ekran, (90, 210, 180), (30, 165, int(280 * oran), 10), border_radius=5)

        if self.level_anim_sure > 0:
            puls = 1.0 + 0.35 * math.sin((0.8 - self.level_anim_sure) * 18)
            boyut = max(28, int(56 * puls))
            fnt = pygame.font.SysFont("Consolas", boyut, bold=True)
            txt = fnt.render("SEVİYE ATLA!", True, (255, 220, 70))
            ekran.blit(txt, (GENISLIK // 2 - txt.get_width() // 2, YUKSEKLIK // 2 - 60))
            for i in range(12):
                px = GENISLIK // 2 + int(math.sin(i * 0.5 + self.level_anim_sure * 9) * 160)
                py = YUKSEKLIK // 2 - 30 + (i * 10) % 80
                pygame.draw.circle(ekran, (255, 220, 80), (px, py), 2)

    def _ciz_silah_bar(self, ekran):
        bar_yuk = 80
        bar_y = YUKSEKLIK - bar_yuk - 20
        
        kart_gen, bosluk = 80, 10
        sahip = [k for k in SILAH_SIRASI if k in self.oyuncu.envanter]
        
        # Çok fazla silah varsa ekranın altına sığmayabilir, sadece seçili silaha en yakın olanları çizebiliriz.
        # Ya da basitçe hepsini çizelim (1920 ekranda 20-25 silah sığar).
        gosterilecek = sahip[-7:] # Ekrana sığması için son 7 silah
        
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

    def _ciz_tehlike_gostergesi(self, ekran: pygame.Surface) -> None:
        """Sağ üst köşede müzik tehdit moduna göre tehlike göstergesi."""
        renk = self.muzik_sis.tehdit_rengi
        metin = self.muzik_sis.tehdit_metin
        # Arkaplan
        pygame.draw.rect(ekran, (10, 10, 15), (GENISLIK - 240, 140, 220, 36), border_radius=8)
        pygame.draw.rect(ekran, renk, (GENISLIK - 240, 140, 220, 36), 2, border_radius=8)
        t = self.font_kucuk.render(metin, True, renk)
        ekran.blit(t, (GENISLIK - 240 + 110 - t.get_width() // 2, 148))
        # Düşman sayısı
        dusman_say = len(self.zombiler) + len(self.bosslar)
        if dusman_say > 0:
            ds = self.font_kucuk.render(f"{dusman_say} düşman aktif", True, (200, 200, 200))
            ekran.blit(ds, (GENISLIK - 240 + 110 - ds.get_width() // 2, 168))

    def _ciz_basarim_bildirimi(self, ekran: pygame.Surface) -> None:
        """Başarım açılma toast bildirimi (sağ üst köşe)."""
        if self.basarim_bildirim_sayac <= 0 or not self.basarim_bildirim_veri:
            return
        veri = self.basarim_bildirim_veri
        # Fade animasyonu
        fade = min(1.0, self.basarim_bildirim_sayac / 0.4)
        alpha = int(255 * fade)
        w, h = 380, 80
        x, y = GENISLIK // 2 - w // 2, 60
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 15, 35, 220), (0, 0, w, h), border_radius=12)
        pygame.draw.rect(panel, (160, 80, 255, 200), (0, 0, w, h), 2, border_radius=12)
        panel.set_alpha(alpha)
        ekran.blit(panel, (x, y))
        # İkon ve metin
        emoji_t = self.font_hud.render(veri.get("emoji", "🏆"), True, (255, 220, 60))
        emoji_t.set_alpha(alpha)
        ekran.blit(emoji_t, (x + 14, y + 12))
        isim_t = self.font_hud.render(f"BAŞARIM: {veri.get('isim','')}", True, (255, 220, 60))
        isim_t.set_alpha(alpha)
        ekran.blit(isim_t, (x + 50, y + 10))
        ac_t = self.font_kucuk.render(veri.get("aciklama", ""), True, (200, 200, 220))
        ac_t.set_alpha(alpha)
        ekran.blit(ac_t, (x + 50, y + 42))

    def _ciz_mini_harita(self, ekran: pygame.Surface) -> None:
        """Sağ alt köşede 160x120 mini harita."""
        mm_w, mm_h = 160, 120
        mm_x = GENISLIK - mm_w - 20
        mm_y = YUKSEKLIK - mm_h - 20
        scale_x = mm_w / GENISLIK
        scale_y = mm_h / YUKSEKLIK
        # Arkaplan
        pygame.draw.rect(ekran, (5, 8, 10), (mm_x, mm_y, mm_w, mm_h), border_radius=8)
        pygame.draw.rect(ekran, (50, 60, 70), (mm_x, mm_y, mm_w, mm_h), 1, border_radius=8)
        # Engeller
        aktif_harita = self.harita_sis.aktif_harita
        for r in aktif_harita.get("engeller", []):
            rx = int(r.x * scale_x) + mm_x
            ry = int(r.y * scale_y) + mm_y
            rw = max(3, int(r.width * scale_x))
            rh = max(3, int(r.height * scale_y))
            pygame.draw.rect(ekran, (60, 70, 80), (rx, ry, rw, rh))
        # Zombiler (kırmızı nokta)
        for z in self.zombiler:
            zx = int(z.x * scale_x) + mm_x
            zy = int(z.y * scale_y) + mm_y
            if mm_x <= zx <= mm_x + mm_w and mm_y <= zy <= mm_y + mm_h:
                pygame.draw.circle(ekran, (200, 60, 60), (zx, zy), 2)
        # Boss (mor nokta, büyük)
        for b in self.bosslar:
            bx = int(b.x * scale_x) + mm_x
            by = int(b.y * scale_y) + mm_y
            if mm_x <= bx <= mm_x + mm_w and mm_y <= by <= mm_y + mm_h:
                pygame.draw.circle(ekran, (200, 80, 255), (bx, by), 4)
        # NPC'ler (sarı)
        for npc in self.npc_liste:
            nx = int(npc.x * scale_x) + mm_x
            ny = int(npc.y * scale_y) + mm_y
            if mm_x <= nx <= mm_x + mm_w and mm_y <= ny <= mm_y + mm_h:
                pygame.draw.circle(ekran, (255, 220, 80), (nx, ny), 2)
        # Oyuncu (yeşil üçgen)
        px = int(self.oyuncu.x * scale_x) + mm_x
        py = int(self.oyuncu.y * scale_y) + mm_y
        pygame.draw.circle(ekran, (80, 255, 120), (px, py), 4)
        pygame.draw.circle(ekran, (255, 255, 255), (px, py), 4, 1)
        # Başlık
        ht = self.font_kucuk.render("RADAR", True, (100, 150, 130))
        ekran.blit(ht, (mm_x + 4, mm_y + 2))

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
