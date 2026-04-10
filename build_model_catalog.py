### Import the needed packages and disable warnings
import os
import glob
import re
import xarray as xr
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Import model definitions from separate file
from model_definitions import MODEL_DEFINITIONS

# Define the base directories to build the model catalog off of and ignore certain subdirectories
BASE_DIR = "/data/esplab/shared/model"
SUBC_DIR = "/data/esplab/subc-backup/"
NMME_DIR = "/data/esplab/nmme-backup/"
IGNORE_DIRS = {'tmp', 'old_versions', '.ipynb_checkpoints'}

# Define a function to recursively find all the .nc files under a certain directory
def get_nc_files_recursive(directory):
    """Recursively find all .nc files under directory"""
    # Use glob to find all .nc files in the specified directory recursively, and return them sorted
    return sorted(glob.glob(os.path.join(directory, '**', '*.nc'), recursive=True))

# Define a function to extract the dates from CESM-CLIMO filenames
def parse_cesm2_climo_filename_date(filename):
    """
    Extract date from CESM2-CLIMO filenames like:
    pr_sfc_NCAR-CESM2_20220829.emean.daily.nc
    Extract date '20220829' and parse to yyyy-mm-dd.
    """
    basename = os.path.basename(filename)
    # Pattern: _NCAR-CESM2_YYYYMMDD.
    m = re.search(r'_NCAR-CESM2_(\d{8})\.', basename)
    if m:
        try:
            dt = pd.to_datetime(m.group(1), format='%Y%m%d', errors='coerce')
            if pd.isna(dt):
                return None
            return dt
        except Exception:
            return None
    return None

# Define a function to extract the dates from filenames in the p1 directory
def parse_p1_filename_date(filename):
    """
    Extract date from filenames like:
    zg_500_cesm2cam6climoOCNclimoLND_23jan2023_00z_d01_d46_m08.nc
    Extract date '23jan2023' and parse to yyyy-mm-dd.
    """
    # Get the final portion of the filepath to a file as the basename
    basename = os.path.basename(filename)

    # Search the basename for a string of the format "_twodigitsthreelettersfourdigits_" and store it as m (Ex: "_02Feb2004_" or "_23NOV1999_")
    m = re.search(r'_(\d{2}[a-z]{3}\d{4})_', basename, re.IGNORECASE) # Ignoring case sensitivity
    # If a suitable string m is found, convert the string to datetime and return it
    if m:
        try:
            dt = pd.to_datetime(m.group(1), format='%d%b%Y', errors='coerce') # Convert the string of format day month year to datetime
            if pd.isna(dt): # If there is no datetime object made, return none
                return None
            return dt.strftime('%Y-%m-%d') # If there is a datetime object, return the datetime as a year-month-day string
        except Exception: # If there is an error trying to convert the datetime object, return none
            return None
    return None # If no m or date basename string exists, return none

# Define a function to extract the dates from CESM2-SMYLE filenames
def parse_smyle_filename_dates(nc_files, temporal='daily'):
    """
    Extract date range from SMYLE filenames like:
    b.e21.BSMYLE.f09_g17.1970-11.020.cam.h1.PRECC.19701101-19721031.nc
    Extract daily dates from pattern: YYYYMMDD-YYYYMMDD before .nc
    Extract monthly dates from pattern: YYYY-MM before .nc
    Returns min and max dates from all files in list.
    """
    # Create an empty list to store the dates extracted from the filenames
    dates = []
    # For each file in the list of .nc files
    for filename in nc_files:
        # Get the final portion of the filepath to a file as the basename
        basename = os.path.basename(filename)
        # If the temporal resolution of the files is monthly
        if temporal == 'monthly':
            # Look for the pattern YYYYMM-YYYYMM before .nc as m
            m = re.search(r'(\d{4})(\d{2})-(\d{4})(\d{2})\.nc$', basename)
            # If the pattern m is found
            if m:
                # Try to
                try:
                    # Extract the start year and month and end year and month from the pattern groups
                    start_year, start_month = int(m.group(1)), int(m.group(2))
                    end_year, end_month = int(m.group(3)), int(m.group(4))
                    # Append the start and end dates in YYYY-MM format to the dates list
                    dates.append(f"{start_year:04d}-{start_month:02d}")
                    dates.append(f"{end_year:04d}-{end_month:02d}")
                # If there is an error trying to extract the dates from the filename, pass and continue to the next file
                except Exception:
                    pass
        # If the temporal resolution of the files is daily
        else:
            # Look for the pattern YYYYMMDD-YYYYMMDD before .nc as m
            m = re.search(r'(\d{8})-(\d{8})\.nc$', basename)
            # If the pattern m is found
            if m:
                # Try to
                try:
                    # Extract the start and end date strings from the pattern groups and convert them to datetime objects
                    start_date = pd.to_datetime(m.group(1), format='%Y%m%d', errors='coerce')
                    end_date = pd.to_datetime(m.group(2), format='%Y%m%d', errors='coerce')
                    # If the start date is valid, append it to the dates list
                    if not pd.isna(start_date):
                        dates.append(start_date)
                    # If the end date is valid, append it to the dates list
                    if not pd.isna(end_date):
                        dates.append(end_date)
                # If there is an error trying to extract the dates from the filename, pass and continue to the next file
                except Exception:
                    pass
    
    # If there are valid dates extracted from the filenames
    if dates:
        # Return the minimum and maximum dates from the list of dates as the date range
        return min(dates), max(dates)
    # If there are no valid dates extracted from the filenames, return None
    return None, None

