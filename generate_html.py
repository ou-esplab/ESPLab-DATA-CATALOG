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


def print_summary(d, level=0, max_level=2):
    indent = '  ' * level
    if level > max_level:
        print(f"{indent}...")
        return
    if isinstance(d, dict):
        for k, v in d.items():
            print(f"{indent}{k}:")
            print_summary(v, level + 1, max_level)
    elif isinstance(d, list):
        print(f"{indent}List with {len(d)} entries")
    else:
        print(f"{indent}{d}")

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
<link rel="stylesheet" href="style.css" />
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
const catalog = """ + json.dumps(data_dict) + """;
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
    const datasets = Object.keys(catalog[domain] || {});
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
    const tempres = Object.keys(catalog[domain][dataset] || {});
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
    const vars = Object.keys(catalog[domain][dataset][tempres] || {});
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
            <div class="dataset-name">${entry.name}</div>
            <div><strong>Description:</strong> ${entry.long_name}</div>
            <div><strong>Units:</strong> ${entry.units}</div>
            <div><strong>Date Range:</strong> ${entry.date_range}</div>
            <div><strong>Files:</strong> ${entry.files}</div>
            <div><strong>Data Location:</strong> ${entry.data_location}</div>
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
    temporal_res = []
    variables = []
    data_dict = {}

    for key, source in catalog["sources"].items():
        parts = key.split("/")
        print("REANALYSIS: ", parts)
        # expects parts like ['reanalysis', 'era5', '4xdaily', 'msl']
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
            "name": variable,
            "long_name": source["metadata"].get("long_name", "No long name"),
            "description": source.get("description", "No description"),
            "units": source["metadata"].get("units", "unknown"),
            "date_range": source["metadata"].get("date_range", "unknown"),
            "files": source["metadata"].get("n_files", 0),
            "data_location": source["metadata"].get("data_location", ""),
        }
        data_dict[dataset][temp][variable].append(entry)

    datasets = sorted(set(datasets))
    temporal_res = sorted(set(temporal_res))
    variables = sorted(set(variables))

    # then build your HTML as before
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Reanalysis</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
<h1>Reanalysis</h1>

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
  const dataset = document.getElementById("dataset").value;
  const tempres = document.getElementById("tempres").value;
  const variable = document.getElementById("variable").value;
  const container = document.getElementById("datasetList");
  container.innerHTML = "";
  if (!dataset || !tempres || !variable) return;
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
  clearAndDisable(tempresSelect);
  clearAndDisable(variableSelect);
  document.getElementById("datasetList").innerHTML = "";
  if (!dataset) return;
  const temps = Object.keys(catalog[dataset]);
  populateSelect(tempresSelect, temps);
});
document.getElementById("tempres").addEventListener("change", () => {
  const dataset = document.getElementById("dataset").value;
  const tempres = document.getElementById("tempres").value;
  const variableSelect = document.getElementById("variable");
  clearAndDisable(variableSelect);
  document.getElementById("datasetList").innerHTML = "";
  if (!tempres) return;
  const vars = Object.keys(catalog[dataset][tempres]);
  populateSelect(variableSelect, vars);
});
document.getElementById("variable").addEventListener("change", updateDatasets);
</script>
</body>
</html>"""

    return html

def generate_model_page(catalog):
    import json

    categories = []
    projects = []
    experiments = []
    data_dict = {}

    for key, source in catalog["sources"].items():
        parts = key.split("/")
        if len(parts) < 4:
            continue

        category = parts[1]
        project = parts[2]

        categories.append(category)
        projects.append(project)

        data_dict.setdefault(category, {})
        data_dict[category].setdefault(project, {})

        if project == "subx":
            variable = parts[4]
            experiment = parts[3]
            data_dict[category][project].setdefault(experiment, {})
            data_dict[category][project][experiment].setdefault(variable, [])
            entry_list = data_dict[category][project][experiment][variable]
        elif project == "nmme":
            experiment = parts[3]
            temporal = parts[4]
            variable = parts[5]
            data_dict[category][project].setdefault(experiment, {})
            data_dict[category][project][experiment].setdefault(temporal, {})
            data_dict[category][project][experiment][temporal].setdefault(variable, [])
            entry_list = data_dict[category][project][experiment][temporal][variable]
        elif project == "NCAR-CESM2-SMYLE":
            temporal = parts[3]
            year = parts[4]
            month = parts[5]
            data_dict[category][project].setdefault(temporal, {})
            data_dict[category][project][temporal].setdefault(year, {})
            data_dict[category][project][temporal][year].setdefault(month, [])
            entry_list = data_dict[category][project][temporal][year][month]
        elif project == "NCAR-CESM2-CLIMO":
            experiment = parts[3]
            datatype = parts[4]
            variable = parts[5]
            data_dict[category][project].setdefault(experiment, {})
            data_dict[category][project][experiment].setdefault(datatype, {})
            data_dict[category][project][experiment][datatype].setdefault(variable, [])
            entry_list = data_dict[category][project][experiment][datatype][variable]
        else:
            entry_list = []

        entry = {
            "name": variable if 'variable' in locals() else "unknown",
            "long_name": source["metadata"].get("long_name", "No long name"),
            "description": source.get("description", "No description"),
            "units": source["metadata"].get("units", "unknown"),
            "date_range": source["metadata"].get("date_range", "unknown"),
            "files": source["metadata"].get("n_files", 0),
            "data_location": source["metadata"].get("data_location", ""),
        }
        entry_list.append(entry)

    categories = sorted(set(categories))
    projects = sorted(set(projects))
    experiments = sorted(set(experiments))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Model</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="style.css" />
</head>
<body>

<h1>Model</h1>

<div>
  <label for="category">Category:</label>
  <select id="category">
    <option value="">-- Select Category --</option>"""
    for c in categories:
        html += f"<option value='{c}'>{c}</option>\n"
    html += "</select>"

    html += """
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

  <!-- Added for SMYLE: year and month dropdowns -->
  <label for="year">Year:</label>
  <select id="year" disabled>
    <option value="">-- Select Year --</option>
  </select>

  <label for="month">Month:</label>
  <select id="month" disabled>
    <option value="">-- Select Month --</option>
  </select>
</div>

<div id="datasetList"></div>

<script>
const catalog = """ + json.dumps(data_dict) + """;

// Helper functions
function clearAndDisable(selectEl, placeholder="-- Select --") {
    selectEl.innerHTML = `<option value="">${placeholder}</option>`;
    selectEl.disabled = true;
}
function enableSelect(selectEl) {
    selectEl.disabled = false;
}
function populateSelect(selectEl, options, placeholder="-- Select --") {
    clearAndDisable(selectEl, placeholder);
    options.forEach(opt => {
        const option = document.createElement("option");
        option.value = opt;
        option.textContent = opt;
        selectEl.appendChild(option);
    });
    enableSelect(selectEl);
}

// Reference selects
const categorySelect = document.getElementById("category");
const projectSelect = document.getElementById("project");
const experimentSelect = document.getElementById("experiment");
const variableSelect = document.getElementById("variable");
const tempresSelect = document.getElementById("tempres");
const yearSelect = document.getElementById("year");
const monthSelect = document.getElementById("month");

// When category changes
categorySelect.addEventListener("change", () => {
    const category = categorySelect.value;

    clearAndDisable(projectSelect, "-- Select Project --");
    clearAndDisable(experimentSelect, "-- Select Experiment --");
    clearAndDisable(variableSelect, "-- Select Variable --");
    clearAndDisable(tempresSelect, "-- Select Temporal Resolution --");
    clearAndDisable(yearSelect, "-- Select Year --");
    clearAndDisable(monthSelect, "-- Select Month --");
    document.getElementById("datasetList").innerHTML = "";

    if (!category) return;

    const projects = Object.keys(catalog[category] || {});
    populateSelect(projectSelect, projects, "-- Select Project --");
});

// When project changes
projectSelect.addEventListener("change", () => {
    const category = categorySelect.value;
    const project = projectSelect.value;

    clearAndDisable(experimentSelect, "-- Select Experiment --");
    clearAndDisable(variableSelect, "-- Select Variable --");
    clearAndDisable(tempresSelect, "-- Select Temporal Resolution --");
    clearAndDisable(yearSelect, "-- Select Year --");
    clearAndDisable(monthSelect, "-- Select Month --");
    document.getElementById("datasetList").innerHTML = "";

    if (!project) return;

    if (project === "NCAR-CESM2-SMYLE") {
        // SMYLE has no experiment dropdown; populate temporal directly
        const temporals = Object.keys(catalog[category][project] || {});
        populateSelect(tempresSelect, temporals, "-- Select Temporal Resolution --");
        tempresSelect.disabled = false;
    } else {
        const experiments = Object.keys(catalog[category][project] || {});
        populateSelect(experimentSelect, experiments, "-- Select Experiment --");
        experimentSelect.disabled = false;
    }
});

// When experiment changes (not for SMYLE)
experimentSelect.addEventListener("change", () => {
    const category = categorySelect.value;
    const project = projectSelect.value;
    const experiment = experimentSelect.value;

    clearAndDisable(variableSelect, "-- Select Variable --");
    clearAndDisable(tempresSelect, "-- Select Temporal Resolution --");
    clearAndDisable(yearSelect, "-- Select Year --");
    clearAndDisable(monthSelect, "-- Select Month --");
    document.getElementById("datasetList").innerHTML = "";

    if (!experiment) return;

    if (project === "subx") {
        const variables = Object.keys(catalog[category][project][experiment] || {});
        populateSelect(variableSelect, variables, "-- Select Variable --");
        variableSelect.disabled = false;
    }
    else if (project === "nmme") {
        const temporals = Object.keys(catalog[category][project][experiment] || {});
        populateSelect(tempresSelect, temporals, "-- Select Temporal Resolution --");
        tempresSelect.disabled = false;
    }
    else if (project === "NCAR-CESM2-CLIMO") {
        const datatypes = Object.keys(catalog[category][project][experiment] || {});
        populateSelect(variableSelect, datatypes, "-- Select Variable --");
        variableSelect.disabled = false;
    }
});

// When temporal resolution changes
tempresSelect.addEventListener("change", () => {
    const category = categorySelect.value;
    const project = projectSelect.value;
    const experiment = experimentSelect.value; // might be empty for SMYLE
    const tempres = tempresSelect.value;

    clearAndDisable(variableSelect, "-- Select Variable --");
    clearAndDisable(yearSelect, "-- Select Year --");
    clearAndDisable(monthSelect, "-- Select Month --");
    document.getElementById("datasetList").innerHTML = "";

    if (!tempres) return;

    if (project === "nmme") {
        const variables = Object.keys(catalog[category][project][experiment][tempres] || {});
        populateSelect(variableSelect, variables, "-- Select Variable --");
        variableSelect.disabled = false;
    }
    else if (project === "NCAR-CESM2-SMYLE") {
        // For SMYLE, populate year dropdown
        const years = Object.keys(catalog[category][project][tempres] || {});
        populateSelect(yearSelect, years, "-- Select Year --");
        yearSelect.disabled = false;
    }
});

// When variable changes
variableSelect.addEventListener("change", () => {
    const category = categorySelect.value;
    const project = projectSelect.value;
    const experiment = experimentSelect.value;
    const variable = variableSelect.value;

    clearAndDisable(tempresSelect, "-- Select Temporal Resolution --");
    clearAndDisable(yearSelect, "-- Select Year --");
    clearAndDisable(monthSelect, "-- Select Month --");
    document.getElementById("datasetList").innerHTML = "";

    if (!variable) return;

    if (project === "NCAR-CESM2-CLIMO") {
        // For CLIMO, variable here is datatype, so show temporal resolution options
        const temporals = Object.keys(catalog[category][project][experiment][variable] || {});
        populateSelect(tempresSelect, temporals, "-- Select Temporal Resolution --");
        tempresSelect.disabled = false;
    }
    else if (project === "subx") {
        // For subx, variable leads directly to dataset list
        updateDatasets();
    }
});

// When year changes (SMYLE only)
yearSelect.addEventListener("change", () => {
    const category = categorySelect.value;
    const project = projectSelect.value;
    const tempres = tempresSelect.value;
    const year = yearSelect.value;

    clearAndDisable(monthSelect, "-- Select Month --");
    document.getElementById("datasetList").innerHTML = "";

    if (!year) return;

    const months = Object.keys(catalog[category][project][tempres][year] || {});
    populateSelect(monthSelect, months, "-- Select Month --");
    monthSelect.disabled = false;
});

// When month changes (SMYLE only)
monthSelect.addEventListener("change", () => {
    updateDatasets();
});

function updateDatasets() {
    const category = categorySelect.value;
    const project = projectSelect.value;
    const experiment = experimentSelect.value;
    const variable = variableSelect.value;
    const tempres = tempresSelect.value;
    const year = yearSelect.value;
    const month = monthSelect.value;

    let entries = [];
    const container = document.getElementById("datasetList");
    container.innerHTML = "";

    try {
        if (project === "subx") {
            entries = catalog[category][project][experiment][variable];
        }
        else if (project === "nmme") {
            entries = catalog[category][project][experiment][tempres][variable];
        }
        else if (project === "NCAR-CESM2-CLIMO") {
            entries = catalog[category][project][experiment][variable][tempres];
        }
        else if (project === "NCAR-CESM2-SMYLE") {
            entries = catalog[category][project][tempres][year][month];
        }
    } catch (e) {
        console.log("No matching entries found:", e);
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
</script>

</body>
</html>
"""

    return html


