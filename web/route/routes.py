from flask import Blueprint, request, jsonify
from src.di.container import Container

def create_routes(app, controller):
    @app.route("/", methods=["GET"])
    def index():
        return controller.index()

    @app.route("/", methods=["POST"])
    def start_game():
        return controller.start_game()

    @app.route("/game/<game_id>", methods=["GET"])
    def game_page(game_id):
        return controller.game_page(game_id)

    @app.route("/scoreboard", methods=["GET"])
    def scoreboard():
        return controller.scoreboard()

    @app.route("/debug")
    def debug_templates():
        return {
            "template_folder": app.template_folder,
            "root_path": app.root_path,
            "full_path": app.jinja_loader.searchpath,
        }
    
    @app.route("/game/<game_id>", methods=["POST"])
    def make_move(game_id):
        return controller.make_move(game_id)

    return app