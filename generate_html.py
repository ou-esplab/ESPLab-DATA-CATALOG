import json
import os

OUTPUT_DIR = "docs"

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def generate_page(title, catalog, category_name):
    # Extract dropdown options for filtering based on catalog keys and metadata
    # For obs: domain, dataset, temporal_resolution, variable (split key)
    # For reanalysis: dataset, temporal_resolution, variable

    keys = list(catalog["sources"].keys())
    # Parse keys differently per category
    # obs keys look like: obs/gridded/<domain>/<variable>/<temporal_resolution>/<dataset>
    # reanalysis keys look like: reanalysis/<dataset>/<temporal_resolution>/<variable>

    # Collect dropdown options
    dropdowns = {}
    if category_name == "Obs":
        dropdowns = {
            "Domain": set(),
            "Variable": set(),
            "Temporal Resolution": set(),
            "Dataset": set()
        }
        for k in keys:
            parts = k.split("/")
            # obs/gridded/<domain>/<variable>/<temporal_resolution>/<dataset>
            if len(parts) >= 6:
                _, _, domain, variable, temp_res, dataset = parts[:6]
                dropdowns["Domain"].add(domain)
                dropdowns["Variable"].add(variable)
                dropdowns["Temporal Resolution"].add(temp_res)
                dropdowns["Dataset"].add(dataset)

    elif category_name == "Reanalysis":
        dropdowns = {
            "Dataset": set(),
            "Temporal Resolution": set(),
            "Variable": set()
        }
        for k in keys:
            parts = k.split("/")
            # reanalysis/<dataset>/<temporal_resolution>/<variable>
            if len(parts) >= 4:
                _, dataset, temp_res, variable = parts[:4]
                dropdowns["Dataset"].add(dataset)
                dropdowns["Temporal Resolution"].add(temp_res)
                dropdowns["Variable"].add(variable)

    # Sort dropdown options
    for k in dropdowns:
        dropdowns[k] = sorted(dropdowns[k])

    # Begin HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>ESPLab Data Catalog - {category_name}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
h1 {{ margin-bottom: 0.5em; }}
label {{ font-weight: bold; margin-right: 0.5em; }}
select {{ margin-right: 1em; margin-bottom: 1em; }}
.dataset {{
    border: 1px solid #ccc;
    padding: 10px;
    margin-bottom: 8px;
    border-radius: 5px;
}}
.dataset b {{ font-size: 1.1em; }}
.metadata div {{ margin-left: 10px; }}
</style>
</head>
<body>
<h1>ESPLab Data Catalog - {category_name}</h1>
<div id="filters">
"""

    # Add dropdowns in HTML
    for dd_name, options in dropdowns.items():
        html += f'<label for="{dd_name}">{dd_name}:</label>'
        html += f'<select id="{dd_name}">'
        html += f'<option value="">-- All --</option>'
        for opt in options:
            html += f'<option value="{opt}">{opt}</option>'
        html += "</select>"

    html += "</div>\n<div id='datasets'>\n"

    # Add datasets container; initially empty, fill with JS for filtering
    html += "</div>\n"

    # Add JS to store data and filter
    html += """
<script>
const catalog = """
    # Embed the catalog JSON as a JS object
    html += json.dumps(catalog["sources"], indent=2)
    html += """;

function createDatasetDiv(key, data) {
  const container = document.createElement('div');
  container.className = 'dataset';

  // Dataset name bold
  const nameDiv = document.createElement('div');
  nameDiv.innerHTML = `<b>${key}</b>`;
  container.appendChild(nameDiv);

  // Description, Units, Date Range, Number of Files, Data Location
  const metaDiv = document.createElement('div');
  metaDiv.className = 'metadata';

  const desc = data.description || 'No description available';
  const units = data.metadata?.units || 'unknown';
  const date_range = data.metadata?.date_range || 'unknown';
  const n_files = data.metadata?.n_files || 'unknown';
  const urlpath = data.args?.urlpath || 'unknown';

  metaDiv.innerHTML = `
    <div><b>Description:</b> ${desc}</div>
    <div><b>Units:</b> ${units}</div>
    <div><b>Date Range:</b> ${date_range}</div>
    <div><b>Number of Files:</b> ${n_files}</div>
    <div><b>Data Location:</b> ${urlpath}</div>
  `;

  container.appendChild(metaDiv);
  return container;
}

function getKeyParts(key) {
  return key.split('/');
}

function filterDatasets() {
  const container = document.getElementById('datasets');
  container.innerHTML = '';

  const filters = {};
  ['Domain', 'Variable', 'Temporal Resolution', 'Dataset'].forEach(id => {
    const el = document.getElementById(id);
    if(el) {
      filters[id] = el.value.trim();
    }
  });

  Object.entries(catalog).forEach(([key, data]) => {
    const parts = getKeyParts(key);
    let match = true;

    if(filters['Domain'] !== undefined && filters['Domain']) {
      // obs keys: obs/gridded/<domain>/<variable>/<temporal_resolution>/<dataset>
      // reanalysis keys: no domain, so skip filter
      if(parts[0] === 'obs') {
        if(parts[2] !== filters['Domain']) match = false;
      }
    }
    if(filters['Variable'] && (parts[0] === 'obs' ? parts[3] !== filters['Variable'] : parts[3] !== filters['Variable'])) {
      match = false;
    }
    if(filters['Temporal Resolution'] && (parts[0] === 'obs' ? parts[4] !== filters['Temporal Resolution'] : parts[2] !== filters['Temporal Resolution'])) {
      match = false;
    }
    if(filters['Dataset'] && (parts[0] === 'obs' ? parts[5] !== filters['Dataset'] : parts[1] !== filters['Dataset'])) {
      match = false;
    }

    if(match) {
      container.appendChild(createDatasetDiv(key, data));
    }
  });
}

// Add event listeners to dropdowns
['Domain', 'Variable', 'Temporal Resolution', 'Dataset'].forEach(id => {
  const el = document.getElementById(id);
  if(el) {
    el.addEventListener('change', filterDatasets);
  }
});

// Initial population
filterDatasets();
</script>
</body>
</html>
"""
    return html


def main():
    obs_catalog_file = os.path.join(OUTPUT_DIR, "obs.json")
    reanalysis_catalog_file = os.path.join(OUTPUT_DIR, "reanalysis.json")

    obs_catalog = load_json(obs_catalog_file)
    reanalysis_catalog = load_json(reanalysis_catalog_file)

    # Generate Obs page
    obs_html = generate_page("ESPLab Data Catalog", obs_catalog, "Obs")
    with open(os.path.join(OUTPUT_DIR, "obs.html"), 'w') as f:
        f.write(obs_html)
    print("Generated obs.html")

    # Generate Reanalysis page
    reanalysis_html = generate_page("ESPLab Data Catalog", reanalysis_catalog, "Reanalysis")
    with open(os.path.join(OUTPUT_DIR, "reanalysis.html"), 'w') as f:
        f.write(reanalysis_html)
    print("Generated reanalysis.html")


if __name__ == "__main__":
    main()

