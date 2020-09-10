### Script objective: output N-dimensional NumPy array with desired data
# Inputs (and data types):
    # ABI product level (int)
    # ABI dataset (str)
    # Start time (long)
    # End time (long)
    # Working directory (string)
# Outputs (and data types):
    # N-dimensional NumPy array (ndarray)
  
##############################################################################
    
import os
import os.path
from netCDF4 import Dataset
import numpy as np
import math

### Data gathering algorithm
### Function objective: list all .nc files that satisfy input conditions
# Inputs (and data types)
    # ABI product level (int)
    # ABI dataset (str)
    # Start time (long)
    # End time (long)
    # Root directory with .nc files (str)
# Outputs (and data types):
    # List of complying files (list)      
# Note: goes-data-storage.py must be run before this

def gather_data(abi_dp_level, abi_dp_name, start_time, end_time, ncdir):
    
    date_length = 14 # Length of GOES filename time markers
    date_markers = ["_s", "_e"] # Markers for GOES filename start and end dates
    
    file_list = [] # Create container for list of files within specified timespan
    
    # Iterate over all .nc files in root directory and add those within 
    # the specified timespan to file list
    for root, dirs, files in os.walk(ncdir):
        for fn in [f for f in files if f.endswith(".nc")]:
            # Get indices where start and end markers, _s and _e, end
            start_idx = fn.find(date_markers[0]) + len(date_markers[0])
            end_idx = fn.find(date_markers[1]) + len(date_markers[1])
            # Grab substrings with dates and convert them to integers for comparison
            fst = int(fn[start_idx:start_idx + date_length]) # File start time
            fet = int(fn[end_idx:end_idx + date_length]) # File end time
            # If the specified start time is before the iterand file start time
            # and greater than the iterand file end time, grab it
            if start_time <= fst and end_time >= fet:
                file_list.append(os.path.join(root, fn))
            
    return file_list

# Test run with start time of 2020-01-01 @ 12:00 AM and end time of 2020-03-01 @ 11:59:59 PM
# fl = gather_data(1, 2, 20200010000000, 20200702359599, r'C:\Users\mrgab\Documents\NOAA-CREST\GOES-16 Data')
# print(fl)

##############################################################################

### GOES satellite projection and data processing algorithm
### Function objective: project GOES satellite data onto grid of lat/lon coordinates, provide output data
# Inputs (and data types)
    # Root directory with .nc files (str)
    # File iterand (int)
# Outputs (and data types):
    # Grid of lon/lat degree values (np.meshgrid)
    # Data array (np.ndarray)
    # Dataset abbreviated name (str)
    # Dataset full name (str)
    # Data units (str)
    # Data time (datetime) 
# Note: Intended to be iterated over for list of .nc files

def goes_img_nav(nc_file, *args):
    # Access .nc file
    working_dir = os.getcwd() # Save current working directory
    g16_data_file = nc_file  # To be modified when user specifies day and hour

    # Designate dataset
    g16nc = Dataset(g16_data_file, 'r')  # Create dataset from .nc file
    dataset_name = [i for i in g16nc.variables][0]  # Gets name of relevant dataset

    # .nc file metadata
    dataset_long_name = g16nc.variables[dataset_name].long_name
    data_units = g16nc.variables[dataset_name].units
    data_time = ((g16nc.time_coverage_end).replace('T', ', ')).replace('Z', '')

    # GOES-R projection info
    proj_info = g16nc.variables['goes_imager_projection']
    lon_origin = proj_info.longitude_of_projection_origin
    H = proj_info.perspective_point_height + proj_info.semi_major_axis
    r_eq = proj_info.semi_major_axis
    r_pol = proj_info.semi_minor_axis

    # GOES-R grid info
    lat_rad_1d = g16nc.variables['x'][:]
    lon_rad_1d = g16nc.variables['y'][:]
    data = g16nc.variables[dataset_name][:]

    # Close .nc file
    g16nc.close()
    g16nc = None
    os.chdir(working_dir)  # Revert to script directory

    # Create meshgrid
    lat_rad, lon_rad = np.meshgrid(lat_rad_1d, lon_rad_1d)  # x and y (reference PUG, Section 4.2.8.1)

    # Latitude/longitude projection calculation from satellite radian angle vectors (reference PUG, Section 4.2.8.1)
    lambda_0 = lon_origin * np.pi / 180  # Longitude of origin converted to radians
    a = np.power(np.sin(lat_rad), 2) + np.power(np.cos(lat_rad), 2) * (
                np.power(np.cos(lon_rad), 2) + np.power(np.sin(lon_rad), 2) * np.power(r_eq, 2) / np.power(r_pol, 2))
    b = (-2) * H * np.cos(lat_rad) * np.cos(lon_rad)
    c = np.power(H, 2) - np.power(r_eq, 2)
    r_s = ((-b) - np.sqrt(np.power(b, 2) - 4 * a * c)) / (2 * a)  # distance from satellite to surface

    s_x = r_s * np.cos(lat_rad) * np.cos(lon_rad)
    s_y = (-1 * r_s) * np.sin(lat_rad)
    s_z = r_s * np.cos(lat_rad) * np.sin(lon_rad)

    # Transform radian latitude and longitude values to degrees
    lat_deg = (180 / np.pi) * np.arctan(
        (np.power(r_eq, 2) / np.power(r_pol, 2)) * s_z / (np.sqrt((np.power((H - s_x), 2)) + np.power(s_y, 2))))
    lon_deg = (180 / np.pi) * (lambda_0 - np.arctan(s_y / (H - s_x)))
    
    # Create mask to filter out data where values are default
    data_mask = np.where(data.data != 65535)
    # Generate ndarray with relevant data for future processing/stats
    output_data = np.where(data.data != 65535, data, float('NaN'))
    
    # Create bound box for plotting purposes
    bound_box = [np.min(lon_deg[data_mask]),
                 np.max(lon_deg[data_mask]),
                 np.min(lat_deg[data_mask]),
                 np.max(lat_deg[data_mask])]
    
    # If statement filters out data beyond user-defined window
    if args:
        [central_lon, central_lat, bound_sz] = args[:]
        # Create window from user input
        bound_box = [central_lon - bound_sz,
                     central_lon + bound_sz,
                     central_lat - bound_sz,
                     central_lat + bound_sz]        
        # Generate lons for points within window boundaries
        working_lon_deg = np.where((np.greater(lon_deg, bound_box[0]) & \
                            np.less(lon_deg, bound_box[1])), \
                            lon_deg, float('NaN'))
        # Generate lats for points within window boundaries
        working_lat_deg = np.where((np.greater(lat_deg, bound_box[2]) & \
                            np.less(lat_deg, bound_box[3])), \
                            lat_deg, float('NaN'))
        # Generate ndarray with relevant data for future processing/stats within
        # window boundaries
        output_data = np.where((~np.isnan(working_lon_deg) & ~np.isnan(working_lat_deg)), 
                               data, 
                               float('NaN'))
            
        return output_data, lat_deg, lon_deg, data, dataset_name, dataset_long_name, data_units, data_time, bound_box
    
    # Else, plot CONUS or Full-Disk image
    else:
        return output_data, lat_deg, lon_deg, data, dataset_name, dataset_long_name, data_units, data_time, bound_box