def generate_model_page_old(catalog):
    categories = []
    projects = []
    experiments = []
    data_dict = {}

    for key, source in catalog["sources"].items():
        #print("MODEL KEY: ",key)
        parts = key.split("/")
        #print("MODEL PARTS: ",parts)
        if len(parts) < 4:
            continue

        category = parts[1]
        project = parts[2]

        categories.append(category)
        projects.append(project)
       # experiments.append(experiment)

        # initialize project dict
        data_dict.setdefault(category, {})
        data_dict[category].setdefault(project, {})
        #data_dict[category][project].setdefault(experiment, {})

        if project == "subx":
            # category/project/experiment/variable
            variable = parts[4]
            experiment = parts[3]
            data_dict[category][project].setdefault(experiment, {})
            data_dict[category][project][experiment].setdefault(variable, [])
            entry_list = data_dict[category][project][experiment][variable]

        elif project == "nmme":
            experiment = parts[3]
            temporal = parts[4]
            variable = parts[5]
            data_dict[category][project].setdefault(experiment, {})
            data_dict[category][project][experiment].setdefault(temporal, {})
            data_dict[category][project][experiment][temporal].setdefault(variable, [])
            entry_list = data_dict[category][project][experiment][temporal][variable]

        #elif project == "NCAR-CESM2-SMYLE":
        #    # category/project/temporal/YYYY/MM
        #    temporal = parts[3]
        #    year = parts[4]
        #    month = parts[5]
        #    data_dict[category][project].setdefault(temporal, {})
        #    data_dict[category][project][temporal].setdefault(year, {})
        #    data_dict[category][project][temporal][year].setdefault(month, [])
        #    entry_list = data_dict[category][project][temporal][year][month]
        elif project == "NCAR-CESM2-SMYLE":
            year = parts[3]
            month = parts[4]
            pdata = data_dict[category][project]
            pdata.setdefault(year, {})
            pdata[year].setdefault(month, [])
            entry_list = pdata[year][month]
        elif project == "NCAR-CESM2-CLIMO":
            # category/project/experiment/datatype/variable
            experiment = parts[3]
            datatype = parts[4]
            variable = parts[5]
            data_dict[category][project].setdefault(experiment, {})
            data_dict[category][project][experiment].setdefault(datatype, {})
            data_dict[category][project][experiment][datatype].setdefault(variable, [])
            entry_list = data_dict[category][project][experiment][datatype][variable]

        else:
            # fallback
            entry_list = []

        # add entry
        entry = {
            "name": variable if 'variable' in locals() else "unknown",
            "long_name": source["metadata"].get("long_name", "No long name"),
            "description": source.get("description", "No description"),
            "units": source["metadata"].get("units", "unknown"),
            "date_range": source["metadata"].get("date_range", "unknown"),
            "files": source["metadata"].get("n_files", 0),
            "data_location": source["metadata"].get("data_location", ""),
        }
        entry_list.append(entry)

    # drop-down lists
    categories = sorted(set(categories))
    projects = sorted(set(projects))
    experiments = sorted(set(experiments))

    # put the debug print right here
    print_summary(data_dict.get("initialized", {}))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Model</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="style.css" />
