from datasource.repository.rep_game import GameRepository
from datasource.mapper.mapper_dom_data import to_dto, to_domain
from domain.service.service import GameService
from domain.service.user_service import UserService
from domain.model.game import Game


class Container:
    def __init__(self, db):
        self.db = db
        self.repo = GameRepository(db)
        self.service = GameService()
        self.auth_service = UserService(db)

    def create_game(self, player_x_id: str, bot: bool = False) -> Game:
        game = Game(
            player_x_id=player_x_id,
            bot=bot,
            state="in_progress" if bot else "waiting",
        )
        if bot:
            game.player_o_id = None
        self.repo.save(to_dto(game))
        return game

    def get_game(self, game_id: str) -> Game | None:
        dto = self.repo.get(game_id)
        return to_domain(dto) if dto else None

    def list_games(self) -> list[dict]:
        return [
            {"game_id": d.id, "state": d.state, "winner_id": d.winner_id}
            for d in self.repo.get_all()
        ]

    def list_waiting_games(self, exclude_user_id: str) -> list[dict]:
        return self.repo.list_waiting_games(exclude_user_id)

    def get_scoreboard(self, user_id: str) -> list[dict]:
        return self.repo.get_scores(user_id)

    def join_game(self, game_id: str, user_id: str) -> Game | None:
        game = self.get_game(game_id)
        if game is None:
            return None
        if game.state != "waiting":
            return None
        if game.player_x_id == user_id:
            return None
        game.player_o_id = user_id
        game.state = "in_progress"
        self.repo.save(to_dto(game))
        return game

    def play_turn(self, game_id: str, row: int, col: int, user_id: str) -> Game:
        game = self.get_game(game_id)
        if game is None:
            raise ValueError("Game not found")
        if game.state == "waiting":
            raise ValueError("Waiting for an opponent")
        if game.state == "win" or game.state == "draw":
            raise ValueError("Game is already over")

        symbol = game.current_player
        expected_player_id = game.player_id_for_symbol(symbol)

        if game.bot and symbol == "O":
            raise ValueError("It's the bot's turn")
        if expected_player_id is not None and expected_player_id != user_id:
            raise ValueError("Not your turn")

        game = self.service.make_move(game, row, col, symbol)
        self.repo.save(to_dto(game))

        if game.bot and not game.is_over and game.current_player == "O":
            move = self.service.get_next_move(game)
            if move is not None:
                game = self.service.make_move(game, move[0], move[1], "O")
                self.repo.save(to_dto(game))

        if game.state == "win" or game.state == "draw":
            self.repo.save_score(
                game_id=game.id,
                player_x_id=game.player_x_id,
                player_o_id=game.player_o_id,
                winner_id=game.winner_id,
            )

        return game

    def winner_label(self, game) -> str | None:
        if game.state == "draw":
            return "Draw"
        if game.state != "win":
            return None

        if game.bot and game.winner_id is None:
            return "Bot"

        if game.winner_id is None:
            return "Unknown"

        user = self.auth_service.get_user(game.winner_id)
        return user["login"] if user else "Unknown"

    def restart_game(self, game_id: str) -> Game | None:
        old = self.get_game(game_id)
        if old is None:
            return None
        fresh = Game(
            game_id=game_id,
            player_x_id=old.player_x_id,
            player_o_id=old.player_o_id,
            bot=old.bot,
            state=old.state,
        )
        self.repo.save(to_dto(fresh))
        return fresh