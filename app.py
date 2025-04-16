from flask import Flask, jsonify, render_template, request
import os
import json
from collections import defaultdict, Counter
from urllib.parse import urlparse

app = Flask(__name__, template_folder="templates")

JSON_DIR = "hardware_cves"

# Global in-memory storage
cve_data = []
reference_counter = Counter()
submitter_counter = Counter()
domain_to_cves = defaultdict(list)
provider_to_cves = defaultdict(list)

def load_and_index_cves():
    global cve_data, reference_counter, submitter_counter, domain_to_cves, provider_to_cves

    for file in os.listdir(JSON_DIR):
        if not file.endswith(".json"):
            continue

        try:
            with open(os.path.join(JSON_DIR, file), 'r', encoding='utf-8') as f:
                data = json.load(f)

            cve_id = data.get("cveMetadata", {}).get("cveId", file.replace(".json", ""))
            vendor = data.get("containers", {}).get("cna", {}).get("affected", [{}])[0].get("vendor", "n/a")
            product = data.get("containers", {}).get("cna", {}).get("affected", [{}])[0].get("product", "n/a")
            description = data.get("containers", {}).get("cna", {}).get("descriptions", [{}])[0].get("value", "No description")
            references = data.get("containers", {}).get("cna", {}).get("references", [])

            domains = []
            for ref in references:
                url = ref.get("url", "")
                if url:
                    domain = urlparse(url).netloc.lower()
                    if domain:
                        reference_counter[domain] += 1
                        domain_to_cves[domain].append(cve_id)
                        domains.append(domain)

            assigner = data.get("cveMetadata", {}).get("assignerShortName", "n/a").lower()
            containers = data.get("containers", {})
            providers = set()
            for container in containers.values():
                if isinstance(container, dict):
                    prov = container.get("providerMetadata", {}).get("shortName", "")
                    if prov:
                        providers.add(prov.lower())
                elif isinstance(container, list):
                    for item in container:
                        prov = item.get("providerMetadata", {}).get("shortName", "")
                        if prov:
                            providers.add(prov.lower())

            submitter_counter[assigner] += 1
            provider_to_cves[assigner].append(cve_id)
            for p in providers:
                submitter_counter[p] += 1
                provider_to_cves[p].append(cve_id)

            cve_data.append({
                "cve_id": cve_id,
                "vendor": vendor.lower(),
                "product": product.lower(),
                "description": description,
                "references": references,
                "reference_domains": domains,
                "assigner": assigner,
                "providers": list(providers)
            })

        except Exception as e:
            print(f"⚠️ Error processing {file}: {e}")

    print(f"✅ Loaded {len(cve_data)} CVEs from {JSON_DIR}")


# Preload data on server start
load_and_index_cves()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/cves")
def get_filtered_cves():
    vendor = request.args.get("vendor", "").lower()
    product = request.args.get("product", "").lower()
    domain = request.args.get("domain", "").lower()

    filtered = []
    for entry in cve_data:
        if vendor and vendor not in entry["vendor"]:
            continue
        if product and product not in entry["product"]:
            continue
        if domain and not any(domain in d for d in entry["reference_domains"]):
            continue
        filtered.append(entry)
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