# Define a function to extract the month/year from the NMME model filenames
def parse_nmme_filename_date(filename):
    """
    Extract month/year from NMME filenames like:
    prec_NOAA-SFS_2026_04.nc or h200_COLA-RSMAS-CCSM4_2011_05.nc
    Extract dates '2026_04' and '2011_05' and convert to YYYY-MM format.
    """
    # Get the final portion of the filepath to a file as the basename
    basename = os.path.basename(filename)
    # Look for the pattern _YYYY_MM before .nc as m
    m = re.search(r'_(\d{4})_(\d{2})\.', basename)
    # If the pattern m is found
    if m:
        # Try to
        try:
            # Extract the year and month from the pattern groups
            year, month = int(m.group(1)), int(m.group(2))
            # If the year and month are valid, return them in YYYY-MM format
            return f"{year:04d}-{month:02d}"
        # If there is an error trying to extract the month and year from the filename, return None
        except Exception:
            return None
    # If there is no pattern m found in the filename, return None
    return None

# Define a function to extract the date from SubC model filenames
def parse_subc_filename_date(filename):
    """
    Extract date from SubC filenames like:
    rlut_ESRL-FIMr1p1_20230510.daily.nc or pr_ECCC-GEPS8_20201227.daily.nc
    Extract date 'YYYYMMDD' and parse to YYYY-MM-DD format.
    """
    # Get the final portion of the filepath to a file as the basename
    basename = os.path.basename(filename)
    # Look for the pattern _YYYYMMDD. before .daily or .nc as m
    m = re.search(r'_(\d{8})[._]', basename)
    # If the pattern m is found
    if m:
        # Try to
        try:
            # Extract the date string from the pattern group
            date_str = m.group(1)
            # Convert the date string to a datetime object
            dt = pd.to_datetime(date_str, format='%Y%m%d', errors='coerce')
            # If the datetime object is valid, return it
            if not pd.isna(dt):
                return dt
        # If there is an error trying to extract the date from the filename, return None
        except Exception:
            return None
    # If there is no pattern m found in the filename, return None
    return None

