from base64 import b64decode
from functools import wraps
from flask import request, g, jsonify, current_app


def basic_auth_credentials() -> tuple[str, str] | None:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Basic "):
        return None
    try:
        decoded = b64decode(header[6:]).decode("utf-8")
        login, password = decoded.split(":", 1)
        return login, password
    except Exception:
        return None


def authenticated(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        creds = basic_auth_credentials()
        if creds is None:
            return (jsonify({"error": "Unauthorized"}),
                    401,
                    {"WWW-Authenticate": 'Basic realm="TicTacToe"'})

        login, password = creds
        user_id = current_app.container.auth_service.authenticate(login, password)
        if user_id is None:
            return (jsonify({"error": "Invalid credentials"}),
                    401,
                    {"WWW-Authenticate": 'Basic realm="TicTacToe"'})

        g.user_id = user_id
        return fn(*args, **kwargs)
    return wrapper