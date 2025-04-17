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

# In-memory storage
cve_data = []
reference_counter = Counter()
submitter_counter = Counter()
domain_to_cves = defaultdict(list)
provider_to_cves = defaultdict(list)
cooccurrence_counter = Counter()
vendor_product_map = defaultdict(set)

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

            vendor = affected.get("vendor", "n/a").strip().lower()
            product = affected.get("product", "n/a").strip().lower()

            vendor_product_map[vendor].add(product)

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

            assigner = data.get("cveMetadata", {}).get("assignerShortName", "n/a").strip().lower()

            providers = set()
            for container in data.get("containers", {}).values():
                if isinstance(container, dict):
                    p = container.get("providerMetadata", {}).get("shortName", "")
                    if p:
                        providers.add(p.strip().lower())
                elif isinstance(container, list):
                    for item in container:
                        p = item.get("providerMetadata", {}).get("shortName", "")
                        if p:
                            providers.add(p.strip().lower())

            submitter_counter[assigner] += 1
            provider_to_cves[assigner].append(cve_id)
            for p in providers:
                submitter_counter[p] += 1
                provider_to_cves[p].append(cve_id)

            words = [w.lower() for w in description.split() if len(w) > 3]
            for pair in itertools.combinations(set(words), 2):
                cooccurrence_counter[tuple(sorted(pair))] += 1

            date_str = cna.get("datePublic", data.get("published", None))
            date_obj = None
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace("Z", ""))
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
    print(f"📊 Vendors: {len(vendor_product_map)}\n")


@app.route("/api/vendors-products")
def get_vendors_and_products():
    # Convert sets to lists
    result = {v: sorted(list(p)) for v, p in vendor_product_map.items()}
    print(f"🧾 /api/vendors-products returned {len(result)} vendors")
    return jsonify(result)


@app.route("/api/cves")
def get_filtered_cves():
    vendor = request.args.get("vendor", "").strip().lower()
    product = request.args.get("product", "").strip().lower()
    submitter = request.args.get("submitter", "").strip().lower()
    reference = request.args.get("reference", "").strip().lower()
    keyword = request.args.get("keyword", "").strip().lower()

    print("\n🔍 /api/cves filters:")
    print(f"  Vendor:    '{vendor}'")
    print(f"  Product:   '{product}'")
    print(f"  Submitter: '{submitter}'")
    print(f"  Reference: '{reference}'")
    print(f"  Keyword:   '{keyword}'")

    results = []
    for entry in cve_data:
        if vendor and vendor != entry["vendor"]:
            continue
        if product and product != entry["product"]:
            continue
        if submitter and submitter not in ([entry["assigner"]] + entry["providers"]):
            continue
        if reference and not any(reference in d for d in entry["reference_domains"]):
            continue
        if keyword and keyword not in entry["description"].lower():
            continue
        results.append(entry)

    print(f"✅ {len(results)} CVEs matched filters.\n")
    return jsonify(results)


@app.route("/api/stats/top-submitters")
def get_top_submitters():
    return jsonify(submitter_counter.most_common(50))


@app.route("/api/stats/top-domains")
def get_top_domains():
    return jsonify(reference_counter.most_common(50))


@app.route("/api/stats/references")
def get_all_references():
    return jsonify([[k] for k in reference_counter.keys()])


@app.route("/api/stats/cooccurrence")
def get_top_cooccurrences():
    formatted = {
        f"{a}, {b}": count for (a, b), count in cooccurrence_counter.most_common(100)
    }
    return jsonify(formatted)


@app.route("/api/stats/cooccurrence/search")
def search_cooccurrences():
    word = request.args.get("word", "").lower()
    results = {
        f"{a}, {b}": count for (a, b), count in cooccurrence_counter.items()
        if word in (a, b)
    }
    sorted_results = sorted(results.items(), key=lambda x: -x[1])
    return jsonify(sorted_results[:50])


if __name__ == "__main__":
    load_and_index_cves()
    app.run(debug=True)
