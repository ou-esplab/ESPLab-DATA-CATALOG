### Import the needed packages and disable warnings
import os
import yaml
import xarray as xr
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Define the base directory to build the model catalog off of and ignore certain subdirectories
BASE_DIR = "/data/esplab/shared/obs"
IGNORE_DIRS = {'tmp', 'old_versions', '.ipynb_checkpoints', 'ice'}

# Define a function to find all the .nc files under a certain directory 
def get_netcdf_files(directory):
    # Get the files in the directory, join their paths and sort them if the file ends with .nc
    files = sorted([
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.endswith('.nc') and os.path.isfile(os.path.join(directory, f))])

    # If the dataset directory is the CPC-UNI-CONUS-0.25deg directory
    if directory == '/data/esplab/shared/obs/gridded/atm/precip/daily/CPC-UNI-CONUS-0.25deg':
        # Get the files in the directory, join their paths and sort them if the file ends with .YYYY.nc to filter out other .nc files and masks
        files = sorted([
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.endswith('.nc') and os.path.isfile(os.path.join(directory,f)) and 'mask' not in f.lower()])
    
    # Print out how many netCDF files were found in the directory and return them
    print(f"Found {len(files)} NetCDF files in {directory}")
    return files

# Define a function to extract the metadata from all of the .nc files in a list
def extract_metadata_all_files(nc_files):
    # From a list of .nc files, try to
    try:
        #ds = xr.open_mfdataset(nc_files, combine='by_coords', parallel=True)
        # Open all the files in the list, decode the times, and combine them into one dataset by their coordinates
        ds = xr.open_mfdataset(nc_files, combine='by_coords',decode_times=True) 
        var_name = list(ds.data_vars)[-1] if ds.data_vars else "unknown" # Get the last variable name of the data if there are data variables
        long_name = ds[var_name].attrs.get('long_name', var_name) # Get the long name of the variable from the attributes of the data
        units = ds[var_name].attrs.get('units', 'unknown') # Get the units of the variable from the attributes of the data
        # If time is a coordinate of the datafile
        if "time" in ds.coords:
            times = pd.to_datetime(ds.time.values, errors='coerce') # Convert all the time values to datetime times
            times = times.dropna() if hasattr(times, 'dropna') else times # If the times object has the ability to drop NaNs, then drop any NaNs
            # If the number of times is equal to zero, return the date range as unknown
            if len(times) == 0:
                date_range = "unknown"
            # If the number of times is more than zero, get the date range as strings of the minimum and maximum time
            else:
                date_range = f"{times.min().strftime('%Y-%m-%d')} to {times.max().strftime('%Y-%m-%d')}"
        # If time is not a coordinate of the data file, return the date range as unknown
        else:
            date_range = "unknown"
        # Close the combined dataset of data files
        ds.close()
        # Return the long name, units, date range of the data, and the number of .nc files found and set them to a dictionary
        return {
            "long_name": long_name,
            "units": units,
            "date_range": date_range,
            "n_files": len(nc_files)
        }
    # If an error occurs, print that the metadata extraction failed, the error, and return the long name, units, and date range of the data as unknown
    except Exception as e:
        print(f"⚠️ Failed to extract metadata from {nc_files[0]}: {e}")
        return {
            "long_name": "unknown",
            "units": "unknown",
            "date_range": "unknown",
            "n_files": len(nc_files)
        }

