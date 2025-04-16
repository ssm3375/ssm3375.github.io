from flask import Flask, jsonify, render_template, request
import os
import json
from collections import defaultdict, Counter
from urllib.parse import urlparse
from flask_cors import CORS

app = Flask(__name__, template_folder="templates")
CORS(app)

JSON_DIR = "hardware_cves"

# Global in-memory storage
cve_data = []
reference_counter = Counter()
submitter_counter = Counter()
domain_to_cves = defaultdict(list)
provider_to_cves = defaultdict(list)

def load_and_index_cves():
    for file in os.listdir(JSON_DIR):
        if not file.endswith(".json"):
            continue

        try:
            with open(os.path.join(JSON_DIR, file), 'r', encoding='utf-8') as f:
                data = json.load(f)

            cve_id = data.get("cveMetadata", {}).get("cveId", file.replace(".json", "unknown"))

            cna = data.get("containers", {}).get("cna", {})
            affected = cna.get("affected", [{}])[0]
            vendor = affected.get("vendor", "n/a").lower()
            product = affected.get("product", "n/a").lower()
            description = cna.get("descriptions", [{}])[0].get("value", "No description")
            references = cna.get("references", [])

            # Reference domains
            reference_domains = []
            for ref in references:
                url = ref.get("url")
                if url:
                    domain = urlparse(url).netloc.lower()
                    reference_domains.append(domain)
                    reference_counter[domain] += 1
                    domain_to_cves[domain].append(cve_id)

            assigner = data.get("cveMetadata", {}).get("assignerShortName", "n/a").lower()

            # Providers
            providers = set()
            for container in data.get("containers", {}).values():
                if isinstance(container, dict):
                    p = container.get("providerMetadata", {}).get("shortName", "")
                    if p:
                        providers.add(p.lower())
                elif isinstance(container, list):
                    for item in container:
                        p = item.get("providerMetadata", {}).get("shortName", "")
                        if p:
                            providers.add(p.lower())

            submitter_counter[assigner] += 1
            provider_to_cves[assigner].append(cve_id)
            for p in providers:
                submitter_counter[p] += 1
                provider_to_cves[p].append(cve_id)

            cve_data.append({
                "cve_id": cve_id,
                "vendor": vendor,
                "product": product,
                "description": description,
                "references": references,
                "reference_domains": reference_domains,
                "assigner": assigner,
                "providers": list(providers)
            })

        except Exception as e:
            print(f"⚠️ Error reading {file}: {e}")

    print(f"✅ Loaded {len(cve_data)} CVEs from {JSON_DIR}")


# Load data
load_and_index_cves()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/cves")
def get_filtered_cves():
    vendor = request.args.get("vendor", "").lower().strip()
    product = request.args.get("product", "").lower().strip()
    domain = request.args.get("domain", "").lower().strip()

    filtered = []

    for entry in cve_data:
        if vendor and vendor != entry["vendor"]:
            continue
        if product and product != entry["product"]:
            continue
        if domain and domain not in entry["reference_domains"]:
            continue
        filtered.append(entry)

    print(f"[DEBUG] Filter request: vendor={vendor}, product={product}, domain={domain} -> {len(filtered)} CVEs")
    return jsonify(filtered)


@app.route("/api/stats/references")
def reference_stats():
    return jsonify(reference_counter.most_common())


@app.route("/api/stats/submitters")
def submitter_stats():
    return jsonify(submitter_counter.most_common())


@app.route("/includes/<name>")
def include_html(name):
    return render_template(f"includes/{name}")


if __name__ == "__main__":
    app.run(debug=True)