</head>
<body>

<h1>Model</h1>

<div>
  <label for="category">Category:</label>
  <select id="category">
    <option value="">-- Select Category --</option>"""
    for c in categories:
        html += f"<option value='{c}'>{c}</option>\n"
    html += "</select>"

    html += """
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
const catalog = """ + json.dumps(data_dict) + """;

// Helper functions
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

// On category change
document.getElementById("category").addEventListener("change", function() {
    const category = this.value;
    const projectSelect = document.getElementById("project");
    clearAndDisable(projectSelect);
    clearAndDisable(document.getElementById("experiment"));
    clearAndDisable(document.getElementById("variable"));
    clearAndDisable(document.getElementById("tempres"));
    document.getElementById("datasetList").innerHTML = "";

    if (!category) return;

    const projects = Object.keys(catalog[category] || {});
    populateSelect(projectSelect, projects);
});

// On project change
document.getElementById("project").addEventListener("change", function() {
    const category = document.getElementById("category").value;
    const project = this.value;
    const experimentSelect = document.getElementById("experiment");
    clearAndDisable(experimentSelect);
    clearAndDisable(document.getElementById("variable"));
    clearAndDisable(document.getElementById("tempres"));
    document.getElementById("datasetList").innerHTML = "";

    if (!project) return;

    const experiments = Object.keys(catalog[category][project] || {});
    populateSelect(experimentSelect, experiments);
});