# Define a function to extract the metadata from the first .nc file in a list
def extract_metadata(nc_files, variable_name=None, decode_times=True, check_coords=True):
    """Extract metadata from first NetCDF file in list"""
    # Initialize a flag to track if the dataset was successfully opened
    ds_opened = False
    # From a list of .nc files, try to
    try:
        # Get the first few files in the list of files to check for metadata
        files_to_check = nc_files[:min(4, len(nc_files))]
        # Set the default long name and units to unknown
        long_name = "unknown"
        units = "unknown"
        
        # For each .nc file in the list of files to check
        for nc_file in files_to_check:
            # Try to
            try:
                # Open the .nc file with decoding times and using cftime to handle non-standard calendars
                ds = xr.open_dataset(nc_file, decode_times=decode_times, use_cftime=True)
                ds_opened = True
                # If the variable name is provided, use it (to cover files with multiple variables)
                if variable_name and variable_name in ds.data_vars:
                    var_name = variable_name
                # If the variable name is provided but not in data_vars, it might be a coordinate - use it anyway if accessible
                elif variable_name and check_coords and variable_name in ds:
                    var_name = variable_name
                # If no variable name is provided, use the first variable in the dataset or set to unknown if no variables exist
                else:
                    var_name = list(ds.data_vars)[0] if ds.data_vars else None
                # If there is a valid variable name
                if var_name:
                    # Extract the long name and units from the variable attributes
                    long_name = ds[var_name].attrs.get('long_name', var_name)
                    units = ds[var_name].attrs.get('units', 'unknown')
                
                # Close the .nc file after extracting the metadata
                ds.close()
                
                # If both long name and units are successfully extracted
                if units != 'unknown' and long_name != 'unknown':
                    # Break out of the loop and return the extracted metadata
                    break
            # If there is an error trying to extract metadata from a file, continue to the next file
            except Exception:
                continue
        
        # Define an empty list to store the date ranges from each file
        date_ranges = []
        
        # Check only first and last file instead of all files
        for nc_file in [nc_files[0], nc_files[-1]]:
            # Try to
            try:
                # Open the file and decode the times
                ds_temp = xr.open_dataset(nc_file, decode_times=decode_times, use_cftime=True)
                
                # Set the initial time coordinate to None
                time_coord = None
                # If 'time' is a coordinate in the dataset, set the time_coord to 'time'
                if 'time' in ds_temp.coords:
                    time_coord = 'time'
                # If 'S' is a coordinate in the datset, set the time_coord to 'S'
                elif 'S' in ds_temp.coords:
                    time_coord = 'S'
                
                # If there is a time coordinate
                if time_coord:
                    # If decode_times is True
                    if decode_times:
                        # Convert the time values to datetime objects
                        times = pd.to_datetime(ds_temp[time_coord].values, errors='coerce')
                        # If there are valid time values
                        if not times.isnull().all():
                            # Get the min and max of the times and append to the date_ranges list
                            date_ranges.append((times.min(), times.max()))
                    # If decode_times is False
                    else:
                        # Try to parse time units
                        try:
                            # Get the time variable and its units
                            time_var = ds_temp[time_coord]
                            time_units = time_var.attrs.get('units', '')
                            # If the units contain a reference date (e.g. since a certain date)
                            if 'since' in time_units:
                                # Get the reference date string and convert it to a datetime object
                                ref_date_str = units.split('since')[1].strip()
                                ref_date = pd.to_datetime(ref_date_str)
                                # Get the time values and convert them to datetime objects based on the reference date
                                time_values = ds_temp[time_coord].values
                                # If there are time values and the units are in months
                                if len(time_values) > 0 and 'month' in units.lower():
                                    # Calculate the first and last date based on the reference date and time values
                                    first_date = ref_date + pd.DateOffset(months=int(time_values[0]))
                                    last_date = ref_date + pd.DateOffset(months=int(time_values[-1]))
                                    # Append the first and last date to the data_ranges list
                                    date_ranges.append((first_date, last_date))
                                # If there are time values and the units are in days
                                elif len(time_values) > 0 and 'day' in units.lower():
                                    # Calculate the first and last date based on the reference date and time values
                                    first_date = ref_date + pd.Timedelta(days=int(time_values[0]))
                                    last_date = ref_date + pd.Timedelta(days=int(time_values[-1]))
                                    # Append the first and last date to the data_ranges list
                                    date_ranges.append((first_date, last_date))
                        # If there is an error trying to parse the time values without decoding, print error and continue
                        except Exception as e:
                            pass
                
                # Close the temporary dataset
                ds_temp.close()
            # If there is an error trying to open the file or extract the time values, pass and continue to the next file
            except Exception:
                pass
        
        # If there are valid date ranges extracted from the files
        if date_ranges:
            # Get the overall min and max date from the list of date ranges and format it as a string
            min_date = min([d[0] for d in date_ranges])
            max_date = max([d[1] for d in date_ranges])
            date_range = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        # If there are no valid date ranges extracted, set the date range to unknown
        else:
            date_range = "unknown"
        
        # Close the dataset if it was opened successfully
        if ds_opened:
            ds.close()
        # Return the long name, units, and date range of the data
        return long_name, units, date_range
    # If an error occurs, print that the metadata extraction failed, the error, and return the long name, units, and date range of the data as unknown
    except Exception as e:
        print(f"⚠️ Failed to extract metadata from {nc_files[0]}: {e}")
        return "unknown", "unknown", "unknown"
    
