from domain.model.game import Game
from domain.model.board import Board
from datasource.model.dto import GameDTO


def to_dto(game: Game) -> GameDTO:
    return GameDTO(
        id=game.id,
        board_matrix=game.board.board,
        player_x_id=game.player_x_id,
        player_o_id=game.player_o_id,
        bot=game.bot,
        current_player=game.current_player,
        state=game.state,
        winner_id=game.winner_id,)


def to_domain(dto: GameDTO) -> Game:
    matrix = dto.board_matrix
    if isinstance(matrix, Board):
        matrix = matrix.board

    game = Game(
        game_id=dto.id,
        board=Board(matrix),
        player_x_id=dto.player_x_id,
        player_o_id=dto.player_o_id,
        bot=dto.bot,
        state=dto.state,
    )
    game.current_player = dto.current_player
    game.winner_id = dto.winner_id
    return game