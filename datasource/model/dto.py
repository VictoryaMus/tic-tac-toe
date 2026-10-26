from typing import List, Optional


class GameDTO:
    def __init__(self,id: str,board_matrix: List[List[str]],player_x_id: Optional[str],player_o_id: Optional[str],
        bot: bool,current_player: str,state: str,winner_id: Optional[str],):
        self.id = id
        self.board_matrix = board_matrix
        self.player_x_id = player_x_id
        self.player_o_id = player_o_id
        self.bot = bot
        self.current_player = current_player
        self.state = state
        self.winner_id = winner_id