##### Model-specific handler functions to process the data for each model type #####
### Define a function to handle the NCAR-CESM2-CLIMO model
def handle_cesm2_climo(catalog, base_dir, model_name, config):
    """Handle the NCAR-CESM2-CLIMO model using config from MODEL_DEFINITIONS"""
    
    # Format the path template with the actual base directory
    path_template = config['path_template'].format(BASE_DIR=base_dir)

    # For each experiment in the model configuration
    for experiment in config['experiments']:
        # Get the path to the experiment directory
        exp_path = os.path.join(path_template, experiment)
        # If the experiment path does not exist, print a warning and continue to the next experiment
        if not os.path.isdir(exp_path):
            print(f"⚠️  Experiment path not found: {experiment}")
            continue
        
        # For each datatype in the model configuration
        for datatype in config['datatypes']:
            # Get the path to the datatype directory
            dt_path = os.path.join(exp_path, datatype)
            # If the datatype path does not exist, print a warning and continue to the next datatype
            if not os.path.isdir(dt_path):
                print(f"⚠️  Datatype path not found: {datatype}")
                continue
            
            # For each variable in the model configuration
            for variable in sorted(os.listdir(dt_path)):
                # Get the path to the variable directory
                var_path = os.path.join(dt_path, variable)
                # If the variable path does not exist, print a warning and continue to the next variable
                if not os.path.isdir(var_path):
                    print(f"⚠️  Variable path not found: {variable}")
                    continue
                
                # Recursively get all files in the variable path (handles the year/month nesting)
                nc_files = get_nc_files_recursive(var_path)
                
                # If there are specified files to ignore in the model config
                if 'ignored_files' in config:
                    # Filter them out from the list of .nc files
                    nc_files = [f for f in nc_files if os.path.basename(f) not in config['ignored_files']]
                
                # If there are no .nc files after filtering or in general, print a warning and continue to the next variable
                if not nc_files:
                    print(f"⚠️  No valid .nc files found for {variable}")
                    continue
                
                # Use the metadata extraction function to get the metadata of the listed .nc files
                long_name, units, date_range = extract_metadata(nc_files, variable_name=variable)
                
                # For p1 datatype specifically, extract the dates and the date range from the filenames
                if datatype == 'p1':
                    # Get the datetime dates from each of the files using the parse_p1_filename_date function
                    p1_dates = [parse_p1_filename_date(f) for f in nc_files]
                    # Filter out any None values from the list of dates
                    p1_dates = [d for d in p1_dates if d is not None]
                    # If there are valid p1 dates, get the date range as the min and max of the dates
                    if p1_dates:
                        date_range = f"{min(p1_dates)} to {max(p1_dates)}"

                # For other datatypes, extract the date range from filenames
                if datatype != 'p1':
                    # If the datatype of the files is climo
                    if datatype == 'climo':
                        # Manually set the date range from the model definition config
                        date_range = config.get('climo_date_range', 'unknown')
                    # If the datatype is not climo
                    else:
                        # Get the datetime dates from each of the files using the parse_cesm2_climo_filename_date function
                        dates = [parse_cesm2_climo_filename_date(f) for f in nc_files]
                        # Filter out any None values from the list of dates
                        dates = [d for d in dates if d is not None]
                        # If there are valid dates, get the date range as the min and max of the dates
                        if dates:
                            date_range = f"{min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}"

                # If the date_range is still unknown after trying to extract from the filenames
                if date_range == "unknown":
                    print(f"⚠️ Could not extract date range for {experiment}/{datatype}/{variable}")
            
                # Define the key path for the catalog source
                key = f"model/initialized/{model_name}/{experiment}/{datatype}/{variable}"
                # Append the metadata and source information for this variable to the catalog 
                catalog["sources"][key] = {
                    "description": long_name,
                    "driver": "netcdf",
                    "args": {
                        "urlpath": os.path.join(var_path, '**', '*.nc'),
                        "engine": "netcdf4"
                    },
                    "metadata": {
                        "long_name": long_name,
                        "units": units,
                        "date_range": date_range,
                        "n_files": len(nc_files),
                        "ensemble_members": config.get('ensemble_members'),
                        "data_location": var_path
                    }
                }
                # Print that the variable was processed and added successfully to the catalog
                print(f"✓ Processed {experiment}/{datatype}/{variable}")

