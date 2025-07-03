import os
import glob
import re
import xarray as xr
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

BASE_DIR = "/data/esplab/shared/model"
IGNORE_DIRS = {'tmp', 'old_versions', '.ipynb_checkpoints'}

def get_nc_files_recursive(directory):
    """Recursively find all .nc files under directory"""
    return sorted(glob.glob(os.path.join(directory, '**', '*.nc'), recursive=True))

def parse_p1_filename_date(filename):
    """
    Extract date from filenames like:
    zg_500_cesm2cam6climoOCNclimoLND_23jan2023_00z_d01_d46_m08.nc
    Extract date '23jan2023' and parse to yyyy-mm-dd.
    """
    basename = os.path.basename(filename)
    m = re.search(r'_(\d{2}[a-z]{3}\d{4})_', basename, re.IGNORECASE)
    if m:
        try:
            dt = pd.to_datetime(m.group(1), format='%d%b%Y', errors='coerce')
            if pd.isna(dt):
                return None
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return None
    return None

def extract_metadata(nc_files):
    """Extract metadata from first NetCDF file in list"""
    try:
        ds = xr.open_dataset(nc_files[0], decode_times=True, use_cftime=True)
        var_name = list(ds.data_vars)[0] if ds.data_vars else "unknown"
        long_name = ds[var_name].attrs.get('long_name', var_name)
        units = ds[var_name].attrs.get('units', 'unknown')
        if 'time' in ds.coords:
            times = pd.to_datetime(ds.time.values, errors='coerce')
            if times.isnull().all():
                date_range = "unknown"
            else:
                date_range = f"{times.min().strftime('%Y-%m-%d')} to {times.max().strftime('%Y-%m-%d')}"
        else:
            date_range = "unknown"
        ds.close()
        return long_name, units, date_range
    except Exception as e:
        print(f"⚠️ Failed to extract metadata from {nc_files[0]}: {e}")
        return "unknown", "unknown", "unknown"

def build_model_catalog(base_dir=BASE_DIR):
    catalog = {
        "metadata": {
            "title": "Model Data Catalog",
            "version": 1,
            "description": "Auto-generated model data catalog"
        },
        "sources": {}
    }

    categories = ['initialized', 'uninitialized']
    for category in categories:
        category_path = os.path.join(base_dir, category)
        if not os.path.isdir(category_path):
            print(f"Warning: {category_path} does not exist, skipping {category}")
            continue

        for project in sorted(os.listdir(category_path)):
            if project in IGNORE_DIRS:
                continue
            project_path = os.path.join(category_path, project)
            if not os.path.isdir(project_path):
                continue

            for experiment in sorted(os.listdir(project_path)):
                if experiment in IGNORE_DIRS:
                    continue
                experiment_path = os.path.join(project_path, experiment)
                if not os.path.isdir(experiment_path):
                    continue

                # Special handling for NCAR-CESM2-CLIMO and its p1 directory
                if project == "NCAR-CESM2-CLIMO" and experiment == "p1":
                    # For each variable, recursively collect .nc files under <variable>/<YYYY>/<MM>/
                    for variable in sorted(os.listdir(experiment_path)):
                        variable_path = os.path.join(experiment_path, variable)
                        if not os.path.isdir(variable_path):
                            continue

                        nc_files = get_nc_files_recursive(variable_path)
                        if not nc_files:
                            print(f"    No NetCDF files found for {category}/{project}/{experiment}/{variable}")
                            continue

                        # Extract IC dates from filenames
                        ic_dates = sorted(set(filter(None, [parse_p1_filename_date(f) for f in nc_files])))

                        long_name, units, date_range = extract_metadata(nc_files)

                        key = f"model/{category}/{project}/{experiment}/{variable}"
                        catalog["sources"][key] = {
                            "description": long_name,
                            "driver": "netcdf",
                            "args": {
                                "urlpath": os.path.join(variable_path, '**', '*.nc'),
                                "engine": "netcdf4"
                            },
                            "metadata": {
                                "long_name": long_name,
                                "units": units,
                                "date_range": date_range,
                                "n_files": len(nc_files),
                                "IC_dates": ic_dates,
                                "data_location": variable_path
                            }
                        }

                else:
                    # For other experiments (including NCAR-CESM2-CLIMO not p1), assume structure:
                    # /<variable>/*.nc inside experiment directory
                    for datatype in sorted(os.listdir(experiment_path)):
                        datatype_path = os.path.join(experiment_path, datatype)
                        if not os.path.isdir(datatype_path) or datatype in IGNORE_DIRS:
                            continue
                        for variable in sorted(os.listdir(datatype_path)):
                            variable_path = os.path.join(datatype_path, variable)
                            if not os.path.isdir(variable_path):
                                continue
                            nc_files = get_nc_files_recursive(variable_path)
                            if not nc_files:
                                continue

                            long_name, units, date_range = extract_metadata(nc_files)

                            key = f"model/{category}/{project}/{experiment}/{datatype}/{variable}"
                            catalog["sources"][key] = {
                                "description": long_name,
                                "driver": "netcdf",
                                "args": {
                                    "urlpath": os.path.join(variable_path, "*.nc"),
                                    "engine": "netcdf4"
                                },
                                "metadata": {
                                    "long_name": long_name,
                                    "units": units,
                                    "date_range": date_range,
                                    "n_files": len(nc_files),
                                    "data_location": variable_path
                                }
                            }
 
    return catalog

def write_catalog(catalog, output_path="catalogs/model.yaml"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    import yaml
    with open(output_path, 'w') as f:
        yaml.dump(catalog, f, sort_keys=False)
    print(f"✅ Model catalog written to {output_path}")

if __name__ == "__main__":
    model_catalog = build_model_catalog()
    write_catalog(model_catalog)

