import pygame
import os
import math
import wave
import io
import struct
import random

# VERSION: 3.0 (Ultimate Realism Sound Engine)
print("Ses Sistemi v3.0 Yükleniyor... (Gerçekçi Silah Sesleri Aktif)")

class SesSistemi:
    def __init__(self):
        self.sesler = {}
        self.baslatildi = False
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
            self.dizin = os.path.join("assets", "sounds")
            if not os.path.exists(self.dizin):
                os.makedirs(self.dizin)
            self._yukle()
            self.baslatildi = True
        except Exception as e:
            print(f"Ses sistemi hatası: {e}")

    def _prosedurel_wav_uret(self, tip="ates"):
        sample_rate = 44100
        byte_io = io.BytesIO()
        
        # Detaylı Silah Ses Profilleri
        params = {
            "ates":     (0.12, 120, 0.6, 0.4, 2.0),  # Tabanca
            "ates_ak":  (0.25, 55,  0.9, 0.1, 1.2),  # AK-47 (Tok)
            "ates_smg": (0.08, 200, 0.5, 0.5, 2.5),  # SMG (Seri)
            "ates_pom": (0.40, 40,  1.0, 0.2, 3.0),  # Shotgun (Güm)
            "ates_sni": (0.80, 30,  1.0, 0.1, 0.8),  # Sniper (Yankılı)
            "ates_laz": (0.30, 800, 0.1, 0.9, 2.0),  # Lazer (Biuw)
            "ates_ale": (0.10, 100, 1.0, 0.0, 5.0),  # Alev (Fıss)
            "ates_pat": (0.60, 35,  1.0, 0.3, 1.0),  # Patlama (BOOM)
            "hasar":    (0.10, 250, 0.0, 1.0, 2.0),  # Hasar
            "olum":     (0.30, 100, 0.5, 0.5, 1.5)   # Zombi Ölüm
        }
        
        sure, frek, noise_v, sine_v, decay = params.get(tip, params["ates"])
        num_samples = int(sample_rate * sure)
        
        with wave.open(byte_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            for i in range(num_samples):
                t = float(i) / sample_rate
                # Karmaşık Sönümlenme Eğrisi
                vol = (1.0 - (float(i) / num_samples)) ** decay
                
                # Çoklu Frekans ve Gürültü Katmanları
                if "laz" in tip: # Lazer efekti için frekans kayması
                    f = frek * (1.0 - t * 0.5)
                    val = math.sin(t * f * (2 * math.pi)) * 32767
                elif "pom" in tip or "pat" in tip: # Patlama için düşük frekans ağırlığı
                    noise = (random.random() * 2 - 1) * noise_v
                    sine = math.sin(t * frek * (2 * math.pi)) * sine_v
                    val = (noise + sine) * 32767
                else: # Standart silahlar
                    noise = (random.random() * 2 - 1) * noise_v
                    sine = math.sin(t * frek * (2 * math.pi)) * sine_v
                    val = (noise + sine) * 32767
                
                # Değeri 16-bit sınırları içinde tut (Clipping)
                final_val = int(val * vol)
                if final_val > 32767: final_val = 32767
                elif final_val < -32768: final_val = -32768
                
                wav_file.writeframesraw(struct.pack('<h', final_val))
        
        byte_io.seek(0)
        return pygame.mixer.Sound(byte_io)

    def _yukle(self):
        tipler = ["ates", "ates_ak", "ates_smg", "ates_pom", "ates_sni", "ates_laz", "ates_ale", "ates_pat", "hasar", "olum"]
        
        # Gerçek dosyaları ara (Örn: assets/sounds/ates_ak.wav)
        for t in tipler:
            yol = os.path.join(self.dizin, f"{t}.wav")
            if os.path.exists(yol):
                try:
                    self.sesler[t] = pygame.mixer.Sound(yol)
                except Exception as e:
                    print(f"Ses yükleme hatası (anahtar={t}, yol={yol}): {e}")
            
            # Dosya yoksa üret
            if t not in self.sesler:
                self.sesler[t] = self._prosedurel_wav_uret(t)

    def oynat(self, isim):
        if not self.baslatildi:
            return
        if isim in self.sesler:
            self.sesler[isim].play()

ses_sis = SesSistemi()