// On experiment change
document.getElementById("experiment").addEventListener("change", function() {
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experiment = this.value;

    const variableSelect = document.getElementById("variable");
    const tempresSelect = document.getElementById("tempres");

    clearAndDisable(variableSelect);
    clearAndDisable(tempresSelect);
    document.getElementById("datasetList").innerHTML = "";

    if (!experiment) return;

    if (project === "subx") {
        // Keys: variables only, no temporal dropdown
        const variables = Object.keys(catalog[category][project][experiment] || {});
        populateSelect(variableSelect, variables);
        variableSelect.disabled = false;
        tempresSelect.disabled = true;
    }
    else if (project === "nmme") {
        // Keys: temporal resolutions
        const temporals = Object.keys(catalog[category][project][experiment] || {});
        populateSelect(tempresSelect, temporals);
        tempresSelect.disabled = false;
        variableSelect.disabled = true;
    }
    else if (project === "NCAR-CESM2-CLIMO") {
        // Keys: datatypes
        const datatypes = Object.keys(catalog[category][project][experiment] || {});
        populateSelect(variableSelect, datatypes);
        variableSelect.disabled = false;
        tempresSelect.disabled = true;
    }
    else if (project === "NCAR-CESM2-SMYLE") {
        // Keys: temporal resolutions
        const temporals = Object.keys(catalog[category][project][experiment] || {});
        populateSelect(tempresSelect, temporals);
        tempresSelect.disabled = false;
        variableSelect.disabled = true;
    }
});

