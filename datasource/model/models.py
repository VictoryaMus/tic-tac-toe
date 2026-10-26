from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4

db = SQLAlchemy()
class UserRow(db.Model):
    __tablename__ = "users"

    id: str = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    login: str = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash: str = db.Column(db.String(255), nullable=False)

#Game In Progress
class GameRow(db.Model):
    __tablename__ = "GameInProgress"

    id: str = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()), nullable=False,)
    player_x_id: str | None = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    player_o_id: str | None = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    bot: bool = db.Column(db.Boolean, nullable=False, default=False)
    current_player: str = db.Column(db.String(1), nullable=False, default="X")
    board: str = db.Column(db.JSON, nullable=False) 
    winner_id:  str | None = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    state: str = db.Column(db.String(20), nullable=False, default="waiting")

    created_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,)
    # updated_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow,)
    
class ScoreRow(db.Model):
    __tablename__ = "completed_games"
    id: str = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()), nullable=False,)
    game_id: str = db.Column(db.String(36), nullable=False, index=True)
    player_x_id: str | None = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    player_o_id: str | None = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    winner: str | None = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    finished_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)