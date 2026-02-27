import json

from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

AUTH_TOKEN = "CHANGE_ME_TO_RANDOM_STRING"

def authorized(req):
    # token can come from a header **or** a hidden form field
    return (req.headers.get("X-Auth-Token") == AUTH_TOKEN or
            req.form.get("X-Auth-Token") == AUTH_TOKEN)

@app.post("/exec")
def exec_cmd():
    # Get the raw request body as a string
    cmd_json = request.get_json()
    cmd_text = cmd_json.get("cmd")

    print(cmd_text)

    return jsonify({"status": "success", "received": cmd_text})

# TODO
@app.post("/start")
def start():
    if not authorized(request):
        return jsonify({"error": "unauthorized"}), 401
    return "not started"

@app.get("/")
def index():
    return render_template("form.html", token=AUTH_TOKEN)

@app.get("/statuspage")
def indexsp():
    return render_template("statuspage.html", token=AUTH_TOKEN)

@app.post("/statusPageCheck")
def check():
    return jsonify({
        "command": "check",
        "returncode": "null",
    })

@app.get("/ping")
def ping():
    return "pong"

# TODO
@app.get("/status")
def get_status():
    return "null"

# @app.get("/add/<int:a>/<int:b>")
# def add_numbers(a: int, b: int):
#     # URL pattern:  /add/<a>/<b>
#     return jsonify({"a": a, "b": b, "sum": a + b})
# # http://localhost:5000/add/9/2


if __name__ == "__main__":
    # Run on all interfaces; consider using gunicorn or uvicorn for prod
    # app.run(host="0.0.0.0", port=5000, debug=False)
    app.run(host="0.0.0.0", port=5000, debug=False)