### Define a function to handle the NCAR-CESM2-SMYLE model
def handle_cesm2_smyle(catalog, base_dir, model_name, config):
    """Handle the NCAR-CESM2-SMYLE model using config from MODEL_DEFINITIONS"""
    """Process variables defined in config across temporal resolutions"""
    
    # Format the path template with the actual base directory
    path_template = config['path_template'].format(BASE_DIR=base_dir)
    
    # Get the variables of interest from the config
    variables = config.get('variables', [])
    
    # If no variables defined, return early
    if not variables:
        print(f"⚠️  No variables defined for {model_name}. Skipping.")
        return
    
    # For each temporal resolution (daily, monthly)
    for temporal in config['temporals']:
        # Get the path to the temporal resolution directory
        temporal_path = os.path.join(path_template, temporal)
        # If the temporal resolution path does not exist, print a warning and continue to the next temporal resolution
        if not os.path.isdir(temporal_path):
            print(f"⚠️  Temporal directory not found: {temporal}")
            continue
        
        # For each variable defined in the config
        for variable in sorted(variables):
            # Get all the files for this variable using glob
            var_files = sorted(glob.glob(os.path.join(temporal_path, '**', f'*{variable}*.nc'), recursive=True))
            
            # If there are no files for this variable, continue to the next variable
            if not var_files:
                print(f"⚠️  No files found for {temporal}/{variable}")
                continue
            
            # Use the metadata extraction function to get the metadata of the listed .nc files for this variable
            long_name, units, date_range = extract_metadata(var_files, variable_name=variable)

            # Use the filename parsing function to get the min and max dates from the filenames
            min_date, max_date = parse_smyle_filename_dates(var_files, temporal=temporal)
            # If there are valid min and max dates extracted from the files
            if min_date and max_date:
                # If the temporal resolution of the files is monthly
                if temporal == 'monthly':
                    # Format the date range as YYYY-MM to YYYY-MM
                    date_range = f"{min_date} to {max_date}"
                # If the temporal resolution of the files is daily
                else:
                    # Format the date range as YYYY-MM-DD to YYYY-MM-DD
                    date_range = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            
            # If the date_range is still unknown after trying to extract from the filenames
            if date_range == "unknown":
                print(f"⚠️ Could not extract date range for {temporal}/{variable}")

            # Define the key path for the catalog source
            key = f"model/initialized/{model_name}/{temporal}/{variable}"
            # Append the metadata and source information for this variable to the catalog
            catalog["sources"][key] = {
                "description": long_name,
                "driver": "netcdf",
                "args": {
                    "urlpath": os.path.join(temporal_path, "**", f"*{variable}*.nc"),
                    "engine": "netcdf4"
                },
                "metadata": {
                    "long_name": long_name,
                    "units": units,
                    "date_range": date_range,
                    "n_files": len(var_files),
                    "ensemble_members": config.get('ensemble_members'),
                    "data_location": temporal_path
                }
            }
            print(f"✓ Processed {temporal}/{variable}")

