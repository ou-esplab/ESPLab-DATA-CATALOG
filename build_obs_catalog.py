import os
import yaml
import xarray as xr
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

BASE_DIR = "/data/esplab/shared/obs"
IGNORE_DIRS = {'tmp', 'old_versions', '.ipynb_checkpoints'}

def get_netcdf_files(directory):
    files = sorted([
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.endswith('.nc') and os.path.isfile(os.path.join(directory, f))
    ])
    print(f"    Found {len(files)} NetCDF files in {directory}")
    return files

def extract_metadata(nc_files):
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
        return {
            "long_name": long_name,
            "units": units,
            "date_range": date_range,
            "n_files": len(nc_files)
        }
    except Exception as e:
        print(f"⚠️ Failed to extract metadata from {nc_files[0]}: {e}")
        return {
            "long_name": "unknown",
            "units": "unknown",
            "date_range": "unknown",
            "n_files": len(nc_files)
        }

def build_obs_catalog(base_dir):
    catalog = {
        "metadata": {
            "title": "Observational Data Catalog",
            "version": 1,
            "description": "Auto-generated obs data catalog"
        },
        "sources": {}
    }

    print(f"Building OBS catalog from base dir: {base_dir}")
    # Expected structure: obs/gridded/<domain>/<variable>/<temporal_resolution>/<dataset>
    gridded_path = os.path.join(base_dir, "gridded")
    if not os.path.isdir(gridded_path):
        print(f"Error: Expected gridded directory at {gridded_path} not found.")
        return catalog

    for domain in sorted(os.listdir(gridded_path)):
        if domain in IGNORE_DIRS:
            continue
        domain_path = os.path.join(gridded_path, domain)
        if not os.path.isdir(domain_path):
            continue

        for variable in sorted(os.listdir(domain_path)):
            if variable in IGNORE_DIRS:
                continue
            variable_path = os.path.join(domain_path, variable)
            if not os.path.isdir(variable_path):
                continue

            for temp_res in sorted(os.listdir(variable_path)):
                if temp_res in IGNORE_DIRS:
                    continue
                temp_path = os.path.join(variable_path, temp_res)
                if not os.path.isdir(temp_path):
                    continue

                for dataset in sorted(os.listdir(temp_path)):
                    if dataset in IGNORE_DIRS:
                        continue
                    dataset_path = os.path.join(temp_path, dataset)
                    if not os.path.isdir(dataset_path):
                        continue

                    # Try to find NetCDF files directly in dataset_path
                    nc_files = get_netcdf_files(dataset_path)

                    # If no files, check subdirectories one level down
                    if not nc_files:
                        print(f"  No NetCDF files directly in {dataset_path}, checking subdirectories...")
                        subdirs = [d for d in sorted(os.listdir(dataset_path)) if os.path.isdir(os.path.join(dataset_path, d))]
                        if subdirs:
                            for subdir in subdirs:
                                subdir_path = os.path.join(dataset_path, subdir)
                                sub_nc_files = get_netcdf_files(subdir_path)
                                if not sub_nc_files:
                                    print(f"    ⚠️ No NetCDF files in {subdir_path}, skipping.")
                                    continue
                                print(f"✔️ Processing obs/gridded/{domain}/{variable}/{temp_res}/{dataset}/{subdir}")
                                meta = extract_metadata(sub_nc_files)
                                key = f"obs/gridded/{domain}/{variable}/{temp_res}/{dataset}/{subdir}"
                                catalog["sources"][key] = {
                                    "description": meta['long_name'],
                                    "driver": "netcdf",
                                    "args": {
                                        "urlpath": os.path.join(subdir_path, "*.nc"),
                                        "engine": "netcdf4"
                                    },
                                    "metadata": {
                                        "long_name": meta['long_name'],
                                        "units": meta['units'],
                                        "date_range": meta['date_range'],
                                        "n_files": meta['n_files'],
                                        "data_location": subdir_path
                                    }
                                }
                        else:
                            print(f"⚠️ No NetCDF files or subdirectories with files in {dataset_path}, skipping.")
                    else:
                        print(f"✔️ Processing obs/gridded/{domain}/{variable}/{temp_res}/{dataset}")
                        meta = extract_metadata(nc_files)
                        key = f"obs/gridded/{domain}/{variable}/{temp_res}/{dataset}"
                        catalog["sources"][key] = {
                            "description": meta['long_name'],
                            "driver": "netcdf",
                            "args": {
                                "urlpath": os.path.join(dataset_path, "*.nc"),
                                "engine": "netcdf4"
                            },
                            "metadata": {
                                "long_name": meta['long_name'],
                                "units": meta['units'],
                                "date_range": meta['date_range'],
                                "n_files": meta['n_files'],
                                "data_location": dataset_path
                            }
                        }

    return catalog

def write_catalog(catalog, output_path="catalogs/obs.yaml"):
    with open(output_path, 'w') as f:
        yaml.dump(catalog, f, sort_keys=False)
    print(f"✅ Catalog written to {output_path}")

# Main
if __name__ == "__main__":
    catalog = build_obs_catalog(BASE_DIR)
    write_catalog(catalog)

