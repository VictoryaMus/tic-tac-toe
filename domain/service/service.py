from domain.model.game import Game
from domain.model.board import Board

class GameService:
    def validate_the_move(self, game: Game, row: int, col: int):
        if game.is_over:
            raise ValueError("Game is already over")
        if not (0 <= row < 3 and 0 <= col < 3):
            raise ValueError("Coordinates out of range")
        if game.board.get_cell(row, col) != " ":
            raise ValueError("Cell is already taken")

    def check_winner(self, board: Board, player: str) -> bool:
        for row in range(3):
            if all(board.get_cell(row, c) == player for c in range(3)):
                return True
        for col in range(3):
            if all(board.get_cell(r, col) == player for r in range(3)):
                return True
        if all(board.get_cell(i, i) == player for i in range(3)):
            return True
        if all(board.get_cell(i, 2 - i) == player for i in range(3)):
            return True
        return False

    def make_move(self, game: Game, row: int, col: int, player: str) -> Game:
        new_game = self._clone_game(game)
        self.validate_the_move(new_game, row, col)
        new_game.board.set_cell(row, col, player)
        if self.check_winner(new_game.board, player):
            new_game.winner_id = new_game.player_id_for_symbol(player)
            new_game.state = "win"
        elif new_game.board.is_full():
            new_game.state = "draw"

        if new_game.state == "in_progress":
            new_game.switch_player()

        return new_game

    def _clone_game(self, game: Game) -> Game:
        new_game = Game(
            game_id=game.id,
            board=game.board.clone(),
            player_x_id=game.player_x_id,
            player_o_id=game.player_o_id,
            bot= game.bot,
            state= game.state
        )
        new_game.current_player = game.current_player
        new_game.winner_id = game.winner_id
        return new_game
    
    def get_next_move(self, game: Game) -> tuple:
        best_score = -float("inf")
        best_move = None
        for row in range(3):
            for col in range(3):
                if game.board.get_cell(row, col) == " ":
                    game.board.set_cell(row, col, "O")
                    score = self._minimax(game, 0, False)
                    game.board.set_cell(row, col, " ")
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)
        return best_move

    def _minimax(self, game: Game, depth: int, is_maximizing: bool) -> int:
        if self.check_winner(game.board, "O"):
            return 10 - depth
        if self.check_winner(game.board, "X"):
            return depth - 10
        if game.board.is_full():
            return 0

        if is_maximizing:
            best = -float("inf")
            for r in range(3):
                for c in range(3):
                    if game.board.get_cell(r, c) == " ":
                        game.board.set_cell(r, c, "O")
                        best = max(best, self._minimax(game, depth + 1, False))
                        game.board.set_cell(r, c, " ")
            return best
        else:
            best = float("inf")
            for r in range(3):
                for c in range(3):
                    if game.board.get_cell(r, c) == " ":
                        game.board.set_cell(r, c, "X")
                        best = min(best, self._minimax(game, depth + 1, True))
                        game.board.set_cell(r, c, " ")
            return best