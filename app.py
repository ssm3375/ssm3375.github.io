from flask import Flask, jsonify, render_template, request
import os
import json
from collections import defaultdict, Counter
from urllib.parse import urlparse
from flask_cors import CORS

app = Flask(__name__, template_folder="templates")
CORS(app)

JSON_DIR = "hardware_cves"  # Make sure this directory exists and contains JSON files

# Global in-memory storage
cve_data = []
reference_counter = Counter()
submitter_counter = Counter()
domain_to_cves = defaultdict(list)
provider_to_cves = defaultdict(list)

def load_and_index_cves():
    if not os.path.exists(JSON_DIR):
        print(f"❌ ERROR: JSON directory '{JSON_DIR}' not found. Please ensure it exists.")
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

            print(f"✅ Loaded {cve_id} | Vendor: {vendor} | Product: {product} | Domains: {reference_domains}")

        except Exception as e:
            print(f"⚠️ Error reading {file}: {e}")

    print(f"\n✅ Total CVEs Loaded: {len(cve_data)}")


# Load data on start
load_and_index_cves()


@app.route("/api/cves")
def get_filtered_cves():
    vendor = request.args.get("vendor", "").lower()
    product = request.args.get("product", "").lower()
    domain = request.args.get("domain", "").lower()

    print(f"🔍 Filtering for: vendor={vendor}, product={product}, domain={domain}")

    filtered = []
    for entry in cve_data:
        print(f"→ Entry: vendor={entry['vendor']}, product={entry['product']}, domains={entry['reference_domains']}")
        if vendor and vendor not in entry["vendor"]:
            continue
        if product and product not in entry["product"]:
            continue
        if domain and not any(domain in d for d in entry["reference_domains"]):
            continue
        filtered.append(entry)

    print(f"✅ Matched {len(filtered)} CVEs")
    return jsonify(filtered)


@app.route("/api/stats/references")
def reference_stats():
    return jsonify(reference_counter.most_common())


@app.route("/api/stats/submitters")
def submitter_stats():
    return jsonify(submitter_counter.most_common())




if __name__ == "__main__":
    app.run(debug=True)
