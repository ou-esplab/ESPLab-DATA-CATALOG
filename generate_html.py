import yaml
import html
import os
import json

# constants
CATALOG_DIR = "catalogs"
OUTPUT_DIR = "docs"

# index.html content
INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Data Catalog Home</title>
<style>
  body { font-family: Arial, sans-serif; margin: 2em; background: #f9f9f9; }
  a { display: block; margin: 1em 0; color: #2c3e50; font-size: 1.2em; }
</style>
</head>
<body>
<h1>ESPLab Data Catalog</h1>
<a href="obs.html">Observational Data</a>
<a href="reanalysis.html">Reanalysis Data</a>
</body>
</html>
"""

def generate_filtered_html(catalog, output_path, title):
    keys = list(catalog.get("sources", {}).keys())

    domain_set = set()
    variable_set = set()

    entries = []

    for key in keys:
        parts = key.split("/")
        if len(parts) < 4:
            continue
        domain = parts[2]
        variable = parts[3]
        domain_set.add(domain)
        variable_set.add(variable)

        source = catalog["sources"][key]
        desc = html.escape(source.get("description", "No description"))
        meta = source.get("metadata", {})
        units = html.escape(meta.get("units", "unknown"))
        date_range = html.escape(meta.get("date_range", "unknown"))

        entries.append({
            "domain": domain,
            "variable": variable,
            "desc": desc,
            "units": units,
            "date_range": date_range
        })

    domains_sorted = sorted(domain_set)
    variables_sorted = sorted(variable_set)

    def build_options(options):
        return "\n".join([f'<option value="{html.escape(opt)}">{html.escape(opt)}</option>' for opt in options])

    domain_options_html = '<option value="all">All</option>\n' + build_options(domains_sorted)
    variable_options_html = '<option value="all">All</option>\n' + build_options(variables_sorted)

    entries_json = json.dumps(entries, indent=2)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>{title}</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 2em; background: #f9f9f9; }}
  h1 {{ color: #2c3e50; }}
  ul {{ list-style-type: none; padding-left: 0; }}
  li {{ background: white; margin: 0.5em 0; padding: 0.75em; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .desc {{ font-weight: bold; color: #34495e; }}
  .meta {{ color: #7f8c8d; font-size: 0.9em; }}
  label {{ margin-right: 0.5em; }}
  select {{ margin-right: 2em; }}
</style>
</head>
<body>
<h1>{title}</h1>

<a href="index.html">⬅ Back to Home</a><br/>

<label for="domain-select">Domain:</label>
<select id="domain-select">
{domain_options_html}
</select>

<label for="variable-select">Variable:</label>
<select id="variable-select">
{variable_options_html}
</select>

<ul id="catalog-list"></ul>

<script>
const catalogEntries = {entries_json};

function renderCatalog(entries) {{
  const ul = document.getElementById('catalog-list');
  ul.innerHTML = '';
  if(entries.length === 0) {{
    ul.innerHTML = '<li><em>No matching datasets found.</em></li>';
    return;
  }}
  entries.forEach(e => {{
    const li = document.createElement('li');
    li.innerHTML = `<span class="desc">${{e.desc}}</span><br/><span class="meta">(${{e.units}}), ${{e.date_range}}</span>`;
    ul.appendChild(li);
  }});
}}

function filterCatalog() {{
  const domain = document.getElementById('domain-select').value;
  const variable = document.getElementById('variable-select').value;

  const filtered = catalogEntries.filter(e =>
    (domain === 'all' || e.domain === domain) &&
    (variable === 'all' || e.variable === variable)
  );
  renderCatalog(filtered);
}}

document.getElementById('domain-select').addEventListener('change', filterCatalog);
document.getElementById('variable-select').addEventListener('change', filterCatalog);

// Show all by default
renderCatalog(catalogEntries);
</script>

</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html_content)
    print(f"✅ wrote {output_path}")

def main():
    # ensure output dir exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # index.html
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        f.write(INDEX_HTML)
    print("✅ wrote index.html")

    # obs.html
    with open(os.path.join(CATALOG_DIR, "obs.yaml")) as f:
        obs_catalog = yaml.safe_load(f)
    generate_filtered_html(obs_catalog, os.path.join(OUTPUT_DIR, "obs.html"), "Observational Data Catalog")

    # reanalysis.htm

