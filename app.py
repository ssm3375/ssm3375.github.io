from flask import Flask, jsonify, send_from_directory, render_template
import os
import json

app = Flask(__name__)  # will now look in templates/

JSON_DIR = "hardware_cves"  # adjust if needed

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/files")
def list_files():
    files = [f for f in os.listdir(JSON_DIR) if f.endswith(".json")]
    return jsonify(sorted(files))

@app.route("/file/<filename>")
def get_file(filename):
    filepath = os.path.join(JSON_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract key fields (safe defaults)
    cna = data.get("containers", {}).get("cna", {})
    meta = data.get("cveMetadata", {})

    parsed = {
        "cve_id": meta.get("cveId"),
        "vendor": cna.get("affected", [{}])[0].get("vendor", "N/A"),
        "product": cna.get("affected", [{}])[0].get("product", "N/A"),
        "description": cna.get("descriptions", [{}])[0].get("value", "No description"),
        "references": [ref.get("url") for ref in cna.get("references", []) if "url" in ref],
        "raw": data  # optionally include full JSON for detail view
    }

    return jsonify(parsed)

# ✅ Add this route so includes/*.html works
@app.route("/includes/<name>")
def include_html(name):
    return render_template(f"includes/{name}")

if __name__ == "__main__":
    app.run(debug=True)
