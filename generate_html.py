import os
import json

# CONFIG
OBS_JSON = "docs/obs.json"
REANALYSIS_JSON = "docs/reanalysis.json"
MODEL_JSON = "docs/model.json"

OUTPUT_DIR = "docs"
OBS_DIR = os.path.join(OUTPUT_DIR, "obs")
REANALYSIS_DIR = os.path.join(OUTPUT_DIR, "reanalysis")

OU_RED = "#841617"
OU_GOLD = "#FFB81C"
ESPLAB_LOGO = "docs/esplab_logo.png"

def load_catalog_json(path):
    with open(path) as f:
        return json.load(f)

def unique_sorted(lst):
    return sorted(set(lst))

def generate_obs_page(catalog):
    domains = []
    datasets = []
    temporal_res = []
    variables = []

    data_dict = {}
    for key, source in catalog["sources"].items():
        parts = key.split("/")
        domain = parts[2]
        variable = parts[3]
        temp = parts[4]
        dataset = "/".join(parts[5:])
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
            "description": source.get("description", "No description"),
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
<title>Observations</title>
<link rel="stylesheet" href="docs/style.css">
</head>
<body>
<div class="tabs">
  <a class="tab-button" href="obs.html">Observations</a>
  <a class="tab-button" href="reanalysis.html">Reanalysis</a>
  <a class="tab-button" href="model.html">Model</a>
</div>
<h1>Observations</h1>

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
const catalog = """ + json.dumps(data_dict) + """;

function clearAndDisable(selectEl) {
    selectEl.innerHTML = '<option value="">-- Select --</option>';
    selectEl.disabled = true;
}
function enableSelect(selectEl) { selectEl.disabled = false; }
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
    if (!domain || !dataset || !tempres || !variable) return;
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
    if (!domain) { clearAndDisable(datasetSelect); return; }
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
    if (!dataset) { clearAndDisable(tempresSelect); return; }
    const tempres = Object.keys(catalog[domain][dataset]);
    populateSelect(tempresSelect, tempres);
});
document.getElementById("tempres").addEventListener("change", () => {
    const domain = document.getElementById("domain").value;
    const dataset = document.getElementById("dataset").value;
    const tempres = document.getElementById("tempres").value;
    const variableSelect = document.getElementById("variable");
    document.getElementById("datasetList").innerHTML = "";
    if (!tempres) { clearAndDisable(variableSelect); return; }
    const vars = Object.keys(catalog[domain][dataset][tempres]);
    populateSelect(variableSelect, vars);
});
document.getElementById("variable").addEventListener("change", updateDatasets);
</script>
</body>
</html>"""
    return html


def generate_reanalysis_page(catalog):
    datasets = []
    temporal_res = []
    variables = []

    data_dict = {}

    for key, source in catalog["sources"].items():
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
            "description": source.get("description", "No description"),
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
<title>Reanalysis</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="stylesheet" href="docs/style.css">
</head>
<body>
<div class="tabs">
  <a class="tab-button" href="obs.html">Observations</a>
  <a class="tab-button" href="reanalysis.html">Reanalysis</a>
  <a class="tab-button" href="model.html">Model</a>
</div>
<h1>Reanalysis <img src="{ESPLAB_LOGO}" alt="ESPLab logo"></h1>
<div>
...
</div>
<script>
const catalog = """ + json.dumps(data_dict) + """;

function clearAndDisable(selectEl) {
    selectEl.innerHTML = '<option value="">-- Select --</option>';
    selectEl.disabled = true;
}
function enableSelect(selectEl) { selectEl.disabled = false; }
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
    if (!domain || !dataset || !tempres || !variable) return;
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
    if (!domain) { clearAndDisable(datasetSelect); return; }
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
    if (!dataset) { clearAndDisable(tempresSelect); return; }
    const tempres = Object.keys(catalog[domain][dataset]);
    populateSelect(tempresSelect, tempres);
});
document.getElementById("tempres").addEventListener("change", () => {
    const domain = document.getElementById("domain").value;
    const dataset = document.getElementById("dataset").value;
    const tempres = document.getElementById("tempres").value;
    const variableSelect = document.getElementById("variable");
    document.getElementById("datasetList").innerHTML = "";
    if (!tempres) { clearAndDisable(variableSelect); return; }
    const vars = Object.keys(catalog[domain][dataset][tempres]);
    populateSelect(variableSelect, vars);
});
document.getElementById("variable").addEventListener("change", updateDatasets);
</script>
</body>
</html>"""

    return html

def generate_model_page(catalog):
    categories = []
    projects = []
    experiments = []
    temporal_res = []
    variables = []

    data_dict = {}

    for key, source in catalog["sources"].items():
        parts = key.split("/")
        if len(parts) < 4:
            continue

        category = parts[1]
        project = parts[2]
        experiment = parts[3]
        idx = 4

        temporal = None
        variable = None
        if idx < len(parts) and parts[idx] in ["daily", "monthly", "weekly", "seasonal"]:
            temporal = parts[idx]
            idx += 1

        if idx < len(parts):
            variable = parts[idx]
        else:
            variable = "unknown"

        categories.append(category)
        projects.append(project)
        experiments.append(experiment)
        if temporal:
            temporal_res.append(temporal)
        variables.append(variable)

        data_dict.setdefault(category, {})
        data_dict[category].setdefault(project, {})
        data_dict[category][project].setdefault(experiment, {})
        if temporal:
            data_dict[category][project][experiment].setdefault(temporal, {})
            data_dict[category][project][experiment][temporal].setdefault(variable, [])
            entry_list = data_dict[category][project][experiment][temporal][variable]
        else:
            data_dict[category][project][experiment].setdefault(variable, [])
            entry_list = data_dict[category][project][experiment][variable]

        entry = {
            "name": variable,
            "long_name": source["metadata"].get("long_name", "No long name"),
            "description": source.get("description","No description"),
            "units": source["metadata"].get("units", "unknown"),
            "date_range": source["metadata"].get("date_range", "unknown"),
            "files": source["metadata"].get("n_files", 0),
            "data_location": source["metadata"].get("data_location", ""),
        }
        entry_list.append(entry)

    # identical HTML as shown before with logo, category, project, experiment, optional tempres, variable
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Model</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="stylesheet" href="docs/style.css">
</head>
<body>
<div class="tabs">
  <a class="tab-button" href="obs.html">Observations</a>
  <a class="tab-button" href="reanalysis.html">Reanalysis</a>
  <a class="tab-button" href="model.html">Model</a>
