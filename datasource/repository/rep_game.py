from datasource.mapper.mapper_dom_data import to_dto, to_domain
from datasource.model.dto import GameDTO
from datasource.model.models import GameRow, UserRow, ScoreRow


class GameRepository:
    def __init__(self, db):
        self.db = db

    def save(self, dto: GameDTO) -> None:
        row = self.db.session.get(GameRow, dto.id)
        if row is None:
            row = GameRow(id=dto.id)
            self.db.session.add(row)

        row.player_x_id = dto.player_x_id
        row.player_o_id = dto.player_o_id
        row.bot = dto.bot
        row.board = dto.board_matrix
        row.current_player = dto.current_player
        row.state = dto.state
        row.winner_id = dto.winner_id

        self.db.session.commit()

    def get(self, game_id: str) -> GameDTO | None:
        row = self.db.session.get(GameRow, game_id)
        if row is None:
            return None
        return self._row_to_dto(row)

    def delete(self, game_id: str) -> None:
        row = self.db.session.get(GameRow, game_id)
        if row is not None:
            self.db.session.delete(row)
            self.db.session.commit()

    def get_all(self) -> list[GameDTO]:
        rows = self.db.session.execute(self.db.select(GameRow)).scalars().all()
        return [self._row_to_dto(r) for r in rows]

    def exists(self, game_id: str) -> bool:
        return self.db.session.get(GameRow, game_id) is not None

    def list_waiting_games(self, exclude_user_id: str) -> list[dict]:
        rows = self.db.session.execute(
            self.db.select(GameRow, UserRow.login)
            .join(UserRow, GameRow.player_x_id == UserRow.id)
            .where(GameRow.state == "waiting", GameRow.player_x_id != exclude_user_id)
            .order_by(GameRow.created_at.desc())
        ).all()
        return [
            {
                "id": g.id,
                "host_login": login,
                "created_at": g.created_at.isoformat() if g.created_at else None,
            }
            for g, login in rows
        ]

    def _row_to_dto(self, row: GameRow) -> GameDTO:
        return GameDTO(
            id=row.id,
            board_matrix=row.board,
            player_x_id=row.player_x_id,
            player_o_id=row.player_o_id,
            bot=row.bot,
            current_player=row.current_player,
            state=row.state,
            winner_id=row.winner_id,
        )

    def save_score(self, game_id: str, player_x_id: str | None, player_o_id: str | None , winner_id: str | None) -> None:
        self.db.session.add(ScoreRow(
            game_id=game_id,
            player_x_id=player_x_id,
            player_o_id=player_o_id,
            winner=winner_id,
        ))
        self.db.session.commit()

    def get_scores(self, user_id: str) -> list[dict]:
        rows = self.db.session.execute(
            self.db.select(ScoreRow, UserRow.login, GameRow)
            .join(UserRow, ScoreRow.player_x_id == UserRow.id)
            .join(GameRow, ScoreRow.game_id == GameRow.id)
            .where(
                (ScoreRow.player_x_id == user_id) | (ScoreRow.player_o_id == user_id)
            )
            .order_by(ScoreRow.finished_at.desc())
        ).all()

        results = []
        for score, player_login, game in rows:
            if score.winner:
                winner_user = self.db.session.get(UserRow, score.winner)
                winner_label = winner_user.login if winner_user else "Unknown"
            elif game.state == "draw":
                winner_label = "Draw"
            elif game.state == "win" and game.bot:
                winner_label = "Bot"
            else:
                winner_label = "Unknown"

            results.append({
                "player": player_login,
                "winner": winner_label,
            })
        return results