from flask import Blueprint, request, jsonify, current_app, g

from web.auth import authenticated, basic_auth_credentials
from web.mapper.mapper_web_dom import game_to_json


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
game_bp = Blueprint("game", __name__, url_prefix="/api")


# ---------- auth (public) ----------

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    login = (data.get("login") or "").strip()
    password = data.get("password") or ""

    if not login or not password:
        return jsonify({"error": "login and password required"}), 400

    user_id = current_app.container.auth_service.signup(login, password)
    if user_id is None:
        return jsonify({"error": "login already taken"}), 409

    return jsonify({"user_id": user_id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    creds = basic_auth_credentials()
    if creds:
        login, password = creds
    else:
        data = request.get_json(silent=True) or {}
        login = data.get("login")
        password = data.get("password")

    if not login or not password:
        return jsonify({"error": "login and password required"}), 400

    user_id = current_app.container.auth_service.authenticate(login, password)
    if user_id is None:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"user_id": user_id}), 200


# ---------- users ----------

@game_bp.route("/users/<user_id>", methods=["GET"])
@authenticated
def get_user(user_id):
    user = current_app.container.auth_service.get_user(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


# ---------- games ----------

@game_bp.route("/games", methods=["POST"])
@authenticated
def create_game():
    data = request.get_json(silent=True) or {}
    opponent = data.get("opponent", "bot")

    game = current_app.container.create_game(
        player_x_id=g.user_id,
        bot=(opponent == "bot"),
    )
    return jsonify(game_to_json(game, current_app.container.db)), 201


@game_bp.route("/games", methods=["GET"])
@authenticated
def list_games():
    rooms = current_app.container.list_waiting_games(exclude_user_id=g.user_id)
    return jsonify({"games": rooms})


@game_bp.route("/games/<game_id>", methods=["GET"])
@authenticated
def get_game(game_id):
    game = current_app.container.get_game(game_id)
    if game is None:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(game_to_json(game, current_app.container.db))


@game_bp.route("/games/<game_id>/join", methods=["POST"])
@authenticated
def join_game(game_id):
    game = current_app.container.join_game(game_id, g.user_id)
    if game is None:
        return jsonify({"error": "Cannot join this game"}), 400
    return jsonify(game_to_json(game, current_app.container.db))


@game_bp.route("/games/<game_id>/moves", methods=["POST"])
@authenticated
def play_turn(game_id):
    game = current_app.container.get_game(game_id)
    if game is None:
        return jsonify({"error": "Game not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON payload"}), 400

    try:
        row = int(data["row"])
        col = int(data["col"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "'row' and 'col' must be integers"}), 400

    try:
        game = current_app.container.play_turn(game_id, row, col, g.user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(game_to_json(game, current_app.container.db))


@game_bp.route("/games/<game_id>/restart", methods=["POST"])
@authenticated
def restart_game(game_id):
    game = current_app.container.restart_game(game_id)
    if game is None:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(game_to_json(game, current_app.container.db))


@game_bp.route("/scoreboard", methods=["GET"])
@authenticated
def scoreboard():
    return jsonify({"scores": current_app.container.get_scoreboard(g.user_id)})