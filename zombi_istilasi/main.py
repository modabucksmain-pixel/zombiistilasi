import os
import sys

os.environ.setdefault("SDL_HINT_RENDER_DRIVER", "direct3d11")
os.environ.setdefault("SDL_HINT_RENDER_GPU_PRIORITY", "high")

import pygame
from ayarlar import (
    BASLIK,
    DURUM_BITTI,
    DURUM_GUNLUK,
    DURUM_MENU,
    DURUM_META,
    DURUM_OYUN,
    DURUM_OZET,
    DURUM_PAUSE,
    DURUM_SHOP,
    FPS,
    GENISLIK,
    SILAH_SIRASI,
    YUKSEKLIK,
)


def _fare_durumu_ayarla(aktif_oyun: bool) -> None:
    pygame.mouse.set_visible(not aktif_oyun)
    pygame.event.set_grab(aktif_oyun)


def _ekranlari_yukle():
    from ekranlar.ana_menu import AnaMenu
    from ekranlar.duraklama import Duraklama
    from ekranlar.gunluk import GunlukEkrani
    from ekranlar.oyun_bitti import OyunBitti
    from ekranlar.oyun_ekrani import OyunEkrani
    from ekranlar.ozet import OzetEkrani
    from ekranlar.shop import Shop

    return AnaMenu, OyunEkrani, Duraklama, OyunBitti, Shop, GunlukEkrani, OzetEkrani


