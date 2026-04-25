"""Harita üstü hayatta kalan NPC varlıkları — genişletilmiş diyaloglar."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
import pygame


@dataclass(slots=True)
class NPCLine:
    speaker: str
    text: str


NPC_DIALOGUES: dict[str, list[NPCLine]] = {
    "saglikci": [
        NPCLine("Sağlıkçı Ayşe", "Sargı kalmadı ama morali kaybetme."),
        NPCLine("Sağlıkçı Ayşe", "ARGUS depolarında serum sandıkları vardı."),
        NPCLine("Sağlıkçı Ayşe", "EDEN enfeksiyonu kan yoluyla yayılıyor, dikkat!"),
        NPCLine("Sağlıkçı Ayşe", "Antidotun varlığını işitmiştim. Sende mi gerçekten?"),
        NPCLine("Sağlıkçı Ayşe", "Dönmüşlerin gözlerinde hâlâ bir şey var... acı."),
    ],
    "muhendis": [
        NPCLine("Mühendis Tarık", "Şebekeyi manuel çalıştırdım, uzun sürmez."),
        NPCLine("Mühendis Tarık", "Reaktör odasına girersen ölçeri takip et."),
        NPCLine("Mühendis Tarık", "ARGUS'ın sinyal blokeri bölge 3'te aktif."),
        NPCLine("Mühendis Tarık", "Patlama zombileri... kim yaratır bunları kasıtlı olarak?"),
        NPCLine("Mühendis Tarık", "Alt tüneller hâlâ açık. Güneydoğu girişi."),
    ],
    "sivil": [
        NPCLine("Sivil Mehmet", "Ailem tünelin diğer ucunda kaldı."),
        NPCLine("Sivil Mehmet", "Ne olursa olsun bizi burada bırakma doktor."),
        NPCLine("Sivil Mehmet", "Zombiler gece daha hızlı sanki... yanılıyor muyum?"),
        NPCLine("Sivil Mehmet", "Selim Koç ekranda konuşuyor. Bizi kurtaracakmış. Yalan!"),
        NPCLine("Sivil Mehmet", "Radyo sinyalini duydum: metro son anda kapatıldı."),
    ],
}

NPC_RENKLERI: dict[str, tuple[int, int, int]] = {
    "saglikci": (80, 200, 160),
    "muhendis":  (80, 140, 255),
    "sivil":     (200, 180, 100),
}


class NPC:
    """E ile etkileşime girilen harita NPC'si."""

    def __init__(self, x: float, y: float, npc_type: str) -> None:
        self.x = x
        self.y = y
        self.npc_type = npc_type
        self.radius = 14
        self._dialog_index = 0
        self._nefes_sayac = 0.0
        self._konusuldu = False

    def guncelle(self, dt: float) -> None:
        self._nefes_sayac += dt

    def ciz(self, screen: pygame.Surface, ox: int, oy: int, kamera_x: int = 0, kamera_y: int = 0) -> None:
        pos = (int(self.x + ox), int(self.y + oy))
        renk = NPC_RENKLERI.get(self.npc_type, (160, 180, 200))
        ic_renk = tuple(min(255, c + 60) for c in renk)

        # Gölge
        pygame.draw.circle(screen, (0, 0, 0), (pos[0] + 2, pos[1] + 2), self.radius)
        # Dış halka (nefes efekti)
        puls = int(self.radius + 3 + 2 * math.sin(self._nefes_sayac * 2))
        s = pygame.Surface((puls * 2 + 4, puls * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*renk, 60), (puls + 2, puls + 2), puls)
        screen.blit(s, (pos[0] - puls - 2, pos[1] - puls - 2))

        pygame.draw.circle(screen, renk, pos, self.radius)
        pygame.draw.circle(screen, ic_renk, pos, self.radius - 5)

        # "E" tıklama ipucu
        yakin_text = pygame.font.SysFont("Consolas", 13)
        if not self._konusuldu:
            et = yakin_text.render("[E]", True, (255, 255, 200))
            screen.blit(et, (pos[0] - et.get_width() // 2, pos[1] - self.radius - 20))

    def yakin_mi(self, px: float, py: float, limit: float = 80.0) -> bool:
        return math.hypot(self.x - px, self.y - py) <= limit

    def konusmaya_gir(self) -> NPCLine | None:
        """Her çağrıda sıradaki diyalog satırını döndür."""
        satirlar = NPC_DIALOGUES.get(self.npc_type, [])
        if not satirlar:
            return None
        satir = satirlar[self._dialog_index % len(satirlar)]
        self._dialog_index += 1
        self._konusuldu = True
        return satir

    def satirlar(self) -> list[NPCLine]:
        return NPC_DIALOGUES.get(self.npc_type, [])