### Define a function to handle the NMME models
def handle_nmme_model(catalog, base_dir, model_name, config):
    """ Handle the NMME models using the config from MODEL_DEFINITIONS """
    """ and dynamically read the directories underneath the forecast and hindcast directories """

    # Format the path template with the actual NMME directory
    path_template = config['path_template'].format(NMME_DIR=base_dir)

    # For each temporal time period of the data
    for temporal in config['temporals']:
        # Get the path to the temporal directory (forecast or hindcast)
        temporal_path = os.path.join(path_template, temporal)
        # If the temporal path does not exist, print a warning and continue to the next temporal period
        if not os.path.isdir(temporal_path):
            print(f"⚠️  Temporal directory not found: {temporal}")
            continue
        
        # For each variable directory under the temporal directory (dynamically read them)
        for variable in sorted(os.listdir(temporal_path)):
            # Get the path to the variable directory
            var_path = os.path.join(temporal_path, variable)
            # If the variable path does not exist, print a warning and continue to the next variable
            if not os.path.isdir(var_path):
                print(f"⚠️  Variable directory not found: {variable}")
                continue
        
            # Recursively find all .nc files in this variable directory
            nc_files = get_nc_files_recursive(var_path)

            # If there are no .nc files, print a warning and continue to the next temporal period
            if not nc_files:
                print(f"⚠️  No .nc files found for variable: {temporal}/{variable}")
                continue

            # Use the metadata extraction function to get the metadata of the listed .nc files for this variable
            long_name, units, date_range = extract_metadata(nc_files, variable_name=variable, decode_times=False, check_coords=False)

            # Use the parsing function to get the month/year dates from the filenames
            dates = [parse_nmme_filename_date(f) for f in nc_files]
            # Filter out any None values from the list of dates
            dates = [d for d in dates if d is not None]
            # If there are valid dates extracted from the filenames
            if dates:
                # Get the date range as the min and max of the dates and format it as a string
                date_range = f"{min(dates)} to {max(dates)}"

            # Define the key path for the catalog source
            key = f"model/nmme-backup/{model_name}/{temporal}/{variable}"
            # Append the metadata and source information for this variable to the catalog
            catalog["sources"][key] = {
                "description": long_name,
                "driver": "netcdf",
                "args": {
                    "urlpath": os.path.join(var_path, '**', '*.nc'),
                    "engine": "netcdf4"
                },
                "metadata": {
                    "long_name": long_name,
                    "units": units,
                    "date_range": date_range,
                    "n_files": len(nc_files),
                    "ensemble_members": config.get('ensemble_members', {}).get(temporal),
                    "data_location": var_path
                }
            }
            print(f"✓ Processed {temporal}/{variable}")

### Define a function to handle the SubC models
def handle_subc_model(catalog, base_dir, model_name, config):
    """ Handle the SubC models using the config from MODEL_DEFINITIONS """
    """ and dynamically read the directories underneath the forecast and hindcast directories """

    # Format the path template with the actual SubC directory
    path_template = config['path_template'].format(SUBC_DIR=base_dir)

    # For each temporal time period of the data
    for temporal in config['temporals']:
        # Get the path to the temporal directory (forecast or hindcast)
        temporal_path = os.path.join(path_template, temporal)
        # If the temporal path does not exist, print a warning and continue to the next temporal period
        if not os.path.isdir(temporal_path):
            print(f"⚠️  Temporal directory not found: {temporal}")
            continue
        
        # For each variable directory under the temporal directory (dynamically read them)
        for variable in sorted(os.listdir(temporal_path)):
            # Get the path to the variable directory
            var_path = os.path.join(temporal_path, variable)
            # If the variable path does not exist, print a warning and continue to the next variable
            if not os.path.isdir(var_path):
                print(f"⚠️  Variable directory not found: {variable}")
                continue
        
            # Recursively find all .nc files in this variable directory
            nc_files = get_nc_files_recursive(var_path)

            # If there are no .nc files, print a warning and continue to the next temporal period
            if not nc_files:
                print(f"⚠️  No .nc files found for variable: {temporal}/{variable}")
                continue

            # Use the metadata extraction function to get the metadata of the listed .nc files for this variable
            long_name, units, date_range = extract_metadata(nc_files, variable_name=variable, decode_times=False, check_coords=False)

            # Extract dates from SubC filenames (pattern: {var}_{model}_{YYYYMMDD}.daily.nc)
            dates = [parse_subc_filename_date(f) for f in nc_files]
            # Filter out any None values from the list of dates
            dates = [d for d in dates if d is not None]
            # If there are valid dates extracted from the filenames
            if dates:
                # Get the date range as the min and max of the dates and format it as a string
                date_range = f"{min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}"

            # Define the key path for the catalog source
            key = f"model/subc-backup/{model_name}/{temporal}/{variable}"
            # Append the metadata and source information for this variable to the catalog
            catalog["sources"][key] = {
                "description": long_name,
                "driver": "netcdf",
                "args": {
                    "urlpath": os.path.join(var_path, '**', '*.nc'),
                    "engine": "netcdf4"
                },
                "metadata": {
                    "long_name": long_name,
                    "units": units,
                    "date_range": date_range,
                    "n_files": len(nc_files),
                    "ensemble_members": config.get('ensemble_members', {}).get(temporal),
                    "data_location": var_path
                }
            }
            print(f"✓ Processed {temporal}/{variable}")


