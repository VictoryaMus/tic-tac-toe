from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from datasource.model.models import UserRow

class UserService:
    def __init__(self, db):
        self.db = db

    def signup(self, login: str, password: str) -> str | None:
        login = (login or "").strip()
        if not login or not password:
            return None

        user = UserRow(
            id=str(uuid4()),
            login=login,
            password_hash=generate_password_hash(password),
        )
        self.db.session.add(user)
        try:
            self.db.session.commit()
        except IntegrityError:
            self.db.session.rollback()
            return None
        return user.id

    def authenticate(self, login: str, password: str) -> str | None:
        user = self.db.session.execute(
            self.db.select(UserRow).where(UserRow.login == login)
        ).scalar_one_or_none()
        if user is None:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        return user.id

    def get_user(self, user_id: str) -> dict | None:
        user = self.db.session.get(UserRow, user_id)
        if user is None:
            return None
        return {"id": user.id, "login": user.login}