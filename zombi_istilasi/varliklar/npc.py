"""Harita üstü hayatta kalan NPC varlığı."""

from __future__ import annotations

from dataclasses import dataclass
import math
import pygame


@dataclass(slots=True)
class NPCLine:
    speaker: str
    text: str


NPC_DIALOGUES: dict[str, list[NPCLine]] = {
    "saglikci": [NPCLine("Sağlıkçı", "Sargı kalmadı, ama seni görünce umutlandım."), NPCLine("Sağlıkçı", "ARGUS depolarında serum sandıkları vardı.")],
    "muhendis": [NPCLine("Mühendis", "Şebekeyi manuel çalıştırdım, uzun sürmez."), NPCLine("Mühendis", "Reaktör odasına girersen ölçeri takip et.")],
    "sivil": [NPCLine("Sivil", "Ailem tünelin diğer ucunda kaldı."), NPCLine("Sivil", "Ne olursa olsun bizi burada bırakma doktor.")],
}


class NPC:
    """E ile etkileşime girilen basit NPC."""

    def __init__(self, x: float, y: float, npc_type: str) -> None:
        self.x = x
        self.y = y
        self.npc_type = npc_type
        self.radius = 14

    def ciz(self, screen: pygame.Surface, ox: int, oy: int) -> None:
        pos = (int(self.x + ox), int(self.y + oy))
        pygame.draw.circle(screen, (80, 140, 220), pos, self.radius)
        pygame.draw.circle(screen, (160, 220, 255), pos, self.radius - 5)

    def yakin_mi(self, px: float, py: float, limit: float = 80) -> bool:
        return math.hypot(self.x - px, self.y - py) <= limit

    def satirlar(self) -> list[NPCLine]:
        return NPC_DIALOGUES.get(self.npc_type, [])
