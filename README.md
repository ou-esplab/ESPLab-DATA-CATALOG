# ESPLab-DATA-CATALOG

This repository provides an interactive web-based data catalog browser of the data holdings of the [OU School of Meteorology Earth System Prediction Lab (ESPLab)](kathypegion.com). The application is built using [Panel](https://panel.holoviz.org/) and [Intake](https://intake.readthedocs.io/) and is designed to help users browse NetCDF datasets across categories like:

- **Model**: Initialized and uninitialized model output
- **Observations**: Gridded, station, and index data
- **Reanalysis**: ERA5, ERA5-Land, MERRA-2, and more

## 📁 Data Organization

The catalog reflects the following directory structure:

├── model/
│ ├── initialized/
│ └── uninitialized/
├── obs/
│ ├── gridded/
│ ├── indices/
│ └── station/
└── reanalysis/
├── era5/
├── era5-land/
└── merra-2/


Each entry includes metadata such as:

- Variable name and long name
- Units
- Date range
- Number of NetCDF files
- Data location path

---

## 🧭 Features

✅ Dropdown menus for selecting:

- **Category** (e.g., model, obs, reanalysis)  
- **Subcategory** (e.g., initialized, gridded, era5)  
- **Variable** (available options filtered dynamically)

✅ **Live Metadata Preview**  
View information like units, time coverage, and file count.

✅ **Live Dataset Preview**  
Displays a compact summary of the selected dataset using `xarray`.

✅ **Search/Filter** (Coming Soon)  
Filter variables or subcategories by keyword (e.g., "precip", "temperature").

✅ **Responsive Layout**  
Expandable views and scrollable panels to accommodate large datasets.

---

## 🚀 Launch via Binder

Try the catalog in your browser—no installation needed:

[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/YOUR_USERNAME/ESPLab-DATA-CATALOG/HEAD?urlpath=proxy/5006/data_catalog_app)

> **Note**: It may take 1–2 minutes to start the Binder environment.

---

## 🧰 Local Development

To test the Panel app locally:

```bash
# Clone the repo
git clone https://github.com/ou-esplab/ESPLab-DATA-CATALOG.git
cd ESPLab-DATA-CATALOG

# Create environment (optional)
conda env create -f .binder/environment.yml
conda activate esplab-env

# Run the app
panel serve data_catalog_app.py --autoreload


ChatGPT was used significantly in the writing of this app.
