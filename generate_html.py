import os
import yaml
import json

# Config paths
OBS_JSON = "docs/obs.json"
REANALYSIS_JSON = "docs/reanalysis.json"
OUTPUT_DIR = "docs"
OBS_DIR = os.path.join(OUTPUT_DIR, "obs")
REANALYSIS_DIR = os.path.join(OUTPUT_DIR, "reanalysis")

OU_RED = "#841617"
OU_GOLD = "#FFB81C"

def load_catalog_json(path):
    with open(path) as f:
        return json.load(f)

def unique_sorted(lst):
    return sorted(set(lst))

def generate_obs_page(catalog):
    # Extract dropdown options
    domains = []
    datasets = []
    temporal_res = []
    variables = []

    # Build dataset dict for JS: key by domain->dataset->temporal_res->variable list of entries
    data_dict = {}

    for key, source in catalog["sources"].items():
        # key example: obs/gridded/atm/precip/daily/CMORPH
        parts = key.split("/")
#        if len(parts) < 6:
#            continue
#        _, _, domain, variable, temp, dataset = parts
        _, _, domain, variable, temp, dataset = parts[:6]
        if len(parts) > 6:
            subdataset = "/".join(parts[6:])
            dataset = f"{dataset}/{subdataset}"


        # Append to lists
        domains.append(domain)
        datasets.append(dataset)
        temporal_res.append(temp)
        variables.append(variable)

        data_dict.setdefault(domain, {})
        data_dict[domain].setdefault(dataset, {})
        data_dict[domain][dataset].setdefault(temp, {})
        data_dict[domain][dataset][temp].setdefault(variable, [])

        entry = {
            "name": dataset,
            "long_name": source["metadata"].get("long_name", "No long name"),
            "description": source.get("description","No description"),
            "units": source["metadata"].get("units", "unknown"),
            "date_range": source["metadata"].get("date_range", "unknown"),
            "files": source["metadata"].get("n_files", 0),
            "data_location": source["metadata"].get("data_location", ""),
        }
        data_dict[domain][dataset][temp][variable].append(entry)

    domains = unique_sorted(domains)
    datasets = unique_sorted(datasets)
    temporal_res = unique_sorted(temporal_res)
    variables = unique_sorted(variables)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ESPLab Data Catalog - Observations</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 20px;
    background-color: #fff;
    color: #222;
}}
h1 {{
    color: {OU_RED};
}}
label {{
    font-weight: bold;
    margin-right: 8px;
}}
select {{
    margin: 5px 15px 15px 0;
    padding: 5px;
    font-size: 1rem;
}}
.dataset-entry {{
    border: 1px solid {OU_GOLD};
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
    background: #fff8e1;
}}
.dataset-name {{
    font-weight: bold;
    font-size: 1.1em;
    color: {OU_RED};
}}
.meta-field {{
    margin-left: 10px;
}}
</style>
</head>
<body>
<h1>ESPLab Data Catalog - Observations</h1>

<div>
<label for="domain">Domain:</label>
<select id="domain">
  <option value="">-- Select Domain --</option>"""
    for d in domains:
        html += f'<option value="{d}">{d}</option>\n'
    html += "</select>"

    html += """
<label for="dataset">Dataset:</label>
<select id="dataset" disabled>
  <option value="">-- Select Dataset --</option>
</select>"""

    html += """
<label for="tempres">Temporal Resolution:</label>
<select id="tempres" disabled>
  <option value="">-- Select Temporal Resolution --</option>
</select>"""

    html += """
<label for="variable">Variable:</label>
<select id="variable" disabled>
  <option value="">-- Select Variable --</option>
</select>
</div>

<div id="datasetList"></div>

<script>
// Full catalog data:
const catalog = """ + json.dumps(data_dict) + """;

function clearAndDisable(selectEl) {
    selectEl.innerHTML = '<option value="">-- Select --</option>';
    selectEl.disabled = true;
}

function enableSelect(selectEl) {
    selectEl.disabled = false;
}

function populateSelect(selectEl, options) {
    clearAndDisable(selectEl);
    options.forEach(opt => {
        let option = document.createElement("option");
        option.value = opt;
        option.textContent = opt;
        selectEl.appendChild(option);
    });
    enableSelect(selectEl);
}

function updateDatasets() {
    const domain = document.getElementById("domain").value;
    const dataset = document.getElementById("dataset").value;
    const tempres = document.getElementById("tempres").value;
    const variable = document.getElementById("variable").value;
    const container = document.getElementById("datasetList");
    container.innerHTML = "";

    if (!domain || !dataset || !tempres || !variable) {
        // don't show datasets if any dropdown is unselected
        return;
    }

    const entries = catalog[domain]?.[dataset]?.[tempres]?.[variable];
    if (!entries || entries.length === 0) {
        container.textContent = "No datasets found for this selection.";
        return;
    }

    entries.forEach(entry => {
        const div = document.createElement("div");
        div.className = "dataset-entry";
        div.innerHTML = `
            <div class="dataset-name">${entry.name}</div>
            <div><span class="meta-field">Description:</span> ${entry.long_name}</div>
            <div><span class="meta-field">Units:</span> ${entry.units}</div>
            <div><span class="meta-field">Date Range:</span> ${entry.date_range}</div>
            <div><span class="meta-field">Files:</span> ${entry.files}</div>
            <div><span class="meta-field">Data Location:</span> ${entry.data_location}</div>
        `;
        container.appendChild(div);
    });
}

