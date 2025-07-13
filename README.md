# ESPLab-DATA-CATALOG

[![Website](https://img.shields.io/badge/GitHub%20Pages-View%20Site-blue)](https://ou-esplab.github.io/ESPLab-DATA-CATALOG/)

The **ESPLab Data Catalog** is an interactive web interface for exploring climate and weather datasets curated by the [OU Earth System Prediction Lab (ESPLab)](https://ou-esplab.github.io). The catalog enables users to browse metadata about observational data, reanalysis products, and model hindcasts across a range of domains and timescales.

🔗 **Live Catalog**: [https://ou-esplab.github.io/ESPLab-DATA-CATALOG/](https://ou-esplab.github.io/ESPLab-DATA-CATALOG/)

---

## 📁 Repository Structure

- `catalogs/` — Intake YAML catalogs for observations, reanalysis, and model data.
- `generate_html.py` — Script that parses the catalog and builds interactive HTML pages.
- `obs.html`, `model.html`, etc. — Auto-generated HTML files served via GitHub Pages.
- `style.css` — Stylesheet used by all HTML pages.
- `environment.yml` — Conda environment specification for development and catalog generation.

---

## ⚡ Features

- Dynamic dropdown menus to filter by domain, variable, dataset, temporal resolution, etc.
- Instant display of dataset metadata, including:
  - Long name
  - Description
  - Units
  - Time range
  - Number of files
  - Data location
- Supports multiple data categories:
  - **Observations**
  - **Reanalysis**
  - **Initialized model hindcasts**

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ou-esplab/ESPLab-DATA-CATALOG.git
cd ESPLab-DATA-CATALOG


### 2. Create and activate the environment

```bash
conda env create -f environment.yml
conda activate data-dashboard

### 3. Generate the HTML pages

```bash
python generate_html.py

This builds the `obs.html` and `model.html` catalog browser interfaces.

## 🧠 How It Works
Data sources are described using Intake, a lightweight cataloging system.

generate_html.py dynamically builds the catalog interface using metadata from each dataset.

The JavaScript dropdown logic allows users to interactively filter datasets.

The HTML pages are static and hosted via GitHub Pages (no server backend required).

## 🗂 Data Types Supported

### ✅ Observations
- CPC-UNI-HIRES  
- NOAA OISST  
- *And more...*

### ✅ Reanalysis
- ERA5  
- MERRA-2  
- ERA5-Land

### ✅ Models
- SubX  
- NMME  
- NCAR CESM2 (SMYLE and CLIMO)

Each source is organized with consistent directory structure to enable automated catalog building.

---

## 🌐 GitHub Pages

The site is hosted from the `main` branch via GitHub Pages.

To update the live catalog:

1. Update catalog YAMLs or NetCDF/Zarr content  
2. Run `generate_html.py` to regenerate the HTML  
3. Commit and push changes to `main`  
4. GitHub will automatically publish the updates

🔗 **View the live site**:  
📄 [https://ou-esplab.github.io/ESPLab-DATA-CATALOG/](https://ou-esplab.github.io/ESPLab-DATA-CATALOG/)

---

## 🤝 Contributing

We welcome contributions and feedback from the community. To contribute:

1. Fork this repository  
2. Create a feature branch  
3. Submit a pull request with a clear description

If you encounter bugs or have questions, please open an issue.

---

## 📄 License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.

---

## 👩‍🔬 Maintainers

Developed and maintained by the  
**OU Earth System Prediction Lab (ESPLab)**  
🔗 [https://ou-esplab.github.io](https://ou-esplab.github.io)