</div>
<h1>Model <img src="{ESPLAB_LOGO}" alt="ESPLab logo"></h1>
<div>
...
</div>
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
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experiment = document.getElementById("experiment").value;
    const variable = document.getElementById("variable").value;
    const tempres = document.getElementById("tempres")?.value;

    const container = document.getElementById("datasetList");
    container.innerHTML = "";

    if (!category || !project || !experiment || !variable) {
        return;
    }

    let entries;
    if (tempres) {
        entries = catalog?.[category]?.[project]?.[experiment]?.[variable]?.[tempres];
    } else {
        entries = catalog?.[category]?.[project]?.[experiment]?.[variable];
    }

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

document.getElementById("category").addEventListener("change", () => {
    const category = document.getElementById("category").value;
    const projectSelect = document.getElementById("project");
    const experimentSelect = document.getElementById("experiment");
    const variableSelect = document.getElementById("variable");
    const tempresSelect = document.getElementById("tempres");
    clearAndDisable(projectSelect);
    clearAndDisable(experimentSelect);
    clearAndDisable(variableSelect);
    clearAndDisable(tempresSelect);
    document.getElementById("datasetList").innerHTML = "";

    if (!category) return;

    const projects = Object.keys(catalog[category]);
    populateSelect(projectSelect, projects);
});

document.getElementById("project").addEventListener("change", () => {
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experimentSelect = document.getElementById("experiment");
    const variableSelect = document.getElementById("variable");
    const tempresSelect = document.getElementById("tempres");
    clearAndDisable(experimentSelect);
    clearAndDisable(variableSelect);
    clearAndDisable(tempresSelect);
    document.getElementById("datasetList").innerHTML = "";

    if (!project) return;

    const experiments = Object.keys(catalog[category][project]);
    populateSelect(experimentSelect, experiments);
});

document.getElementById("experiment").addEventListener("change", () => {
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experiment = document.getElementById("experiment").value;
    const variableSelect = document.getElementById("variable");
    const tempresSelect = document.getElementById("tempres");
    clearAndDisable(variableSelect);
    clearAndDisable(tempresSelect);
    document.getElementById("datasetList").innerHTML = "";

    if (!experiment) return;

    const variables = Object.keys(catalog[category][project][experiment]);
    populateSelect(variableSelect, variables);
});

document.getElementById("variable").addEventListener("change", () => {
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experiment = document.getElementById("experiment").value;
    const variable = document.getElementById("variable").value;
    const tempresSelect = document.getElementById("tempres");
    document.getElementById("datasetList").innerHTML = "";

    if (!variable) {
        clearAndDisable(tempresSelect);
        return;
    }

    const tempres_options = Object.keys(catalog[category][project][experiment][variable] || {});
    if (tempres_options.length > 0 && !tempres_options.includes("name")) {
        populateSelect(tempresSelect, tempres_options);
    } else {
        clearAndDisable(tempresSelect);
    }
});

document.getElementById("tempres")?.addEventListener("change", updateDatasets);
</script>

</body></html>"""
    return html

def generate_index_html():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ESPLab Data Catalog</title>
<link rel="stylesheet" href="docs/style.css" />
</head>
<body>

<h1>ESPLab Data Catalog</h1>

<div class="tabs">
  <button class="tab-button active" data-tab="obs">Observations</button>
  <button class="tab-button" data-tab="reanalysis">Reanalysis</button>
  <button class="tab-button" data-tab="model">Model</button>
</div>

<div id="obs" class="tab-content active">
  <iframe src="obs.html" style="width:100%; height:600px; border:none;"></iframe>
</div>
<div id="reanalysis" class="tab-content">
  <iframe src="reanalysis.html" style="width:100%; height:600px; border:none;"></iframe>
</div>
<div id="model" class="tab-content">
  <iframe src="model.html" style="width:100%; height:600px; border:none;"></iframe>
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    obs_catalog = load_catalog_json(OBS_JSON)
    reanalysis_catalog = load_catalog_json(REANALYSIS_JSON)
    model_catalog = load_catalog_json(MODEL_JSON)

    obs_html = generate_obs_page(obs_catalog)
    reanalysis_html = generate_reanalysis_page(reanalysis_catalog)
    model_html = generate_model_page(model_catalog)
    index_html = generate_index_html()

    write_html(os.path.join(OUTPUT_DIR, "index.html"), index_html)
    write_html(os.path.join(OUTPUT_DIR, "obs.html"), obs_html)
    write_html(os.path.join(OUTPUT_DIR, "reanalysis.html"), reanalysis_html)
    write_html(os.path.join(OUTPUT_DIR, "model.html"), model_html)

if __name__ == "__main__":
    main()

