"""
Model catalog definitions and configurations.
Each model's structure, variables, and path templates are defined here for use in the 
building of the data catalog and other potential future scripts.
"""

# Define all model structures in a centralized dictionary to be referenced easily later and to
# allow for special handling of certain models with unique structures 
MODEL_DEFINITIONS = {
    ### Initialized models ###
    'initialized': {
        #1. The structure for the NCAR-CESM2-CLIMO model
        'NCAR-CESM2-CLIMO': {
            'name': 'NCAR-CESM2-CLIMO',
            'description': 'NCAR CESM2 Climatological S2S Hindcasts',
            'path_template': '{BASE_DIR}/initialized/NCAR-CESM2-CLIMO',
            # Experiments under NCAR-CESM2-CLIMO
            'experiments': [
                'S2SHINDCASTSclimoALL',
                'S2SHINDCASTSclimoATM',
                'S2SHINDCASTSclimoLND',
                'S2SHINDCASTSclimoOCN',
                'S2SHINDCASTSclimoATMclimoLND',
                'S2SHINDCASTSclimoOCNclimoATM',
                'S2SHINDCASTSclimoOCNclimoLND'],
            # Datatypes under each experiment
            'datatypes': ['anoms', 'climo', 'p1', 'raw'],
            # Other .nc files to be ignored by the get_nc_files_recursive function here
            'ignored_files': ["NCAR-CESM2.landfrac.nc"],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': 11,
            # Date range of the climo files to be put into catalog metadata (since it is not available in the files themselves)
            'climo_date_range': "1999-01-01 to 2022-12-31"
            },
        #2. The structure for the NCAR-CESM2-SMYLE model
        'NCAR-CESM2-SMYLE': {
            'name': 'NCAR-CESM2-SMYLE',
            'description': 'NCAR CESM2 Seasonal to Multi-Year Large Ensemble',
            'path_template': '{BASE_DIR}/initialized/NCAR-CESM2-SMYLE',
            # Temporal resolutions of the data (skip monthly for now)
            'temporals': ['daily', 'monthly'],
            # The variables to be included in the catalog for this model since there are so many
            'variables': ['PRECC', 'PRECL', 'TREFHT', 'TS', 'U850', 'Z850'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': 20
        }
    },
    ### Uninitialized models (leave empty for now and add later) ###
    'uninitialized': {
        
    },
    ### NMME models ###
    'nmme': {
        #1. The structure for the CanESM5 model
        'CanESM5': {
            'name': 'CanESM5',
            'description': 'Canadian Earth System Model Version 5 Seasonal Forecasts and Hindcasts',
            'path_template': '{NMME_DIR}/CanESM5',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 20,
                'hindcast': 20
            }
        },
        #2. The structure for the COLA-RSMAS-CCSM4 model
        'COLA-RSMAS-CCSM4': {
            'name': 'COLA-RSMAS-CCSM4',
            'description': 'COLA-RSMAS-CCSM4 Seasonal Forecasts and Hindcasts',
            'path_template': '{NMME_DIR}/COLA-RSMAS-CCSM4',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 10,
                'hindcast': 10
            }
        },
        #3. The structure for the COLA-RSMAS-CESM1 model
        'COLA-RSMAS-CESM1': {
            'name': 'COLA-RSMAS-CESM1',
            'description': 'COLA-RSMAS-CESM1 Seasonal Forecasts and Hindcasts',
            'path_template': '{NMME_DIR}/COLA-RSMAS-CESM1',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 10,
                'hindcast': 10
            }
        },
        #4. The structure for the GEM5.2-NEMO model
        'GEM5.2-NEMO': {
            'name': 'GEM5.2-NEMO',
            'description': 'GEM5.2-NEMO Seasonal Forecasts and Hindcasts',
            'path_template': '{NMME_DIR}/GEM5.2-NEMO',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 20,
                'hindcast': 20
            }
        },
        #5. The structure for the GFDL-SPEAR model
        'GFDL-SPEAR': {
            'name': 'GFDL-SPEAR',
            'description': 'GFDL-SPEAR Seasonal Forecasts and Hindcasts',
            'path_template': '{NMME_DIR}/GFDL-SPEAR',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 30,
                'hindcast': 15
            }
        },
        #6. The structure for the NASA-GEOSS2S model
        'NASA-GEOSS2S': {
            'name': 'NASA-GEOSS2S',
            'description': 'NASA GEOSS2S Seasonal Forecasts and Hindcasts',
            'path_template': '{NMME_DIR}/NASA-GEOSS2S',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 10,
                'hindcast': 4
            }
        },
        #7. The structure for the NCAR-CESM1 model (currently empty)
        'NCAR-CESM1': {
            'name': 'NCAR-CESM1',
            'description': 'NCAR CESM1 Seasonal Forecasts and Hindcasts',
            'path_template': '{NMME_DIR}/NCAR-CESM1',
            # Time periods of the data
            'temporals': ['forecast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 'N/A' 
            }
        },
        #8. The structure for the NCEP-CFSv2 model
        'NCEP-CFSv2': {
            'name': 'NCEP-CFSv2-NMME',
            'description': 'NCEP CFSv2 Seasonal Forecasts and Hindcasts',
            'path_template': '{NMME_DIR}/NCEP-CFSv2',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 32,
                'hindcast': 24
            }
        },
        #9. The structure for the NOAA-SFS model
        'NOAA-SFS': {
            'name': 'NOAA-SFS',
            'description': 'NOAA SFS Seasonal Forecasts and Hindcasts',
            'path_template': '{NMME_DIR}/NOAA-SFS',
            # Time periods of the data
            'temporals': ['forecast', 'reforecast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 31,
                'reforecast': 11
            }
        },
        # Add more NMME models as needed...
    },
    ### SubC models ###
    'subc': {
        #1. The structure for the ECCC-GEM model
        'ECCC-GEM': {
            'name': 'ECCC-GEM',
            'description': 'ECCC GEM Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/ECCC-GEM',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 21,
                'hindcast': 4
            }
        },
        #2. The structure for the ECCC-GEPS5 model
        'ECCC-GEPS5': {
            'name': 'ECCC-GEPS5',
            'description': 'ECCC GEPS5 Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/ECCC-GEPS5',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 21,
                'hindcast': 4
            }
        },
        #3. The structure for the ECCC-GEPS6 model
        'ECCC-GEPS6': {
            'name': 'ECCC-GEPS6',
            'description': 'ECCC GEPS6 Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/ECCC-GEPS6',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 21,
                'hindcast': 4
            }
        },
        #4. The structure for the ECCC-GEPS7 model
        'ECCC-GEPS7': {
            'name': 'ECCC-GEPS7',
            'description': 'ECCC GEPS7 Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/ECCC-GEPS7',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 21,
                'hindcast': 4
            }
        },
        #5. The structure for the ECCC-GEPS8 model
        'ECCC-GEPS8': {
            'name': 'ECCC-GEPS8',
            'description': 'ECCC GEPS8 Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/ECCC-GEPS8',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 21,
                'hindcast': 4
            }
        },
        #6. The structure for the EMC-GEFS model
        'EMC-GEFS': {
            'name': 'EMC-GEFS',
            'description': 'EMC GEFS Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/EMC-GEFS',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 21,
                'hindcast': 11
            }
        },
        #7. The structure for the EMC-GEFSv12 model
        'EMC-GEFSv12': {
            'name': 'EMC-GEFSv12',
            'description': 'EMC GEFSv12 Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/EMC-GEFSv12',
            # Time periods of the data
            'temporals': ['forecast'], # hindcast is currently empty, so only include forecast for now
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 31,
            }
        },
        #8. The structure for the EMC-GEFSv12_CPC model
        'EMC-GEFSv12_CPC': {
            'name': 'EMC-GEFSv12_CPC',
            'description': 'EMC GEFSv12_CPC Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/EMC-GEFSv12_CPC',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 31,
                'hindcast': 11
            }
        },
        #9. The structure for the ESRL-FIM model (currently empty)
        'ESRL-FIM': {
            'name': 'ESRL-FIM',
            'description': 'ESRL FIM Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/ESRL-FIM',
            # Time periods of the data
            'temporals': ['forecast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 21
            }
        },
        #10. The structure for the ESRL-FIMr1p1 model
        'ESRL-FIMr1p1': {
            'name': 'ESRL-FIMr1p1',
            'description': 'ESRL FIMr1p1 Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/ESRL-FIMr1p1',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 4,
                'hindcast': 4
            }
        },
        #11. The structure for the GMAO-GEOS_V2p1 model
        'GMAO-GEOS_V2p1': {
            'name': 'GMAO-GEOS_V2p1',
            'description': 'GMAO GEOS_V2p1 Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/GMAO-GEOS_V2p1',
            # Time periods of the data
            'temporals': ['forecast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 4
            }
        },
        #12. The structure for the GMAO-GEOS_V2p1_5daily model
        'GMAO-GEOS_V2p1_5daily': {
            'name': 'GMAO-GEOS_V2p1_5daily',
            'description': 'GMAO GEOS_V2p1_5daily Subseasonal Forecasts',
            'path_template': '{SUBC_DIR}/GMAO-GEOS_V2p1_5daily',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 4,
                'hindcast': 4
            }
        },
        #13. The structure for the NCEP-CFSv2 model
        'NCEP-CFSv2': {
            'name': 'NCEP-CFSv2-SUBC',
            'description': 'NCEP CFSv2 Subseasonal Forecasts and Hindcasts',
            'path_template': '{SUBC_DIR}/NCEP-CFSv2',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 4,
                'hindcast': 1
            }
        },
        #14. The structure for the NRL-NESM model
        'NRL-NESM': {
            'name': 'NRL-NESM',
            'description': 'NRL NESM Subseasonal Forecasts and Hindcasts',
            'path_template': '{SUBC_DIR}/NRL-NESM',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 1,
                'hindcast': 1
            }
        },
        #15. The structure for the RSMAS-CCSM4 model
        'RSMAS-CCSM4': {
            'name': 'RSMAS-CCSM4',
            'description': 'RSMAS-CCSM4 Subseasonal Forecasts and Hindcasts',
            'path_template': '{SUBC_DIR}/RSMAS-CCSM4',
            # Time periods of the data
            'temporals': ['forecast', 'hindcast'],
            # Number of ensemble members (if applicable) to be put into catalog metadata
            'ensemble_members': {
                'forecast': 9,
                'hindcast': 3
            }
        },
        # Add more SubC models as needed...
    }
}