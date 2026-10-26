from domain.model.game import Game
from domain.model.board import Board


def game_to_json(game: Game, db=None) -> dict:
    status_map = {
        "waiting": "waiting",
        "in_progress": "ongoing",
        "draw": "draw",
        "win": "won",
    }

    player_x_login = None
    player_o_login = "Bot" if game.bot else None
    winner_login = None

    if db is not None:
        from datasource.model.models import UserRow
        if game.player_x_id:
            u = db.session.get(UserRow, game.player_x_id)
            player_x_login = u.login if u else None
        if game.player_o_id and not game.bot:
            u = db.session.get(UserRow, game.player_o_id)
            player_o_login = u.login if u else None
        if game.winner_id:
            u = db.session.get(UserRow, game.winner_id)
            winner_login = u.login if u else None

    return {
        "game_id": game.id,
        "state": game.state,
        "status": status_map.get(game.state, "unknown"),
        "bot": game.bot,
        "current_player": game.current_player,
        "player_x": player_x_login,
        "player_o": player_o_login,
        "winner_id": game.winner_id,
        "winner": winner_login,
        "is_over": game.is_over,
        "board": {
            "grid": [row[:] for row in game.board.board],
            "printable": _printable(game.board.board),
        },
    }


def json_to_game(data: dict, game_id: str) -> Game:
    grid = data.get("board", {}).get("grid")
    board = Board(grid) if grid else Board()
    return Game(game_id=game_id, board=board)


def _printable(grid) -> str:
    sep = "+---+---+---+"
    lines = [sep]
    for row in grid:
        lines.append("| " + " | ".join(c for c in row) + " |")
        lines.append(sep)
    return "\n".join(lines)