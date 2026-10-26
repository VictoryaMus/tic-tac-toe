from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

@dataclass
class WebBoard:
    matrix: List[List[str]] = field(
        default_factory=lambda: [[" " for _ in range(3)] for _ in range(3)]
    )

@dataclass
class WebGame:
    id: UUID
    board: WebBoard
    player_name: str = "Player"
    current_player: str = "X"
    winner: Optional[str] = None
    is_over: bool = False