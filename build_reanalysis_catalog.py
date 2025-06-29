import os
import glob
import xarray as xr
import yaml
from tqdm import tqdm

def get_metadata_from_sample_file(filepath):
    try:
        with xr.open_dataset(filepath, decode_times=False) as ds:
            # Pick first data variable if exists, else fallback
            if ds.data_vars:
                var_name = list(ds.data_vars)[0]
                var = ds[var_name]
                long_name = var.attrs.get('long_name', var_name)
                units = var.attrs.get('units', 'unknown')
            else:
                long_name = "unknown"
                units = "unknown"

            # Decode times to get date range
            if 'time' in ds.coords:
                ds_decoded = xr.decode_cf(ds)
                time = ds_decoded['time']
                date_range = f"{str(time.min().values)[:10]} to {str(time.max().values)[:10]}"
            else:
                date_range = "unknown"

            metadata = {
                "long_name": long_name,
                "units": units,
                "date_range": date_range,
            }

            # Include some dimension sizes if present
            for dim in ['latitude', 'longitude', 'level']:
                if dim in ds.dims:
                    metadata[f"{dim}_size"] = ds.dims[dim]

            return metadata
    except Exception as e:
        print(f"⚠️ Failed to read metadata from {filepath}: {e}")
        return {
            "long_name": "unknown",
            "units": "unknown",
            "date_range": "unknown",
            "error": str(e)
        }

def build_catalog(rean_dir="/data/esplab/shared/reanalysis", output_yaml="reanalysis.yaml"):
    catalog = {
        "metadata": {
            "title": "Reanalysis Data Catalog",
            "version": 1,
            "description": "Auto-generated reanalysis data catalog"
        },
        "sources": {}
    }

    print(f"Building REANALYSIS catalog from base dir: {rean_dir}")

    for root, dirs, files in tqdm(os.walk(rean_dir), desc="Scanning directories"):
        nc_files = sorted(glob.glob(os.path.join(root, "*.nc")))
        if not nc_files:
            continue

        # Expected structure: reanalysis/<dataset>/<temporal_resolution>/<variable>
        rel_path = os.path.relpath(root, rean_dir)
        parts = rel_path.split(os.sep)
        if len(parts) != 3:
            # Skip unexpected paths
            continue

        dataset, temp_res, variable = parts
        entry_name = f"reanalysis/{dataset}/{temp_res}/{variable}"

        metadata = get_metadata_from_sample_file(nc_files[0])
        metadata["n_files"] = len(nc_files)
        metadata["data_location"] = root

        catalog["sources"][entry_name] = {
            "description": f"{metadata.get('long_name', 'unknown')} ({metadata.get('units', 'unknown')}), {metadata.get('date_range', 'unknown')}",
            "driver": "netcdf",
            "args": {
                "urlpath": os.path.join(root, "*.nc"),
                "engine": "netcdf4"
            },
            "metadata": metadata
        }

    with open(output_yaml, "w") as f:
        yaml.dump(catalog, f, sort_keys=False)

    print(f"✅ Catalog written to {output_yaml}")

if __name__ == "__main__":
    build_catalog()
