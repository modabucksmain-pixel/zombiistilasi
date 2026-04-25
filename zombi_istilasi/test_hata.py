"""Karantina bolgesinde test - zombie spawn ve carpisma."""
import sys, traceback
try:
    import pygame
    pygame.init()
    ekran = pygame.display.set_mode((1280, 720))
    
    from ekranlar.oyun_ekrani import OyunEkrani
    oe = OyunEkrani()
    oe.baslat()
    
    # Oyuncuyu Karantina'ya tasi (guvenli degil, spawn olacak)
    oe.oyuncu.x = 1500.0
    oe.oyuncu.y = 1000.0
    oe.kamera.x = 1500.0
    oe.kamera.y = 1000.0
    
    tuslar = {"yukari": False, "asagi": False, "sol": False, "sag": True, 
              "ates": True, "sprint": False, "nisan": False, "etkilesim": False,
              "ult": False, "secim1": False, "secim2": False}
    
    hatalar = []
    for i in range(500):
        try:
            oe.guncelle(0.016, tuslar, (640, 360))
            oe.ciz(ekran)
        except Exception as e:
            msg = f"Frame {i}: {type(e).__name__}: {e}"
            if msg not in [h[0] for h in hatalar]:
                hatalar.append((msg, traceback.format_exc()))
            if len(hatalar) >= 10:
                break
    
    if hatalar:
        print(f"\n=== {len(hatalar)} FARKLI HATA BULUNDU ===")
        for msg, tb in hatalar:
            print(f"\n--- {msg} ---")
            print(tb)
    else:
        print(f"\n=== 500 FRAME SORUNSUZ GECTI ===")
        print(f"Zombi sayisi: {len(oe.zombiler)}")
        print(f"Boss sayisi: {len(oe.bosslar)}")
        print(f"Oyuncu pos: ({oe.oyuncu.x:.0f}, {oe.oyuncu.y:.0f})")
        print(f"Bolge: {oe.dunya.oyuncu_bolgesi(oe.oyuncu.x, oe.oyuncu.y)}")
        print(f"Spawn toplam: {oe.spawn_sis.toplam_spawn}")
        
except Exception as e:
    print(f"\nKRITIK HATA: {e}")
    traceback.print_exc()
finally:
    pygame.quit()