##############################################################################

def goes_data_processor(file_list, *args):
    data_list = []
    for file in file_list:
        output_data, lat_deg, lon_deg, data, dataset_name, dataset_long_name, \
            data_units, data_time, bound_box = goes_img_nav(file, *args)
        data_list.append([output_data, lat_deg, lon_deg, data, dataset_name, dataset_long_name, \
            data_units, data_time, bound_box])        
    return data_list

import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot_ncdata(*args, **kwargs):
    
    [lat_deg, lon_deg, data, dataset_name, dataset_long_name, data_units, data_time, bound_box] = kwargs.values()
        
    if args:
        [central_lon, central_lat, bound_sz] = args[:]
    else:
        central_lon = (bound_box[0] + bound_box[1]) / 2.0
        central_lat = (bound_box[2] + bound_box[3]) / 2.0   
        
    # Convert from degK to degF
    # dataF = (data - 273.15) * (9 / 5) + 32

    # Create figure and format it
    fig = plt.figure(figsize=(6, 6), dpi=200)
    matplotlib.rcParams['font.family'] = ['Arial']

    # Define desired projection. GOES-16 default is PlateCarree. Orthographic is chosen as final projection
    proj = [ccrs.PlateCarree(), ccrs.Orthographic(central_lon, central_lat)];
    ax = plt.axes(projection=proj[1])
    ax.set_extent(bound_box)
    ax.gridlines()
    ax.coastlines(resolution='10m')

    ### Figure metadata
    # Figure title
    plt.title('%s \n %s' % (dataset_long_name, data_time))
    # Figure colormap
    im = ax.pcolormesh(lon_deg.data, lat_deg.data, data, transform=proj[0], cmap=plt.get_cmap('jet'))
    # Scales colorbar to height of plot
    cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])    
    cb = plt.colorbar(im, cax=cax)
    cb.set_label(r'%s [%s]' % (dataset_name, data_units))

    plt.show()

def main(abi_dp_level, abi_dp_name, start_time, end_time, ncdir, *args):
    file_list = gather_data(abi_dp_level, abi_dp_name, start_time, end_time, ncdir)
    data_list = goes_data_processor(file_list, *args)
    for file in data_list:
        print(file[-1]) # Print timestamps for each file read
        plot_ncdata(*args,
                    lat_deg = file[1],
                    lon_deg = file[2], 
                    data = file[3], 
                    dataset_name = file[4], 
                    dataset_long_name = file[5], 
                    data_units = file[6], 
                    data_time = file[7],
                    bound_box = file[8])
    
# main(2, 'LSTC', 20200010000000, 20201802359599, r'C:\Users\mrgab\Documents\NOAA-CREST\GOES-16 Data', -74, 40.8, 1)
main(2, 'LSTC', 20200010000000, 20201802359599, r'C:\Users\mrgab\Documents\NOAA-CREST\GOES-16 Data')