from flask import Flask, jsonify, request
import os
import json
from collections import defaultdict, Counter
from urllib.parse import urlparse
from flask_cors import CORS
from datetime import datetime
import itertools

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
vendor_year_heatmap = defaultdict(lambda: defaultdict(int))
domain_year_heatmap = defaultdict(lambda: defaultdict(int))
submitter_year_heatmap = defaultdict(lambda: defaultdict(int))
cooccurrence_counter = Counter()
vuln_type_counter = Counter()

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
            problem_types = cna.get("problemTypes", [])

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
                    date_key = date_obj.strftime("%Y")
                    date_distribution[date_key] += 1
                    vendor_year_heatmap[vendor][date_key] += 1
                    for domain in reference_domains:
                        domain_year_heatmap[domain][date_key] += 1
                    submitter_year_heatmap[assigner][date_key] += 1
                except Exception as e:
                    print(f"⚠️ Failed to parse date for {cve_id}: {e}")

            # Keyword co-occurrence
            words = [w.lower() for w in description.split() if len(w) > 3]
            for pair in itertools.combinations(set(words), 2):
                cooccurrence_counter[tuple(sorted(pair))] += 1

            # Vulnerability types
            for pt in problem_types:
                for desc in pt.get("descriptions", []):
                    d = desc.get("description", "").lower()
                    if d:
                        vuln_type_counter[d] += 1

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

# ------------------ API ------------------

@app.route("/api/stats/cooccurrence")
def get_keyword_pairs():
    return jsonify(cooccurrence_counter.most_common(100))

@app.route("/api/stats/vuln-types")
def get_vuln_types():
    return jsonify(vuln_type_counter.most_common())

@app.route("/api/stats/heatmap/vendors")
def heatmap_vendors():
    return jsonify(vendor_year_heatmap)

@app.route("/api/stats/heatmap/domains")
def heatmap_domains():
    return jsonify(domain_year_heatmap)

@app.route("/api/stats/heatmap/submitters")
def heatmap_submitters():
    return jsonify(submitter_year_heatmap)

if __name__ == "__main__":
    app.run(debug=True)
