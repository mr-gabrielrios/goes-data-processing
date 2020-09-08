from netCDF4 import Dataset
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cf
import os
from datetime import datetime
import urllib.request

def main(*args):
    gcs_path, local_dir = create_path_dirs()
    print('Path created')
    gcs_data_access(gcs_path, local_dir);
    print('Data accessed')
    lat_deg, lon_deg, data, dataset_name, dataset_long_name, data_units, data_time = goes_img_nav(local_dir);
    print('Satellite image processed')
    ncdata = plot_ncdata(lat_deg, lon_deg, data, dataset_name, dataset_long_name, data_units, data_time, *args);
    print('Script finished, data should be plotting.')
    return ncdata
    
# Objective: specify GOES-16 data type (L1 or L2) and date to prompt download from Google Cloud Storage
# Input: user prompts for desired data product and date
# Output: strings for Google Cloud Storage and local directories for desired data
# Note: GOES only uploads L2 products hourly

def create_path_dirs():
    # Define web path to Google Cloud Repo with GOES-16 data
    g16path = "https://console.cloud.google.com/storage/browser/gcp-public-data-goes-16"

    # This is the root directory for all locally-stored GOES-16 data
    g16dir = r'C:\Users\mrgab\Documents\NOAA-CREST\GOES-16 Data'

    # Grab product level desired by user
    input_product_level = input('Enter a GOES-16 ABI product level: ')
    input_product_level = 'L' + input_product_level

    # Grab data type desired by user
    input_dataset = input('Enter a GOES-16 ABI dataset: ')

    # Grab date from user input
    input_bool = False
    while input_bool == False:  # Ensures only good data is input
        input_date = input('Enter a date in YYYY-MM-DD-HH format:\n HH ranges from 00 to 23 ')
        if len(input_date) == 13 and input_date[4] == '-' and input_date[7] == '-' and input_date[10] == '-':
            input_bool = True
        else:
            print('\n Whoa there skipper, read the instructions and try again!')
            continue
    input_date = input_date.replace('-', '')

    # Generate 3-digit day of year from input_date
    doy = str(datetime(int(input_date[0:4]), int(input_date[4:6]), int(input_date[6:8])).timetuple().tm_yday)
    doy = (3 - len(doy)) * "0" + doy  # Prepend leading zeros to day of the year

    # Generate web path string
    gcs_path = "ABI-" + input_product_level + "-" + input_dataset + "/" + input_date[
                                                                          0:4] + "/" + doy + "/" + input_date[8:10]

    # Generate local directory for downloaded data
    local_dir = g16dir + "\\ABI-" + input_product_level + "-" + input_dataset + "\\" + input_date[
                                                                                       0:4] + "\\" + doy + "\\" + input_date[
                                                                                                                  8:10]

    return gcs_path, local_dir


# Objective: specify GOES-16 data type (L1 or L2) and date to prompt download from Google Cloud Storage
# Input: user prompts for desired data product and date
# Output: .nc file downloaded to specified local directory
# Note: GOES only uploads L2 products hourly

def gcs_data_access(gcs_path, local_dir):
    # 1. Connect to Google Cloud Storage and authenticate for data access
    from google.cloud import storage
    # Reference credentials on local network
    os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\mrgab\Documents\NOAA-CREST\GOES-16 Data\Google Cloud Storage\GOES Data Access-a53f6b6a1e82.json"
    client = storage.Client()

    # 2. Generate paths for Google Cloud Repo (source) and local directory (destination)
    # NOTE: Please only use for L2 products at the moment. Functionality for L1 products to be added.
    # Get Google Cloud path to read from and local path to write to
    # Connect to GOES-16/-17 data bucket
    bucket = client.get_bucket('gcp-public-data-goes-16')
    # Get .nc files that match with user-designate ddata
    blobs_16 = bucket.list_blobs(prefix=gcs_path)
    for blob in blobs_16:
        # If directory doesn't already exist, make it
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        # Generate filename for .nc file
        blob_fn = local_dir + r"\\" + blob.name.split('/')[-1]
        # Download the .nc file
        blob.download_to_filename(blob_fn)
        print("File " + blob_fn + " downloaded!")


# Intended to be a remake of Josh Hrisko's script, lat_lon_reproj(), with added features and different formatting
# Objective: ask user input a year, month, day, and hour and return a fixed grid with processed data
# Objective: be flexible such that the method can take an input directory to work similarly to Josh's
# Input: optional argument - directory with .nc files
# Output: 2D NumPy meshgrid with GOES-16 satellite data

def goes_img_nav(ncdir):
    # Access .nc file
    working_dir = os.getcwd() # Save current working directory
    os.chdir(ncdir)  # Change working directory
    nc_files = [i for i in os.listdir() if i.endswith('.nc')]  # Generate list of .nc files in directory
    g16_data_file = nc_files[0]  # To be modified when user specifies day and hour

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

    print('File name: %s' % g16_data_file)

    return lat_deg, lon_deg, data, dataset_name, dataset_long_name, data_units, data_time


# Intended to be a redo of Josh Hrisko's script, geo_plotter()
# Objective: plot GOES data using Cartopy library
# Input: optional user prompt to define coordinates and window size to focus on
# Output: plot of GOES data for selected variable
# NOTE: This method must be run after having saved data to variables after runnnig goes_img_nav()

def plot_ncdata(lat_deg, lon_deg, data, dataset_name, dataset_long_name, data_units, data_time, *args):
    print(args[:])
    # To-do: user prompt to specify coordinates to be defined

    # 1. Establish viewbox settings
    # 1a. If user provides inputs, use those to define viewbox
    if len(args) > 0:
        [central_lon, central_lat, bound_sz] = args
        # Create box from user input
        bound_box = [central_lon - bound_sz,
                     central_lon + bound_sz,
                     central_lat - bound_sz,
                     central_lat + bound_sz]
        # Generate data for points within viewbox boundaries
        bound_data = data[np.where((lon_deg > bound_box[0]) & \
                                   (lon_deg < bound_box[1]) & \
                                   (lat_deg > bound_box[2]) & \
                                   (lat_deg < bound_box[3]))]
        # Filter out default data values
        bound_data = bound_data[np.where(bound_data.data != 65535)]
    # 1b. Else, use GOES boundaries (typically CONUS or Full Disk)
    else:
        # Filter out default data values
        bound_data = np.where(data.data != 65535)
        # Generate data for points within viewbox boundaries
        bound_box = [np.min(lon_deg[bound_data]),
                     np.max(lon_deg[bound_data]),
                     np.min(lat_deg[bound_data]),
                     np.max(lat_deg[bound_data])]
        central_lon = (bound_box[0] + bound_box[1]) / 2.0
        central_lat = (bound_box[2] + bound_box[3]) / 2.0

        # Convert from degK to degF
    dataF = (data - 273.15) * (9 / 5) + 32

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

    return bound_data

main()