document.getElementById("domain").addEventListener("change", () => {
    const domain = document.getElementById("domain").value;
    const datasetSelect = document.getElementById("dataset");
    const tempresSelect = document.getElementById("tempres");
    const variableSelect = document.getElementById("variable");

    clearAndDisable(tempresSelect);
    clearAndDisable(variableSelect);
    document.getElementById("datasetList").innerHTML = "";

    if (!domain) {
        clearAndDisable(datasetSelect);
        return;
    }

    const datasets = Object.keys(catalog[domain]);
    populateSelect(datasetSelect, datasets);
});

document.getElementById("dataset").addEventListener("change", () => {
    const domain = document.getElementById("domain").value;
    const dataset = document.getElementById("dataset").value;
    const tempresSelect = document.getElementById("tempres");
    const variableSelect = document.getElementById("variable");
    clearAndDisable(variableSelect);
    document.getElementById("datasetList").innerHTML = "";

    if (!dataset) {
        clearAndDisable(tempresSelect);
        return;
    }

    const tempres = Object.keys(catalog[domain][dataset]);
    populateSelect(tempresSelect, tempres);
});

document.getElementById("tempres").addEventListener("change", () => {
    const domain = document.getElementById("domain").value;
    const dataset = document.getElementById("dataset").value;
    const tempres = document.getElementById("tempres").value;
    const variableSelect = document.getElementById("variable");
    document.getElementById("datasetList").innerHTML = "";

    if (!tempres) {
        clearAndDisable(variableSelect);
        return;
    }

    const vars = Object.keys(catalog[domain][dataset][tempres]);
    populateSelect(variableSelect, vars);
});

document.getElementById("variable").addEventListener("change", updateDatasets);
</script>

</body>
</html>
"""
    return html

def generate_reanalysis_page(catalog):
    # Dropdown order: Dataset, Temporal Resolution, Variable
    datasets = []
    temporal_res = []
    variables = []

    data_dict = {}

    for key, source in catalog["sources"].items():
        # key example: reanalysis/era5/daily/z850
        parts = key.split("/")
        if len(parts) < 4:
            continue
        _, dataset, temp, variable = parts[-4:]

        datasets.append(dataset)
        temporal_res.append(temp)
        variables.append(variable)

        data_dict.setdefault(dataset, {})
        data_dict[dataset].setdefault(temp, {})
        data_dict[dataset][temp].setdefault(variable, [])

        entry = {
            "name": dataset,
            "long_name": source["metadata"].get("long_name", "No long name"),
            "description": source.get("description","No description"),
            "units": source["metadata"].get("units", "unknown"),
            "date_range": source["metadata"].get("date_range", "unknown"),
            "files": source["metadata"].get("n_files", 0),
            "data_location": source["metadata"].get("data_location", ""),
        }
        data_dict[dataset][temp][variable].append(entry)

    datasets = unique_sorted(datasets)
    temporal_res = unique_sorted(temporal_res)
    variables = unique_sorted(variables)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ESPLab Data Catalog - Reanalysis</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 20px;
    background-color: #fff;
    color: #222;
}}
h1 {{
    color: {OU_RED};
}}
label {{
    font-weight: bold;
    margin-right: 8px;
}}
select {{
    margin: 5px 15px 15px 0;
    padding: 5px;
    font-size: 1rem;
}}
.dataset-entry {{
    border: 1px solid {OU_GOLD};
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
    background: #fff8e1;
}}
.dataset-name {{
    font-weight: bold;
    font-size: 1.1em;
    color: {OU_RED};
}}
.meta-field {{
    margin-left: 10px;
}}
</style>
</head>
<body>
<h1>ESPLab Data Catalog - Reanalysis</h1>

<div>
<label for="dataset">Dataset:</label>
<select id="dataset">
  <option value="">-- Select Dataset --</option>"""
    for d in datasets:
        html += f'<option value="{d}">{d}</option>\n'
    html += "</select>"

    html += """
<label for="tempres">Temporal Resolution:</label>
<select id="tempres" disabled>
  <option value="">-- Select Temporal Resolution --</option>
</select>"""

    html += """
<label for="variable">Variable:</label>
<select id="variable" disabled>
  <option value="">-- Select Variable --</option>
</select>
</div>

<div id="datasetList"></div>

<script>
const catalog = """ + json.dumps(data_dict) + """;

function clearAndDisable(selectEl) {
    selectEl.innerHTML = '<option value="">-- Select --</option>';
    selectEl.disabled = true;
}

function enableSelect(selectEl) {
    selectEl.disabled = false;
}

function populateSelect(selectEl, options) {
    clearAndDisable(selectEl);
    options.forEach(opt => {
        let option = document.createElement("option");
        option.value = opt;
        option.textContent = opt;
        selectEl.appendChild(option);
    });
    enableSelect(selectEl);
}

function updateDatasets() {
    const dataset = document.getElementById("dataset").value;
    const tempres = document.getElementById("tempres").value;
    const variable = document.getElementById("variable").value;
    const container = document.getElementById("datasetList");
    container.innerHTML = "";

    if (!dataset || !tempres || !variable) {
        return;
    }

    const entries = catalog[dataset]?.[tempres]?.[variable];
    if (!entries || entries.length === 0) {
        container.textContent = "No datasets found for this selection.";
        return;
    }

    entries.forEach(entry => {
        const div = document.createElement("div");
        div.className = "dataset-entry";
        div.innerHTML = `
            <div class="dataset-name">${entry.name}</div>
            <div><span class="meta-field">Description:</span> ${entry.long_name}</div>
            <div><span class="meta-field">Units:</span> ${entry.units}</div>
            <div><span class="meta-field">Date Range:</span> ${entry.date_range}</div>
            <div><span class="meta-field">Files:</span> ${entry.files}</div>
            <div><span class="meta-field">Data Location:</span> ${entry.data_location}</div>
        `;
        container.appendChild(div);
    });
}

document.getElementById("dataset").addEventListener("change", () => {
    const dataset = document.getElementById("dataset").value;
    const tempresSelect = document.getElementById("tempres");
    const variableSelect = document.getElementById("variable");
    clearAndDisable(variableSelect);
    document.getElementById("datasetList").innerHTML = "";

    if (!dataset) {
        clearAndDisable(tempresSelect);
        return;
    }

    const tempres = Object.keys(catalog[dataset]);
    populateSelect(tempresSelect, tempres);
});

document.getElementById("tempres").addEventListener("change", () => {
    const dataset = document.getElementById("dataset").value;
    const tempres = document.getElementById("tempres").value;
    const variableSelect = document.getElementById("variable");
    document.getElementById("datasetList").innerHTML = "";

    if (!tempres) {
        clearAndDisable(variableSelect);
        return;
    }

    const vars = Object.keys(catalog[dataset][tempres]);
    populateSelect(variableSelect, vars);
});

document.getElementById("variable").addEventListener("change", updateDatasets);
</script>

</body>
</html>
"""
    return html

