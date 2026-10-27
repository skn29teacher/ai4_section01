import sqlite3
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

from .config import load_config
from .db import close_db


def create_app(overrides=None):
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.update(load_config(overrides))
    app.json.ensure_ascii = False
    app.teardown_appcontext(close_db)

    from .routes.api import api
    from .auth import protect_request
    app.register_blueprint(api)
    app.before_request(protect_request)

    @app.get("/")
    @app.get("/signup")
    @app.get("/login")
    @app.get("/forgot-password")
    @app.get("/posts/new")
    @app.get("/posts/<int:post_id>")
    @app.get("/posts/<int:post_id>/edit")
    @app.get("/admin/mask-rules")
    def screen(post_id=None):
        return send_from_directory(app.static_folder, "index.html")

    @app.after_request
    def headers(response):
        if not request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
        )
        return response

    @app.errorhandler(HTTPException)
    def http_error(error):
        descriptions = {400: "잘못된 요청입니다.", 404: "존재하지 않는 페이지입니다.",
                        405: "지원하지 않는 요청 방식입니다.", 413: "요청 크기가 너무 큽니다."}
        message = error.description if getattr(error, "custom_message", False) else descriptions.get(error.code, "요청을 처리할 수 없습니다.")
        return jsonify(error=message), error.code

    @app.errorhandler(sqlite3.IntegrityError)
    def integrity_error(error):
        return jsonify(error="중복되거나 유효하지 않은 데이터입니다."), 409

    @app.errorhandler(sqlite3.OperationalError)
    def database_error(error):
        app.logger.error("Database operation failed (%s)", type(error).__name__)
        return jsonify(error="DB를 사용할 수 없습니다. 초기화 상태를 확인하거나 잠시 후 다시 시도하세요."), 503

    @app.errorhandler(500)
    def server_error(error):
        return jsonify(error="처리 중 오류가 발생했습니다. 잠시 후 다시 시도하세요."), 500

    return app
