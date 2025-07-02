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
ESPLAB_LOGO = "esplab_logo.png"

def load_catalog_json(path):
    with open(path) as f:
        return json.load(f)

def unique_sorted(lst):
    return sorted(set(lst))

def generate_obs_page(catalog):
    domains = []
    data_dict = {}

    for key, source in catalog["sources"].items():
        parts = key.split("/")
        if len(parts) < 5:
            continue
        domain = parts[2]
        variable = parts[3]
        temp = parts[4]
        dataset = "/".join(parts[5:])
        domains.append(domain)

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

    domains = sorted(set(domains))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Observations</title>
<link rel="stylesheet" href="docs/style.css" />
</head>
<body>

<h1>Observations</h1>

<div>
<label for="domain">Domain:</label>
<select id="domain">
  <option value="">-- Select Domain --</option>
  {"".join(f'<option value="{d}">{d}</option>' for d in domains)}
</select>

<label for="dataset">Dataset:</label>
<select id="dataset" disabled>
  <option value="">-- Select Dataset --</option>
</select>

<label for="tempres">Temporal Resolution:</label>
<select id="tempres" disabled>
  <option value="">-- Select Temporal Resolution --</option>
</select>

<label for="variable">Variable:</label>
<select id="variable" disabled>
  <option value="">-- Select Variable --</option>
</select>
</div>

<div id="datasetList"></div>

<script>
const catalog = {json.dumps(data_dict)};

function clearSelect(sel) {{
    sel.innerHTML = '<option value="">-- Select --</option>';
    sel.disabled = true;
}}

function populateSelect(sel, options) {{
    clearSelect(sel);
    options.forEach(opt => {{
        let option = document.createElement("option");
        option.value = opt;
        option.textContent = opt;
        sel.appendChild(option);
    }});
    sel.disabled = false;
}}

document.getElementById("domain").addEventListener("change", () => {{
    const domain = document.getElementById("domain").value;
    const datasetSel = document.getElementById("dataset");
    const tempresSel = document.getElementById("tempres");
    const variableSel = document.getElementById("variable");
    document.getElementById("datasetList").innerHTML = "";
    clearSelect(tempresSel);
    clearSelect(variableSel);
    if (!domain) {{
        clearSelect(datasetSel);
        return;
    }}
    const datasets = Object.keys(catalog[domain] || {{}});
    populateSelect(datasetSel, datasets);
}});

document.getElementById("dataset").addEventListener("change", () => {{
    const domain = document.getElementById("domain").value;
    const dataset = document.getElementById("dataset").value;
    const tempresSel = document.getElementById("tempres");
    const variableSel = document.getElementById("variable");
    document.getElementById("datasetList").innerHTML = "";
    clearSelect(variableSel);
    if (!dataset) {{
        clearSelect(tempresSel);
        return;
    }}
    const tempres = Object.keys(catalog[domain][dataset] || {{}});
    populateSelect(tempresSel, tempres);
}});

document.getElementById("tempres").addEventListener("change", () => {{
    const domain = document.getElementById("domain").value;
    const dataset = document.getElementById("dataset").value;
    const tempres = document.getElementById("tempres").value;
    const variableSel = document.getElementById("variable");
    document.getElementById("datasetList").innerHTML = "";
    if (!tempres) {{
        clearSelect(variableSel);
        return;
    }}
    const vars = Object.keys(catalog[domain][dataset][tempres] || {{}});
    populateSelect(variableSel, vars);
}});

document.getElementById("variable").addEventListener("change", () => {{
    const domain = document.getElementById("domain").value;
    const dataset = document.getElementById("dataset").value;
    const tempres = document.getElementById("tempres").value;
    const variable = document.getElementById("variable").value;
    const container = document.getElementById("datasetList");
    container.innerHTML = "";
    if (!domain || !dataset || !tempres || !variable) {{
        return;
    }}
    const entries = catalog[domain][dataset][tempres][variable] || [];
    if (entries.length === 0) {{
        container.textContent = "No datasets found for this selection.";
        return;
    }}
    entries.forEach(entry => {{
        const div = document.createElement("div");
        div.className = "dataset-entry";
        div.innerHTML = `
            <div class="dataset-name">${{entry.name}}</div>
            <div><strong>Description:</strong> ${{entry.long_name}}</div>
            <div><strong>Units:</strong> ${{entry.units}}</div>
            <div><strong>Date Range:</strong> ${{entry.date_range}}</div>
            <div><strong>Files:</strong> ${{entry.files}}</div>
            <div><strong>Data Location:</strong> ${{entry.data_location}}</div>
        `;
        container.appendChild(div);
    }});
}});
</script>

