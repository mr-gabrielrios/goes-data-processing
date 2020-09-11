import os
from datetime import datetime
import time

def main():
    gcs_path, gcs_times, local_dir = create_path_dirs()
    print('GCS Path: ', gcs_path)
    print('GCS Times: ', gcs_times)
    print('Path created')
    start_time = time.time()
    gcs_data_access(gcs_path, gcs_times, local_dir);
    print('Data accessed & downloaded')
    print('Runtime: %s sec' % (time.time() - start_time))
    
# Objective: specify GOES-16 data type (L1 or L2) and date to prompt download 
#            from Google Cloud Storage
# Input: user prompts for desired data product and date
# Output: strings for Google Cloud Storage and local directories for desired data
# Note: GOES only uploads L2 products hourly

def create_path_dirs():
    # Define web path to Google Cloud Repo with GOES-16 data
    g16path = "https://console.cloud.google.com/storage/browser/gcp-public-data-goes-16"

    # This is the root directory for all locally-stored GOES-16 data
    g16dir = r'C:\Users\mrgab\Documents\NOAA-CREST\GOES-16 Data\ncdata'

    # Grab product level desired by user
    input_product_level = input('Enter a GOES-16 ABI product level: ')
    input_product_level = 'L' + input_product_level

    # Grab data type desired by user
    input_dataset = input('Enter a GOES-16 ABI dataset: ')

    # Grab date from user input - input_bool controls while loop
    input_bool = [False, False]
    # Generate empty list to hold dates
    input_dates = 2*[None]
    
    # Get start date from user input
    while input_bool[0] == False:  # Ensures only good data is input
        date_str = input('Enter a start date in YYYY-MM-DD-HH format:\n HH ranges from 00 to 23 ')
        if len(date_str) == 13 and date_str[4] == '-' and date_str[7] == '-' and date_str[10] == '-':
            input_bool[0] = True
        else:
            print('\n Whoa there skipper, read the instructions and try again!')
            continue
    input_dates[0] = date_str.replace('-', '')
        
    # Get end date from user input
    while input_bool[1] == False:  # Ensures only good data is input
        date_str = input('Enter an end date in YYYY-MM-DD-HH format:\n HH ranges from 00 to 23 ')
        if len(date_str) == 13 and date_str[4] == '-' and date_str[7] == '-' and date_str[10] == '-':
            input_bool[1] = True
        else:
            print('\n Whoa there skipper, read the instructions and try again!')
            continue
    input_dates[1] = date_str.replace('-', '')
    
    print(input_dates)
    
    # Generate web path string
    gcs_path = "ABI-" + input_product_level + "-" + input_dataset

    # Initialize list of GCS bucket paths and times
    gcs_times = [None] * len(input_dates)

    # Generate 3-digit day of year from input_date
    i = 0 # Iterand for for-loop
    for date in input_dates:
        doy = str(datetime(int(date[0:4]), int(date[4:6]),
                           int(date[6:8])).timetuple().tm_yday)
        # Prepend leading zeros to day of the year
        doy = (3 - len(doy)) * "0" + doy
        # Append zeroes for minutes, seconds, and millisecond
        gcs_times[i] = date[0:4] + doy + date[8:10] + "00000"
        i += 1

    return gcs_path, gcs_times, g16dir


# Objective: specify GOES-16 data type (L1 or L2) and date to prompt download 
#            Google Cloud Storage
# Input:     user prompts for desired data product and date
# Output:    .nc file downloaded to specified local directory
# Note: GOES only uploads L2 products hourly

def gcs_data_access(gcs_path, gcs_times, local_dir):
    print(local_dir)
    # 1. Connect to Google Cloud Storage and authenticate for data access
    from google.cloud import storage
    # Reference credentials on local network
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
        r"C:\Users\mrgab\Documents\NOAA-CREST\GOES-16 Data\Google Cloud Storage\GOES Data Access-a53f6b6a1e82.json"
    client = storage.Client()

    # 2. Generate paths for Google Cloud Repo (source) and local directory (destination)
    # NOTE: Please only use for L2 products at the moment. Functionality for L1 products to be added.
    # Get Google Cloud path to read from and local path to write to
    # Connect to GOES-16/-17 data bucket
    bucket = client.get_bucket('gcp-public-data-goes-16')
    # Get .nc files that match with user-designate ddata
    blobs_16 = bucket.list_blobs(prefix=gcs_path)
    
    date_length = 14 # Length of GOES filename time markers
    date_markers = ["_s", "_e"] # Markers for GOES filename start and end dates
    
    for blob in blobs_16:
        # Get indices where start and end markers, _s and _e, end
        start_idx = blob.name.find(date_markers[0]) + len(date_markers[0])
        end_idx = blob.name.find(date_markers[1]) + len(date_markers[1])
        # Grab substrings with dates and convert them to integers for comparison
        fst = int(blob.name[start_idx:start_idx + date_length]) # File start time
        fet = int(blob.name[end_idx:end_idx + date_length]) # File end time
        # If the specified start time is before the iterand file start time
        # and greater than the iterand file end time, grab it
        if int(gcs_times[0]) <= fst and int(gcs_times[1]) >= fet:
            blob_fn = local_dir + r"\\" + blob.name.split('/')[-1]
            # Download the .nc file
            blob.download_to_filename(blob_fn)
            print("File " + blob_fn + " downloaded!")

main()