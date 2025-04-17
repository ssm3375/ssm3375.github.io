from flask import Flask, jsonify, request
import os
import json
from collections import defaultdict, Counter
from urllib.parse import urlparse
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

JSON_DIR = "hardware_cves"

# Global in-memory storage
cve_data = []
reference_counter = Counter()
submitter_counter = Counter()
domain_to_cves = defaultdict(list)
provider_to_cves = defaultdict(list)
date_distribution = Counter()

def load_and_index_cves():
    if not os.path.exists(JSON_DIR):
        print(f"❌ ERROR: JSON directory '{JSON_DIR}' not found.")
        return

    print(f"📂 Loading CVEs from '{JSON_DIR}'...")

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

            reference_domains = []
            for ref in references:
                url = ref.get("url")
                if url:
                    domain = urlparse(url).netloc.lower()
                    reference_domains.append(domain)
                    reference_counter[domain] += 1
                    domain_to_cves[domain].append(cve_id)

            assigner = data.get("cveMetadata", {}).get("assignerShortName", "n/a").lower()

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

            # Date parsing
            date_str = cna.get("datePublic", data.get("published", None))
            date_obj = None
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace("Z", ""))
                    date_key = date_obj.strftime("%Y-%m")
                    date_distribution[date_key] += 1
                except Exception as e:
                    print(f"⚠️ Failed to parse date for {cve_id}: {e}")

            cve_data.append({
                "cve_id": cve_id,
                "vendor": vendor,
                "product": product,
                "description": description,
                "references": references,
                "reference_domains": reference_domains,
                "assigner": assigner,
                "providers": list(providers),
                "datePublic": date_obj.isoformat() if date_obj else None
            })

            print(f"✅ Loaded {cve_id}")

        except Exception as e:
            print(f"⚠️ Error reading {file}: {e}")

    print(f"\n✅ Total CVEs Loaded: {len(cve_data)}")

load_and_index_cves()

# ----------------------------------------
# API ROUTES
# ----------------------------------------

@app.route("/api/cves")
def get_filtered_cves():
    vendor = request.args.get("vendor", "").lower()
    product = request.args.get("product", "").lower()
    domain = request.args.get("domain", "").lower()
    keyword = request.args.get("keyword", "").lower()

    filtered = []
    for entry in cve_data:
        if vendor and vendor not in entry["vendor"]:
            continue
        if product and product not in entry["product"]:
            continue
        if domain and not any(domain in d for d in entry["reference_domains"]):
            continue
        if keyword and keyword not in entry["description"].lower():
            continue
        filtered.append(entry)

    return jsonify(filtered)


@app.route("/api/stats/summary")
def get_summary():
    return jsonify({
        "total_cves": len(cve_data),
        "unique_vendors": len(set(e["vendor"] for e in cve_data)),
        "unique_products": len(set(e["product"] for e in cve_data)),
        "unique_domains": len(reference_counter),
    })


@app.route("/api/stats/references")
def reference_stats():
    return jsonify(reference_counter.most_common())


@app.route("/api/stats/submitters")
def submitter_stats():
    return jsonify(submitter_counter.most_common())


@app.route("/api/stats/timeline")
def get_timeline():
    sorted_timeline = sorted(date_distribution.items())
    return jsonify(sorted_timeline)


@app.route("/api/vendors")
def get_all_vendors():
    vendors = sorted(set(e["vendor"] for e in cve_data))
    return jsonify(vendors)


@app.route("/api/products")
def get_all_products():
    products = sorted(set(e["product"] for e in cve_data))
    return jsonify(products)


if __name__ == "__main__":
    app.run(debug=True)