</body>
</html>
"""
    return html

def generate_reanalysis_page(catalog):
    datasets = []
    data_dict = {}

    for key, source in catalog["sources"].items():
        parts = key.split("/")
        if len(parts) < 4:
            continue
        dataset = parts[-4]
        temp = parts[-3]
        variable = parts[-2]

        datasets.append(dataset)

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

    datasets = sorted(set(datasets))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Reanalysis</title>
<link rel="stylesheet" href="docs/style.css" />
</head>
<body>

<h1>Reanalysis</h1>

<div>
<label for="dataset">Dataset:</label>
<select id="dataset">
  <option value="">-- Select Dataset --</option>
  {"".join(f'<option value="{d}">{d}</option>' for d in datasets)}
</select>

<label for="tempres">Temporal Resolution:</label>
<select id="tempres" disabled>
  <option value="">-- Select Temporal Resolution --</option>
</select>

<label for="variable">Variable:</label>
<select id="variable" disabled>
  <option value="">-- Select Variable --</option>
</select>
</div>

<div id="datasetList"></div>

<script>
const catalog = {json.dumps(data_dict)};

function clearSelect(sel) {{
    sel.innerHTML = '<option value="">-- Select --</option>';
    sel.disabled = true;
}}

function populateSelect(sel, options) {{
    clearSelect(sel);
    options.forEach(opt => {{
        let option = document.createElement("option");
        option.value = opt;
        option.textContent = opt;
        sel.appendChild(option);
    }});
    sel.disabled = false;
}}

document.getElementById("dataset").addEventListener("change", () => {{
    const dataset = document.getElementById("dataset").value;
    const tempresSel = document.getElementById("tempres");
    const variableSel = document.getElementById("variable");
    document.getElementById("datasetList").innerHTML = "";
    clearSelect(variableSel);
    if (!dataset) {{
        clearSelect(tempresSel);
        return;
    }}
    const tempres = Object.keys(catalog[dataset] || {{}});
    populateSelect(tempresSel, tempres);
}});

document.getElementById("tempres").addEventListener("change", () => {{
    const dataset = document.getElementById("dataset").value;
    const tempres = document.getElementById("tempres").value;
    const variableSel = document.getElementById("variable");
    document.getElementById("datasetList").innerHTML = "";
    if (!tempres) {{
        clearSelect(variableSel);
        return;
    }}
    const vars = Object.keys(catalog[dataset][tempres] || {{}});
    populateSelect(variableSel, vars);
}});

document.getElementById("variable").addEventListener("change", () => {{
    const dataset = document.getElementById("dataset").value;
    const tempres = document.getElementById("tempres").value;
    const variable = document.getElementById("variable").value;
    const container = document.getElementById("datasetList");
    container.innerHTML = "";
    if (!dataset || !tempres || !variable) {{
        return;
    }}
    const entries = catalog[dataset][tempres][variable] || [];
    if (entries.length === 0) {{
        container.textContent = "No datasets found for this selection.";
        return;
    }}
    entries.forEach(entry => {{
        const div = document.createElement("div");
        div.className = "dataset-entry";
        div.innerHTML = `
            <div class="dataset-name">${{entry.name}}</div>
            <div><strong>Description:</strong> ${{entry.long_name}}</div>
            <div><strong>Units:</strong> ${{entry.units}}</div>
            <div><strong>Date Range:</strong> ${{entry.date_range}}</div>
            <div><strong>Files:</strong> ${{entry.files}}</div>
            <div><strong>Data Location:</strong> ${{entry.data_location}}</div>
        `;
        container.appendChild(div);
    }});
}});
</script>

</body>
</html>
"""
    return html


def generate_model_page(catalog):
    categories = []
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

        # allow temporal res to be optional
        if idx < len(parts) and parts[idx] in ["daily", "monthly", "weekly", "seasonal"]:
            temporal = parts[idx]
            idx += 1

        if idx < len(parts):
            variable = parts[idx]
        else:
            variable = "unknown"

        categories.append(category)

        # build the nested dict
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

    categories = sorted(set(categories))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Model</title>
<link rel="stylesheet" href="docs/style.css" />
</head>
<body>

<h1>Model</h1>

<div>
<label for="category">Category:</label>
<select id="category">
  <option value="">-- Select Category --</option>
  {"".join(f'<option value="{c}">{c}</option>' for c in categories)}
</select>

<label for="project">Project:</label>
<select id="project" disabled>
  <option value="">-- Select Project --</option>
</select>

<label for="experiment">Experiment:</label>
<select id="experiment" disabled>
  <option value="">-- Select Experiment --</option>
</select>

<label for="variable">Variable:</label>
<select id="variable" disabled>
  <option value="">-- Select Variable --</option>
</select>

<label for="tempres">Temporal Resolution:</label>
<select id="tempres" disabled>
  <option value="">-- Select Temporal Resolution --</option>
</select>
</div>

<div id="datasetList"></div>

<script>
const catalog = {json.dumps(data_dict)};

function clearSelect(sel) {{
    sel.innerHTML = '<option value="">-- Select --</option>';
    sel.disabled = true;
}}

function populateSelect(sel, options) {{
    clearSelect(sel);
    options.forEach(opt => {{
        let option = document.createElement("option");
        option.value = opt;
        option.textContent = opt;
        sel.appendChild(option);
    }});
    sel.disabled = false;
}}

