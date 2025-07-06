from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
import redis
import json
import logging


try:
    from flask_talisman import Talisman
except ImportError:
    Talisman = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gist_api")

r = None  # Will be initialized inside create_app
class DummyRedis:
    def get(self, k): return None
    def setex(self, *a, **k): pass

def create_app(test_config=None):
    global r
    app = Flask(__name__)
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    app.wsgi_app = ProxyFix(app.wsgi_app)

    if test_config:
        app.config.update(test_config)

    if not app.config.get("TESTING", False) and Talisman:
        Talisman(app, force_https=False)

    # Redis setup (skip if testing)
    if not app.config.get("TESTING", False):
        r = redis.Redis(host="redis", port=6379, decode_responses=True)
    else:
        # Dummy redis mock for testing
        r = DummyRedis()

    @app.route("/healthz")
    def health():
        return {"status": "ok"}, 200

    @app.route("/<username>", strict_slashes=False)
    def get_gists(username):
        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))
        except ValueError:
            return jsonify({"error": "Invalid pagination parameters"}), 400

        if page < 1 or not (1 <= per_page <= 100):
            return jsonify({"error": "Invalid page/per_page values"}), 400

        cache_key = f"gists:{username}:{page}:{per_page}"
        if cached := r.get(cache_key):
            logger.info(f"Serving from cache: {cache_key}")
            return jsonify(json.loads(cached))

        url = f"https://api.github.com/users/{username}/gists"
        params = {"page": page, "per_page": per_page}
        response = requests.get(url, params=params, timeout=5)

        if response.status_code == 404:
            return jsonify({"error": "User not found"}), 404
        elif response.status_code != 200:
            return jsonify({"error": "GitHub API error"}), response.status_code

        gists = [
            {
                "id": gist["id"],
                "description": gist["description"],
                "url": gist["html_url"]
            }
            for gist in response.json()
        ]

        r.setex(cache_key, 300, json.dumps(gists))
        return jsonify(gists)

    return app

if __name__ == "__main__": # pragma: no cover
    app = create_app()
    app.run(host="0.0.0.0", port=8080, debug=True)