# Define a function to get the appropriate handler function for a model name
def get_model_handler(model_name):
    """Return the appropriate handler function for a model name"""
    handlers = {
        'NCAR-CESM2-CLIMO': handle_cesm2_climo,
        'NCAR-CESM2-SMYLE': handle_cesm2_smyle,
        'CanESM5': handle_nmme_model,
        'COLA-RSMAS-CCSM4': handle_nmme_model,
        'COLA-RSMAS-CESM1': handle_nmme_model,
        'GEM5.2-NEMO': handle_nmme_model,
        'GFDL-SPEAR': handle_nmme_model,
        'NASA-GEOSS2S': handle_nmme_model,
        'NCAR-CESM1': handle_nmme_model,
        'NCEP-CFSv2-NMME': handle_nmme_model,
        'NOAA-SFS': handle_nmme_model,
        'ECCC-GEM': handle_subc_model,
        'ECCC-GEPS5': handle_subc_model,
        'ECCC-GEPS6': handle_subc_model,
        'ECCC-GEPS7': handle_subc_model,
        'ECCC-GEPS8': handle_subc_model,
        'EMC-GEFS': handle_subc_model,
        'EMC-GEFSv12': handle_subc_model,
        'EMC-GEFSv12_CPC': handle_subc_model,
        'ESRL-FIM': handle_subc_model,
        'ESRL-FIMr1p1': handle_subc_model,
        'GMAO-GEOS_V2p1': handle_subc_model,
        'GMAO-GEOS_V2p1_5daily': handle_subc_model,
        'NCEP-CFSv2-SUBC': handle_subc_model,
        'NRL-NESM': handle_subc_model,
        'RSMAS-CCSM4': handle_subc_model
        # Add more handlers as needed
    }
    return handlers.get(model_name)

# Define a function to fill in missing units for the anoms entries by copying them from
# the corresponding p1 or raw entries for the same experiment and variable
def fill_missing_cesm_climo_units(catalog):
    """
    Fill missing units for anoms entries by copying from corresponding p1 or raw entries.
    For each anoms entry with units='unknown', find the corresponding p1 or raw entry
    and use its units if available.
    """
    # Get the sources from the catalog
    sources = catalog.get("sources", {})
    
    # Build a mapping of variables to their units and long names from p1 and raw entries
    units_map = {}  # {experiment/variable: units}
    long_names_map = {}  # {experiment/variable: long_name}
    
    # For each source in the catalog
    for key, source in sources.items():
        # Get the metadata, long name, and units from the source
        metadata = source.get("metadata", {})
        units = metadata.get("units", "unknown")
        long_name = metadata.get("long_name", "unknown")
        
        # Split the key path into parts
        parts = key.split('/')
        # If there are more than 6 parts in the key path
        if len(parts) >= 6:
            datatype = parts[-2]    # Extract the datatype
            variable = parts[-1]    # Extract the variable
            experiment = parts[-3]  # Extract the experiment
            # Create a combined key of experiment and variable for the mapping
            exp_var = f"{experiment}/{variable}"
            
            # If the datatype is p1 or raw and the units are known
            if datatype in ['p1', 'raw'] and units != 'unknown':
                # Add the units to the mapping for this experiment/variable combination
                units_map[exp_var] = units

            # If the datatype is p1 or raw and the long name/descriptions are known and not just the variable
            if datatype in ['p1', 'raw'] and long_name != 'unknown' and long_name != variable:
                # Add the long name to the mapping for this experiment/variable combination
                long_names_map[exp_var] = long_name
    
    # For each source in the catalog
    for key, source in sources.items():
        # Get the metadata and long name from the source
        metadata = source.get("metadata", {})
        long_name = metadata.get("long_name", "unknown")
        
        # Split the key path into parts FIRST
        parts = key.split('/')
        
        # If there are more than 6 parts in the key path
        if len(parts) >= 6:
            datatype = parts[-2]
            variable = parts[-1]
            experiment = parts[-3]
            
            # If the metadata units are unknown
            if metadata.get("units") == "unknown":
                # If the datatype is anoms or climo
                if datatype in ['anoms', 'climo']:
                    # Create a combined key of experiment and variable for the matching
                    exp_var = f"{experiment}/{variable}"
                    
                    # If there are units in the mapping for this experiment/variable combination
                    if exp_var in units_map:
                        # Get the units from the mapping and fill it in for this anoms entry
                        source["metadata"]["units"] = units_map[exp_var]
                        # Print that the units were filled for this anoms entry
                        print(f"✓ Filled units for {key}: {units_map[exp_var]}")

            # If the datatype is anoms or climo, try to fill description from mapping
            if datatype in ['anoms', 'climo']:
                # Create a combined key of experiment and variable for the matching
                exp_var = f"{experiment}/{variable}"
                
                # If there are long_names in the mapping for this experiment/variable combination
                if exp_var in long_names_map:
                    # Only fill if long_name is currently unknown or just the variable name
                    if long_name == "unknown" or long_name == variable or len(long_name) < 10:
                        # Get the long_name from the mapping and fill it in
                        source["metadata"]["long_name"] = long_names_map[exp_var]
                        print(f"✓ Filled description for {key}: {long_names_map[exp_var]}")