def generate_index_html():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ESPLab Data Catalog</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 20px;
    background-color: #fff;
    color: #222;
}}
h1 {{
    color: {OU_RED};
    margin-bottom: 1rem;
}}
.tabs {{
  overflow: hidden;
  background-color: #f1f1f1;
  border-radius: 5px;
  margin-bottom: 20px;
}}
.tab-button {{
  background-color: inherit;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 14px 16px;
  transition: 0.3s;
  font-weight: bold;
  font-size: 1rem;
  color: {OU_RED};
}}
.tab-button:hover {{
  background-color: {OU_GOLD};
  color: #000;
}}
.tab-button.active {{
  background-color: {OU_RED};
  color: white;
}}
.tab-content {{
  display: none;
  border: 1px solid {OU_RED};
  border-radius: 5px;
  padding: 15px;
}}
.tab-content.active {{
  display: block;
}}
</style>
</head>
<body>

<h1>ESPLab Data Catalog</h1>

<div class="tabs">
  <button class="tab-button active" data-tab="obs">Observations</button>
  <button class="tab-button" data-tab="reanalysis">Reanalysis</button>
</div>

<div id="obs" class="tab-content active">
  <iframe src="obs.html" style="width:100%; height:600px; border:none;"></iframe>
</div>
<div id="reanalysis" class="tab-content">
  <iframe src="reanalysis.html" style="width:100%; height:600px; border:none;"></iframe>
</div>

<script>
const tabs = document.querySelectorAll('.tab-button');
const contents = document.querySelectorAll('.tab-content');

tabs.forEach(button => {{
    button.addEventListener('click', () => {{
        const tab = button.getAttribute('data-tab');

        tabs.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        contents.forEach(content => {{
            content.classList.remove('active');
            if(content.id === tab) {{
                content.classList.add('active');
            }}
        }});
    }});
}});
</script>

</body>
</html>
"""
    return html

def write_html(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {path}")

def main():
    os.makedirs(OBS_DIR, exist_ok=True)
    os.makedirs(REANALYSIS_DIR, exist_ok=True)

    obs_catalog = load_catalog_json(OBS_JSON)
    reanalysis_catalog = load_catalog_json(REANALYSIS_JSON)

    obs_html = generate_obs_page(obs_catalog)
    reanalysis_html = generate_reanalysis_page(reanalysis_catalog)
    index_html = generate_index_html()

    write_html(os.path.join(OUTPUT_DIR, "index.html"), index_html)
    write_html(os.path.join(OUTPUT_DIR, "obs.html"), obs_html)
    write_html(os.path.join(OUTPUT_DIR, "reanalysis.html"), reanalysis_html)

if __name__ == "__main__":
    main()