# Define a function to build the catalog of observation data from a given base directory
def build_obs_catalog(base_dir):
    # Create an empty catalog to append to
    catalog = {
        "metadata": {
            "title": "Observational Data Catalog",
            "version": 1,
            "description": "Auto-generated obs data catalog"
        },
        "sources": {}
    }

    # Print a statement that the obs catalog is being built from the given base directory
    print(f"Building OBS catalog from base dir: {base_dir}")
    print()
    
    ##### Filepath to the indices data is usually as follows: obs/indices/<teleconnection>/<dataset>           #####
    #####                                                 Ex: obs/indices/mlso/mlso.index.01011979-08312019.nc #####
    #####                                                 Ex: obs/indices/nino34/nino34.erasstv5.psl.csv       #####

    # Define the filepath to the indices data
    indices_path = os.path.join(base_dir, "indices")
    # If the indices data directory does not exist, print a message and return the empty catalog
    if not os.path.isdir(indices_path):
        print(f"Error: Expected indices directory at {indices_path} not found.")
        return catalog

    # For each teleconnection directory in the indices path (mslo, nino34)
    for teleconn in sorted(os.listdir(indices_path)):
        # If the teleconnection directory is in the ignorable directories, continue
        if teleconn in IGNORE_DIRS:
            continue
        # Define the teleconnection path based on the teleconnection
        teleconn_path =  os.path.join(indices_path, teleconn)
        # If the teleconnection path does not exist, continue
        if not os.path.isdir(teleconn_path):
            continue

        # Use the function to get and sort all the files in the teleconnection path
        nc_files = get_netcdf_files(teleconn_path)

        # If there are no subdirectories or netCDF files in the teleconnection path, print out there are none and continue
        if not nc_files:
            print(f"⚠️ No NetCDF files or subdirectories with files in {teleconn_path}, skipping.")
            print()
        # If there are netCDF files in the teleconnection path, print that they are found successfully and being processed
        else:
            print(f"✔️ Processing obs/indices/{teleconn}")
            print()
            # Use the function to extract the metadata from all the .nc files in the dataset path 
            meta = extract_metadata_all_files(nc_files)
            # Define the key path to where the dataset data is found
            key = f"obs/indices/{teleconn}"
            # Append the catalog for a dataset filepath with the resulting metadata
            catalog["sources"][key] = {
                "description": meta['long_name'],
                "driver": "netcdf",
                "args": {
                    "urlpath": os.path.join(teleconn_path, "*.nc"),
                    "engine": "netcdf4"
                },
                "metadata": {
                    "long_name": meta['long_name'],
                    "units": meta['units'],
                    "date_range": meta['date_range'],
                    "n_files": meta['n_files'],
                    "data_location": teleconn_path
                }
            }
    
    ##### Filepath to the gridded data is usually as follows: obs/gridded/<domain>/<variable>/<temporal_resolution>/<dataset> #####
    #####                                                 Ex: obs/gridded/ocn/SST/weekly/NOAA-OISSTv2/                        #####
    #####                                                 Ex: obs/gridded/atm/precip/daily/chirps-v2.0/<subdirectories>       #####
    #####                                                 Ex: obs/gridded/fluxes-radiation/OLR/daily/NOAA-interp-OLR          #####
    
    # Define the filepath to the gridded data
    gridded_path = os.path.join(base_dir, "gridded")
    # If the gridded data directory does not exist, print a message and return the empty catalog
    if not os.path.isdir(gridded_path):
        print(f"Error: Expected gridded directory at {gridded_path} not found.")
        return catalog

    # For each domain directory in the gridded path (ocn, atm, fluxes-radiation)
    for domain in sorted(os.listdir(gridded_path)):
        # If the domain directory is in the ignorable directories, continue
        if domain in IGNORE_DIRS:
            continue
        # Define the domain path based on the domain
        domain_path = os.path.join(gridded_path, domain)
        # If the domain path does not exist, continue
        if not os.path.isdir(domain_path):
            continue

        # For each variable directory in the domain path (SST, precip, OLR)
        for variable in sorted(os.listdir(domain_path)):
            # If the variable directory is in the ignorable directories, continue
            if variable in IGNORE_DIRS:
                continue
            # Define the variable path based on the variable
            variable_path = os.path.join(domain_path, variable)
            # If the variable path does not exist, continue
            if not os.path.isdir(variable_path):
                continue

            # For each temporal resolution in the variable path (daily, weekly, monthly)
            for temp_res in sorted(os.listdir(variable_path)):
                # If the temporal resolution directory is in the ignorable directories, continue
                if temp_res in IGNORE_DIRS:
                    continue
                # Define the temporal resolution path based on the resolution
                temp_path = os.path.join(variable_path, temp_res)
                # If the temporal resolution path does not exist, continue
                if not os.path.isdir(temp_path):
                    continue

                # For each dataset in the temporal resolution path (NOAA-interp-OLR, GPCC, NOAA-PRECL, CPC-UNI-HIRES, chirps-v2.0) 
                for dataset in sorted(os.listdir(temp_path)):
                    # If the dataset is in the ignorable directories, continue
                    if dataset in IGNORE_DIRS:
                        continue
                    # Define the dataset path based on the dataset
                    dataset_path = os.path.join(temp_path, dataset)
                    # If the dataset path does not exist, continue
                    if not os.path.isdir(dataset_path):
                        continue
                    
                    # Use the function to get and sort all the files in the dataset path
                    nc_files = get_netcdf_files(dataset_path)

                    # If the dataset is the CPC-UNI-CONUS-0.25deg dataset 
                    if dataset == "CPC-UNI-CONUS-0.25deg":
                        # If there are .nc files in the dataset, print that they are found successfully and are being processed
                        if nc_files:
                            print(f"✔️ Processing obs/gridded/{domain}/{variable}/{temp_res}/{dataset}")
                            print()
                            # Use the function to extract the metadata from all the .nc files in the dataset
                            meta = extract_metadata_all_files(nc_files)
                            # Define the key path to where the dataset is found
                            key = f"obs/gridded/{domain}/{variable}/{temp_res}/{dataset}"
                            # Append the catalog for a dataset filepath with the resulting metadata
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
                                    "data_location": dataset_path,
                                    "type": "historical"
                                }
                            }

                        # Process the RT sub-directory by defining the path to the RT data
                        rt_path = os.path.join(dataset_path, "RT")
                        # If the path to the RT sub-directory exists
                        if os.path.isdir(rt_path):
                            # Use the function to get and sort all the files in the sub-directory path
                            rt_files = get_netcdf_files(rt_path)
                            # If there are .nc files in the sub-directory, print that they are found successfully and are being processed
                            if rt_files:
                                print(f"✔️ Processing obs/gridded/{domain}/{variable}/{temp_res}/{dataset}/RT")
                                print()
                                # Use the function to extract the metadata from all the .nc files in the sub-directory
                                meta = extract_metadata_all_files(rt_files)
                                # Define the key path to where the sub-directory is found
                                key = f"obs/gridded/{domain}/{variable}/{temp_res}/{dataset}/RT"
                                # Append the catalog for a dataset filepath with the resulting metadata
                                catalog["sources"][key] = {
                                    "description": meta['long_name'],
                                    "driver": "netcdf",
                                    "args": {
                                        "urlpath": os.path.join(rt_path, "*.nc"),
                                        "engine": "netcdf4"
                                    },
                                    "metadata": {
                                        "long_name": meta['long_name'],
                                        "units": meta['units'],
                                        "date_range": meta['date_range'],
                                        "n_files": meta['n_files'],
                                        "data_location": rt_path,
                                        "type": "realtime"
                                    }
                                }

                        # Skip future logic for this dataset so CPC-UNI-CONUS-0.25deg is not processed twice
                        continue

                    # If there are no files, check the subdirectories one level down
                    if not nc_files:
                        print(f"No NetCDF files directly in {dataset_path}, checking subdirectories...")
                        subdirs = [d for d in sorted(os.listdir(dataset_path)) if os.path.isdir(os.path.join(dataset_path, d))]
                        # If there are subdirectories (such as in the CHIRPS version 2.0 dataset)
                        if subdirs:
                            # For each subdirectory in the dataset path
                            for subdir in subdirs:
                                # Define the subdirectory path based on the subdirectory
                                subdir_path = os.path.join(dataset_path, subdir)
                                # Use the function to get and sort all the files in the subdirectory path
                                sub_nc_files = get_netcdf_files(subdir_path)
                                # If there are no .nc files in the subdirectory, print out that there are none and continue
                                if not sub_nc_files:
                                    print(f"⚠️ No NetCDF files in {subdir_path}, skipping.")
                                    continue
                                print(f"✔️ Processing obs/gridded/{domain}/{variable}/{temp_res}/{dataset}/{subdir}")
                                # Use the function to extract the metadata from all the .nc files in the subdirectory
                                meta = extract_metadata_all_files(sub_nc_files)
                                # Print out the metadata dictionary of the subdirectory
                                print("Metadata:", meta)
                                print()
                                # Define the key path to where the subdirectory data is found
                                key = f"obs/gridded/{domain}/{variable}/{temp_res}/{dataset}/{subdir}"
                                # Append the catalog for a subdirectory filepath with the resulting metadata
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
                        # If there are no subdirectories or netCDF files in the dataset path, print out there are none and continue
                        else:
                            print(f"⚠️ No NetCDF files or subdirectories with files in {dataset_path}, skipping.")
                    # If there are netCDF files in the dataset path, print that they are found successfully and being processed
                    else:
                        print(f"✔️ Processing obs/gridded/{domain}/{variable}/{temp_res}/{dataset}")
                        print()
                        # Use the function to extract the metadata from all the .nc files in the dataset path 
                        meta = extract_metadata_all_files(nc_files)
                        # Define the key path to where the dataset data is found
                        key = f"obs/gridded/{domain}/{variable}/{temp_res}/{dataset}"
                        # Append the catalog for a dataset filepath with the resulting metadata
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

    # Return the catalog from the base directory
    return catalog

# Define a function the write the appended catalog to a .yaml file
def write_catalog(catalog, output_path="catalogs/obs.yaml"):
    # Write to the output path the updated catalog as a .yaml file and print that it was written
    with open(output_path, 'w') as f:
        yaml.dump(catalog, f, sort_keys=False)
    print(f"✅ Catalog written to {output_path}")

# Run the following if the code is being run as a script
if __name__ == "__main__":
    # Build the catalog using the function and the defined base directory
    obs_catalog = build_obs_catalog(BASE_DIR)
    # Write the resulting catalog using the function
    write_catalog(obs_catalog)

