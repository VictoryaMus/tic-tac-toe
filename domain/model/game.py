from uuid import uuid4
from domain.model.board import Board

class Game:
    def __init__(self, game_id: str | None = None, board: Board | None = None, 
                 player_x_id: str | None = None, player_o_id: str | None = None,bot: bool = False, 
                 state: str = "waiting",):
        self.id: str = game_id or str(uuid4())
        self.board: Board = board or Board()
        self.player_x_id: str | None = player_x_id
        self.player_o_id: str | None = player_o_id
        self.bot: bool = bot
        self.current_player: str = "X"
        self.state: str = state 
        self.winner_id: str | None = None
        self.move_history: list[list[int]] = []

    @property
    def is_over(self) -> bool:
        return self.state in ("draw", "win")

    def switch_player(self) -> None:
        self.current_player = "O" if self.current_player == "X" else "X"

    def player_id_for_symbol(self, symbol: str) -> str | None:
        return self.player_x_id if symbol == "X" else self.player_o_id