// On variable (or datatype for NCAR-CESM2-CLIMO) change
document.getElementById("variable").addEventListener("change", function() {
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experiment = document.getElementById("experiment").value;
    const variable = this.value;

    const tempresSelect = document.getElementById("tempres");
    clearAndDisable(tempresSelect);
    document.getElementById("datasetList").innerHTML = "";

    if (!variable) return;

    if (project === "NCAR-CESM2-CLIMO") {
        // Show variables under selected datatype in temporal dropdown
        const variables = Object.keys(catalog[category][project][experiment][variable] || {});
        populateSelect(tempresSelect, variables);
        tempresSelect.disabled = false;
    }
    else if (project === "subx") {
        // Subx shows results immediately, no temporal dropdown
        updateDatasets();
    }
});

// On temporal resolution change
document.getElementById("tempres").addEventListener("change", function() {
    updateDatasets();
});

// Function to update dataset list
function updateDatasets() {
    const category = document.getElementById("category").value;
    const project = document.getElementById("project").value;
    const experiment = document.getElementById("experiment").value;
    const variable = document.getElementById("variable").value;
    const tempres = document.getElementById("tempres").value;

    let entries = [];
    const container = document.getElementById("datasetList");
    container.innerHTML = "";

    try {
        if (project === "subx") {
            entries = catalog[category][project][experiment][variable];
        }
        else if (project === "nmme") {
            entries = catalog[category][project][experiment][tempres][variable];
        }
        else if (project === "NCAR-CESM2-CLIMO") {
            entries = catalog[category][project][experiment][variable][tempres];
        }
        else if (project === "NCAR-CESM2-SMYLE") {
            entries = catalog[category][project][experiment][tempres];
        }
    } catch (e) {
        console.log("No matching entries found:", e);
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
  <link rel="stylesheet" href="style.css" />
</head>
<body>

<!-- Banner -->
<div class="banner" style="background-color:#f1f1f1; padding:20px; display:flex; align-items:center;">
  <img src="{ESPLAB_LOGO}" alt="ESPLab logo" style="height:90px; margin-right:15px;">
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