document.getElementById("category").addEventListener("change", () => {{
    const category = document.getElementById("category").value;
    const projectSel = document.getElementById("project");
    const experimentSel = document.getElementById("experiment");
    const variableSel = document.getElementById("variable");
    const tempresSel = document.getElementById("tempres");
    document.getElementById("datasetList").innerHTML = "";
    clearSelect(projectSel);
    clearSelect(experimentSel);
    clearSelect(variableSel);
    clearSelect(tempresSel);
    if (!category) return;
    const projects = Object.keys(catalog[category] || {{}});
    populateSelect(projectSel, projects);
}});

document.getElementById("project").addEventListener("change", () => {{
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experimentSel = document.getElementById("experiment");
    const variableSel = document.getElementById("variable");
    const tempresSel = document.getElementById("tempres");
    document.getElementById("datasetList").innerHTML = "";
    clearSelect(experimentSel);
    clearSelect(variableSel);
    clearSelect(tempresSel);
    if (!project) return;
    const experiments = Object.keys(catalog[category][project] || {{}});
    populateSelect(experimentSel, experiments);
}});

document.getElementById("experiment").addEventListener("change", () => {{
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experiment = document.getElementById("experiment").value;
    const variableSel = document.getElementById("variable");
    const tempresSel = document.getElementById("tempres");
    document.getElementById("datasetList").innerHTML = "";
    clearSelect(variableSel);
    clearSelect(tempresSel);
    if (!experiment) return;
    const variables = Object.keys(catalog[category][project][experiment] || {{}});
    populateSelect(variableSel, variables);
}});

document.getElementById("variable").addEventListener("change", () => {{
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experiment = document.getElementById("experiment").value;
    const variable = document.getElementById("variable").value;
    const tempresSel = document.getElementById("tempres");
    document.getElementById("datasetList").innerHTML = "";
    clearSelect(tempresSel);
    if (!variable) return;
    const node = catalog[category][project][experiment][variable];
    if (typeof node === "object" && !Array.isArray(node)) {{
        // means temporal resolutions exist
        const tempres = Object.keys(node);
        populateSelect(tempresSel, tempres);
    }} else {{
        updateDatasetList();
    }}
}});

document.getElementById("tempres").addEventListener("change", updateDatasetList);

function updateDatasetList() {{
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experiment = document.getElementById("experiment").value;
    const variable = document.getElementById("variable").value;
    const tempres = document.getElementById("tempres").value;
    const container = document.getElementById("datasetList");
    container.innerHTML = "";
    let entries;
    if (tempres) {{
        entries = catalog[category][project][experiment][variable][tempres] || [];
    }} else {{
        entries = catalog[category][project][experiment][variable] || [];
    }}
    if (!entries || entries.length === 0) {{
        container.textContent = "No datasets found for this selection.";
        return;
    }}
    entries.forEach(entry => {{
        const div = document.createElement("div");
        div.className = "dataset-entry";
        div.innerHTML = `
            <div class="dataset-name">${{entry.name}}</div>
            <div><strong>Description:</strong> ${{entry.long_name}}</div>
            <div><strong>Units:</strong> ${{entry.units}}</div>
            <div><strong>Date Range:</strong> ${{entry.date_range}}</div>
            <div><strong>Files:</strong> ${{entry.files}}</div>
            <div><strong>Data Location:</strong> ${{entry.data_location}}</div>
        `;
        container.appendChild(div);
    }});
}}
</script>

</body>
</html>"""
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

<!-- Banner -->
<div class="banner" style="background-color:#f1f1f1; padding:20px; display:flex; align-items:center;">
  <img src="{ESPLAB_LOGO}" alt="ESPLab logo" style="height:80px; margin-right:15px;">
  <h1 style="margin:0; color:{OU_RED}; font-size:2.0em;">ESPLab Data Catalog</h1>
</div>

<div class="tab" style="margin-top:10px;">
  <button class="tablinks active" onclick="openTab(event, 'obs')">Observations</button>
  <button class="tablinks" onclick="openTab(event, 'reanalysis')">Reanalysis</button>
  <button class="tablinks" onclick="openTab(event, 'model')">Model</button>
</div>

<div id="obs" class="tabcontent" style="display: block;">
  <iframe src="obs.html" style="width:100%; height:600px; border:none;"></iframe>
</div>
<div id="reanalysis" class="tabcontent" style="display: none;">
  <iframe src="reanalysis.html" style="width:100%; height:600px; border:none;"></iframe>
</div>
<div id="model" class="tabcontent" style="display: none;">
  <iframe src="model.html" style="width:100%; height:600px; border:none;"></iframe>
</div>

<script>
function openTab(evt, tabName) {{
  var tabcontent = document.getElementsByClassName("tabcontent");
  for (var i = 0; i < tabcontent.length; i++) {{
    tabcontent[i].style.display = "none";
  }}
  var tablinks = document.getElementsByClassName("tablinks");
  for (var i = 0; i < tablinks.length; i++) {{
    tablinks[i].classList.remove("active");
  }}
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.classList.add("active");
}}
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

