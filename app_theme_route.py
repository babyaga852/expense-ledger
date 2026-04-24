# ── Theme persistence ─────────────────────────────────────────────────────────
# Add this route to app.py (paste anywhere after the existing routes)

@app.route("/set-theme", methods=["POST"])
def set_theme():
    data = request.get_json()
    session["theme"] = data.get("theme", "light")
    return "", 204