### Define a function to build the catalog of model data from the base directory ###
def build_model_catalog(base_dir=BASE_DIR):
    # Create an empty catalog to append to
    catalog = {
        "metadata": {
            "title": "Model Data Catalog",
            "version": 1,
            "description": "Auto-generated model data catalog"
        },
        "sources": {}
    }

    ### Process the initialied models first using the model handlers and definitions ##
    print("🔍 Processing initialized models...")
    # For each model name and model configuration in the initialized model definitions
    for model_name, model_config in MODEL_DEFINITIONS.get('initialized', {}).items():
        # Get the relevant model handler function to handle and process the model data
        handler = get_model_handler(model_config['name'])
        # If the handler function exists, print that the model is being processed and use it
        # to process the model data and append it to the catalog
        if handler:
            print(f"\n  Processing {model_name}...")
            handler(catalog, base_dir, model_name, model_config)
        # If the handler function does not exist, print a warning that there is no handler for the model
        else:
            print(f"⚠️ No handler function for type '{model_config['name']}'")

    ### Process the uninitialized models next (add to this later) ###

    ### Process the NMME models using the model handlers and definitions ###
    print("\n🔍 Processing NMME models...")
    for model_name, model_config in MODEL_DEFINITIONS.get('nmme', {}).items():
        # Get the relevant model handler function to handle and process the model data
        handler = get_model_handler(model_config['name'])
        # If the handler function exists, print that the model is being processed and use it
        # to process the model data and append it to the catalog
        if handler:
            print(f"\n  Processing {model_name}...")
            handler(catalog, NMME_DIR, model_name, model_config)
        # If the handler function does not exist, print a warning that there is no handler for the model
        else:
            print(f"⚠️ No handler function for type '{model_config['name']}'")

    ### Process the SubC models using the model handlers and definitions ###
    print("\n🔍 Processing SubC models...")
    for model_name, model_config in MODEL_DEFINITIONS.get('subc', {}).items():
        # Get the relevant model handler function to handle and process the model data
        handler = get_model_handler(model_config['name'])
        # If the handler function exists, print that the model is being processed and use it
        # to process the model data and append it to the catalog
        if handler:
            print(f"\n  Processing {model_name}...")
            handler(catalog, SUBC_DIR, model_name, model_config)
        # If the handler function does not exist, print a warning that there is no handler for the model
        else:
            print(f"⚠️ No handler function for type '{model_config['name']}'")

    ### After processing all models, fill in any missing units for NCAR-CESM2-CLIMO anoms and ###
    ### climo entries using the function to copy them from p1 and raw entries
    print()
    fill_missing_cesm_climo_units(catalog)

    return catalog

# Define a function the write the appended catalog to a .yaml file
def write_catalog(catalog, output_path="catalogs/model.yaml"):
    # Make the file in the output path
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    import yaml # Import the yaml package
    
    # Write to the output path the updated catalog as a .yaml file and print that it was written
    with open(output_path, 'w') as f:
        yaml.dump(catalog, f, sort_keys=False)
    print(f"✅ Model catalog written to {output_path}")

# Run the following if the code is being run as a script
if __name__ == "__main__":
    # Build the catalog using the function
    model_catalog = build_model_catalog()
    # Write the resulting catalog using the function
    write_catalog(model_catalog)