def main():
    pygame.init()
    pygame.display.set_caption(BASLIK)
    flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
    ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK), flags)
    saat = pygame.time.Clock()

    AnaMenu, OyunEkrani, Duraklama, OyunBitti, Shop, GunlukEkrani, OzetEkrani = _ekranlari_yukle()

    ana_menu = AnaMenu()
    oyun_ekrani = OyunEkrani()
    duraklama = Duraklama()
    oyun_bitti = OyunBitti()
    shop = Shop()
    gunluk = GunlukEkrani()
    ozet = OzetEkrani()

    from ekranlar.meta_ekran import MetaEkran
    meta_ekran = MetaEkran()
    meta_donus = DURUM_MENU

    durum = DURUM_MENU
    _fare_durumu_ayarla(aktif_oyun=False)

    while True:
        dt = min(saat.tick(FPS) / 1000.0, 0.05)
        fare_pos = pygame.mouse.get_pos()

        secim1 = secim2 = False
        etkilesim = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    secim1 = True
                elif event.key == pygame.K_2:
                    secim2 = True
                elif event.key == pygame.K_e:
                    etkilesim = True

            if durum == DURUM_MENU:
                sonuc = ana_menu.tik_isle(event, 0)
                if sonuc == DURUM_OYUN:
                    oyun_ekrani.baslat()
                    durum = DURUM_OYUN
                elif sonuc == DURUM_META:
                    meta_ekran.baslat()
                    meta_donus = DURUM_MENU
                    durum = DURUM_META
                elif sonuc == "cikis":
                    pygame.quit()
                    sys.exit()

            elif durum == DURUM_OYUN:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        durum = DURUM_PAUSE
                        _fare_durumu_ayarla(aktif_oyun=False)
                    elif event.key == pygame.K_b:
                        durum = DURUM_SHOP
                        _fare_durumu_ayarla(aktif_oyun=False)
                    elif event.key == pygame.K_3:
                        oyun_ekrani.toggle_3d_mode()
                    elif event.key == pygame.K_m and not oyun_ekrani.is_3d:
                        oyun_ekrani.harita_degistir()
                    elif event.key == pygame.K_SPACE and oyun_ekrani.cutscene.active:
                        oyun_ekrani.cutscene.skip()
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        sahip = [k for k in SILAH_SIRASI if k in oyun_ekrani.oyuncu.envanter]
                        if idx < len(sahip):
                            oyun_ekrani.oyuncu.silah_degistir(sahip[idx])
                elif event.type == pygame.MOUSEWHEEL:
                    oyun_ekrani.oyuncu.siradaki_silah(-event.y)

            elif durum == DURUM_PAUSE:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    durum = DURUM_OYUN
                    if oyun_ekrani.is_3d:
                        _fare_durumu_ayarla(aktif_oyun=True)
                else:
                    sonuc = duraklama.tik_isle(event)
                    if sonuc == "devam":
                        durum = DURUM_OYUN
                        if oyun_ekrani.is_3d:
                            _fare_durumu_ayarla(aktif_oyun=True)
                    elif sonuc == "gunluk":
                        gunluk.ayarla(oyun_ekrani.acilan_kayitlar)
                        durum = DURUM_GUNLUK
                    elif sonuc == "meta":
                        meta_ekran.baslat()
                        meta_donus = DURUM_PAUSE
                        durum = DURUM_META
                    elif sonuc == "menu":
                        durum = DURUM_MENU
                    elif sonuc == "cikis":
                        pygame.quit()
                        sys.exit()

            elif durum == DURUM_GUNLUK:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    durum = DURUM_PAUSE

            elif durum == DURUM_SHOP:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    durum = DURUM_OYUN
                    if oyun_ekrani.is_3d:
                        _fare_durumu_ayarla(aktif_oyun=True)

                sonuc = shop.tik_isle(event, oyun_ekrani.oyuncu, oyun_ekrani.puan_sis)
                if sonuc == "devam":
                    oyun_ekrani.oyuncu.mermileri_fulle()
                    oyun_ekrani.dalga_sis.yeni_dalga_hazirla()
                    durum = DURUM_OYUN
                    if oyun_ekrani.is_3d:
                        _fare_durumu_ayarla(aktif_oyun=True)

            elif durum == DURUM_BITTI:
                sonuc = oyun_bitti.tik_isle(event)
                if sonuc == "oyun":
                    oyun_ekrani.baslat()
                    durum = DURUM_OYUN
                elif sonuc == "menu":
                    durum = DURUM_MENU

            elif durum == DURUM_OZET:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    durum = DURUM_BITTI
            elif durum == DURUM_META:
                sonuc = meta_ekran.tik_isle(event, GENISLIK, YUKSEKLIK)
                if sonuc == "devam":
                    durum = meta_donus

        if durum == DURUM_MENU:
            ana_menu.guncelle(dt)
        elif durum == DURUM_OYUN:
            keys = pygame.key.get_pressed()
            tuslar = {
                "yukari": keys[pygame.K_w] or keys[pygame.K_UP],
                "asagi": keys[pygame.K_s] or keys[pygame.K_DOWN],
                "sol": keys[pygame.K_a] or keys[pygame.K_LEFT],
                "sag": keys[pygame.K_d] or keys[pygame.K_RIGHT],
                "ates": pygame.mouse.get_pressed()[0],
                "nisan": pygame.mouse.get_pressed()[2],
                "ult": keys[pygame.K_SPACE],
                "sprint": keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT],
                "etkilesim": etkilesim,
                "secim1": secim1,
                "secim2": secim2,
            }
            oyun_ekrani.guncelle(dt, tuslar, fare_pos)

            if oyun_ekrani.oyuncu_oldu_mu:
                oyun_bitti.ayarla(oyun_ekrani.son_puan, oyun_ekrani.dalga_no, oyun_ekrani.yuksek_skorlar, "devam")
                ozet.ayarla(oyun_ekrani.dalga_no, oyun_ekrani.oldurulen_zombi_sayisi, oyun_ekrani.gecilen_bolge_listesi, False)
                durum = DURUM_OZET
            elif oyun_ekrani.zafer_mi:
                oyun_bitti.ayarla(oyun_ekrani.son_puan, oyun_ekrani.dalga_no, oyun_ekrani.yuksek_skorlar, "zafer")
                ozet.ayarla(oyun_ekrani.dalga_no, oyun_ekrani.oldurulen_zombi_sayisi, oyun_ekrani.gecilen_bolge_listesi, True)
                durum = DURUM_OZET
            elif oyun_ekrani.dalga_bitti_mi:
                oyun_ekrani.dalga_bitti_isle()  # Görev ödülleri + kristal
                durum = DURUM_SHOP
                _fare_durumu_ayarla(aktif_oyun=False)

        elif durum == DURUM_SHOP:
            shop.guncelle(dt)
        elif durum == DURUM_BITTI:
            oyun_bitti.guncelle(dt)
        elif durum == DURUM_OZET:
            ozet.guncelle(dt)
        elif durum == DURUM_META:
            meta_ekran.guncelle(dt)

        if durum == DURUM_MENU:
            ana_menu.ciz(ekran)
        elif durum == DURUM_OYUN:
            oyun_ekrani.ciz(ekran)
        elif durum == DURUM_PAUSE:
            oyun_ekrani.ciz(ekran)
            duraklama.ciz(ekran)
        elif durum == DURUM_GUNLUK:
            gunluk.ciz(ekran)
        elif durum == DURUM_SHOP:
            note = next(oyun_ekrani.yukleme_notlari)
            ekran.fill((0, 0, 0))
            f = pygame.font.SysFont("Consolas", 24)
            t = f.render(f"Kerem'in Notu: {note}", True, (220, 220, 220))
            ekran.blit(t, (80, 100))
            shop.ciz(ekran, oyun_ekrani.oyuncu, oyun_ekrani.puan_sis)
        elif durum == DURUM_OZET:
            ozet.ciz(ekran)
        elif durum == DURUM_BITTI:
            oyun_bitti.ciz(ekran)
        elif durum == DURUM_META:
            meta_ekran.ciz(ekran, GENISLIK, YUKSEKLIK)

        pygame.display.flip()


if __name__ == "__main__":
    main()
