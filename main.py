import os
from dotenv import load_dotenv
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask, render_template, redirect, url_for, request, session, jsonify,
)

from datasource.model.models import db
from di.container import Container
from web.module.controller import auth_bp, game_bp

load_dotenv()

def _login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper


def _register_ui_routes(app: Flask) -> None:

    @app.route("/", methods=["GET"])
    def index():
        return render_template("main.html")

    @app.route("/ui/signup", methods=["POST"])
    def ui_signup():
        login = (request.form.get("login") or "").strip()
        password = request.form.get("password") or ""
        user_id = app.container.auth_service.signup(login, password)
        if user_id is None:
            return render_template("main.html", error="Login already taken"), 409
        session["user_id"] = user_id
        return redirect(url_for("lobby"))

    @app.route("/ui/login", methods=["POST"])
    def ui_login():
        login = (request.form.get("login") or "").strip()
        password = request.form.get("password") or ""
        user_id = app.container.auth_service.authenticate(login, password)
        if user_id is None:
            return render_template("main.html", error="Invalid credentials"), 401
        session["user_id"] = user_id
        return redirect(url_for("lobby"))

    @app.route("/ui/logout", methods=["POST", "GET"])
    def ui_logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/lobby")
    @_login_required
    def lobby():
        return render_template("lobby.html")

    @app.route("/lobby/rooms")
    @_login_required
    def rooms():
        rooms_list = app.container.list_waiting_games(session["user_id"])
        return render_template("rooms.html", rooms=rooms_list)

    @app.route("/lobby/create", methods=["POST"])
    @_login_required
    def ui_create_game():
        opponent = request.form.get("opponent", "bot")
        print(">>> opponent =", repr(opponent))
        game = app.container.create_game(
            player_x_id=session["user_id"],
            bot=(opponent == "bot"),
        )
        print(">>> bot =", opponent == "bot")
        return redirect(url_for("play_game", game_id=game.id))

    @app.route("/lobby/join", methods=["POST"])
    @_login_required
    def ui_join_game():
        game_id = (request.form.get("game_id") or "").strip()
        game = app.container.join_game(game_id, session["user_id"])
        if game is None:
            rooms_list = app.container.list_waiting_games(session["user_id"])
            return render_template(
                "rooms.html",
                rooms=rooms_list,
                error="Cannot join this game",
            ), 400
        return redirect(url_for("play_game", game_id=game.id))

    @app.route("/game/<game_id>", methods=["GET", "POST"])
    @_login_required
    def play_game(game_id):
        game = app.container.get_game(game_id)
        if game is None:
            return "Game not found", 404

        if session["user_id"] not in (game.player_x_id, game.player_o_id):
            return "You are not a player in this game", 403

        if request.method == "POST":
            action = request.form.get("action")
            if action == "restart":
                app.container.restart_game(game_id)
                return redirect(url_for("play_game", game_id=game_id))

            cell = request.form.get("cell")
            if cell is not None and not game.is_over:
                row, col = divmod(int(cell), 3)
                print(f">>> play_game: game_id={game_id} user_id={session['user_id']} "
                    f"row={row} col={col} state={game.state} current={game.current_player}")
                try:
                    app.container.play_turn(game_id, row, col, session["user_id"])
                except ValueError as e:
                    print(f">>> play_turn REJECTED: {e}")
                    # pass
            return redirect(url_for("play_game", game_id=game_id))

        game = app.container.get_game(game_id)
        return render_template(
                "game.html", game=game, 
                winner_label=app.container.winner_label(game),
                )

    @app.route("/game/<game_id>/state", methods=["GET"])
    @_login_required
    def game_state(game_id):
        game = app.container.get_game(game_id)
        if game is None:
            return jsonify({"error": "not found"}), 404
        if session["user_id"] not in (game.player_x_id, game.player_o_id):
            return jsonify({"error": "forbidden"}), 403
        return jsonify({
            "board": game.board.board,
            "current_player": game.current_player,
            "state": game.state,
        })

    @app.route("/scoreboard", methods=["GET"])
    @_login_required
    def show_scoreboard():
        return render_template(
            "scoreboard.html",
            scores=app.container.get_scoreboard(session["user_id"]),
        )


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:pgpassword123@localhost:5432/tic_tac_toe",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    db.init_app(app)

    app.container = Container(db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    _register_ui_routes(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    print("Registered routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
        methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        print(f"  {methods:20s}  {rule.rule:40s}  ->  {rule.endpoint}")
    app.run(debug=True)