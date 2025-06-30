import os
import json
import yaml

OUTPUT_DIR = "docs"
OBS_JSON = os.path.join(OUTPUT_DIR, "obs.json")
REANALYSIS_JSON = os.path.join(OUTPUT_DIR, "reanalysis.json")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ESPLab Data Catalog</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 20px; }}
  select {{ margin: 5px; padding: 5px; }}
  .dataset {{ border: 1px solid #ccc; margin: 8px 0; padding: 10px; border-radius: 5px; }}
  .dataset-name {{ font-weight: bold; font-size: 1.1em; margin-bottom: 4px; }}
  .metadata {{ margin-left: 10px; font-size: 0.9em; color: #555; }}
  .hidden {{ display: none; }}
</style>
</head>
<body>
<h1>ESPLab Data Catalog</h1>

{dropdowns}

<div id="datasets-container"></div>

<script>
const catalog = {catalog_json};

const filterOrder = {filter_order};

function createDropdown(id, options, label) {{
  let sel = document.createElement("select");
  sel.id = id;
  sel.innerHTML = '<option value="">Select ' + label + '</option>';
  options.forEach(opt => {{
    let option = document.createElement("option");
    option.value = opt;
    option.textContent = opt;
    sel.appendChild(option);
  }});
  return sel;
}}

function getUniqueValues(data, key) {{
  const vals = new Set();
  for (const dsKey in data.sources) {{
    const parts = dsKey.split("/");
    // keys vary by catalog, so map keys to positions
    if (filterOrder[key] !== undefined && parts.length > filterOrder[key]) {{
      vals.add(parts[filterOrder[key]]);
    }}
  }}
  return Array.from(vals).sort();
}}

function renderDatasets(selectedFilters) {{
  const container = document.getElementById("datasets-container");
  container.innerHTML = "";
  for (const dsKey in catalog.sources) {{
    const parts = dsKey.split("/");
    let show = true;
    for (const [filterName, pos] of Object.entries(filterOrder)) {{
      const selectedVal = selectedFilters[filterName];
      if (selectedVal && parts[pos] !== selectedVal) {{
        show = false;
        break;
      }}
    }}
    if (!show) continue;

    const ds = catalog.sources[dsKey];
    const meta = ds.metadata || {{}};
    const div = document.createElement("div");
    div.className = "dataset";
    div.innerHTML = `
      <div class="dataset-name">${{parts.slice(-1)[0]}}</div>
      <div class="metadata"><strong>Description:</strong> ${{ds.description || 'No description'}}<br/>
      <strong>Date Range:</strong> ${{meta.date_range || 'unknown'}}<br/>
      <strong>Units:</strong> ${{meta.units || 'unknown'}}<br/>
      <strong>Files:</strong> ${{meta.n_files || 'unknown'}}<br/>
      <strong>Data Location:</strong> ${{meta.data_location || 'unknown'}}</div>
    `;
    container.appendChild(div);
  }}
  if (container.innerHTML === "") {{
    container.textContent = "No datasets match the selected filters.";
  }}
}}

function setupFilters() {{
  const filtersDiv = document.createElement("div");
  filtersDiv.id = "filters";

  const selectedFilters = {{}};

  // Create dropdowns in filterOrder keys order
  for (const filterName of Object.keys(filterOrder)) {{
    const options = getUniqueValues(catalog, filterName);
    const dropdown = createDropdown("filter-" + filterName, options, filterName);
    dropdown.addEventListener("change", (e) => {{
      selectedFilters[filterName] = e.target.value || null;
      renderDatasets(selectedFilters);
      // Reset subsequent dropdowns
      const keys = Object.keys(filterOrder);
      const currentIndex = keys.indexOf(filterName);
      for (let i = currentIndex + 1; i < keys.length; i++) {{
        const d = document.getElementById("filter-" + keys[i]);
        d.selectedIndex = 0;
        selectedFilters[keys[i]] = null;
      }}
    }});
    filtersDiv.appendChild(dropdown);
  }}

  document.body.insertBefore(filtersDiv, document.getElementById("datasets-container"));

  renderDatasets(selectedFilters);
}}

window.onload = setupFilters;
</script>
</body>
</html>
"""

def generate_html(catalog_path, output_path, filter_order):
    with open(catalog_path) as f:
        catalog = json.load(f)

    # Build dropdowns HTML (will be created dynamically by JS, so keep empty)
    dropdowns = ""

    with open(output_path, "w") as f:
        f.write(HTML_TEMPLATE.format(catalog_json=json.dumps(catalog), filter_order=json.dumps(filter_order), dropdowns=dropdowns))

    print(f"✅ Generated {output_path}")

if __name__ == "__main__":
    # For obs, filter order: Domain (3), Dataset (4), Temporal Resolution (5), Variable (2)
    obs_filter_order = {
        "Domain": 2,          # obs/gridded/<domain>/variable/temp_res/dataset, so domain at pos 2
        "Variable": 3,
        "TemporalResolution": 4,
        "Dataset": 5
    }
    # For your YAML obs keys, adjust the indices based on path structure

    # For reanalysis: Dataset, TemporalResolution, Variable
    reanalysis_filter_order = {
        "Dataset": 2,
        "TemporalResolution": 3,
        "Variable": 4
    }

    generate_html("docs/obs.json", "docs/obs.html", obs_filter_order)
    generate_html("docs/reanalysis.json", "docs/reanalysis.html", reanalysis_filter_order)

