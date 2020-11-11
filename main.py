import access
import plotter
import data_processing as dp
import numpy as np
import time
import warnings

warnings.filterwarnings("ignore")

def main(*args):
    start_time = time.time()
    ### Data access
    gcs_path, goes_times, local_dir = \
        access.create_path_dirs(goes_level=2, goes_product="LSTC", start_date=2020111013, end_date=2020111023)
    access.gcs_data_access(gcs_path, goes_times, local_dir)
    
    ### Data processing
    t = time.time()
    file_list = dp.gather_data(goes_times, local_dir)
    data_list = dp.goes_data_processor(file_list, *args)
    print('Data processing runtime: %.3f sec' % (time.time()-t))
    i = 0
    for file in data_list: 
        if i == 0:
            min_val = np.nanmin(file[0])
            max_val = np.nanmax(file[0])
        else:
            if np.nanmin(file[0]) < min_val:
                min_val = np.nanmin(file[0])
            elif np.nanmax(file[0]) > max_val:
                max_val = np.nanmax(file[0])     
        i += 1
            
    print("Minimum LST: %.3f K | Maximum LST: %.3f K" % (min_val, max_val))
    
    # pa.animate(data_list, min_val, max_val, *args)
    
    ## Data plotting
    for file in data_list:
        print(file[-2]) # Print timestamps for each file read
        plotter.plot_ncdata(min_val,
                    max_val, 
                    *args,
                    lat_deg = file[1],
                    lon_deg = file[2], 
                    data = file[3], 
                    dataset_name = file[4], 
                    dataset_long_name = file[5], 
                    data_units = file[6], 
                    data_time = file[7],
                    bound_box = file[8])
    print('Total runtime: %.3f s' % (time.time() - start_time))
        
    
main(-74.0060, 40.7128, 1)    # New York, NY
# main(-118.2437, 34.0522, 1)   # Los Angeles, CA
# main(-84.3880, 33.7490, 1)    # Atlanta, GA
# main(-87.6298, 41.8781, 1)    # Chicago, IL
# main(-104.9903, 39.7392, 1)   # Denver, CO
# main(-95.3698, 29.7604, 1)    # Houston, TX
# main(-72.6734, 41.7658, 1)    # Hartford, CT
# main(-67.9985, 46.8649, 1)    # Caribou, ME (chosen for CONUS NE limit)
# main(-122.3321, 47.6062, 1)   # Seattle, WA (chosen for CONUS NW limit)
# main(-117.1611, 32.7157, 1)   # San Diego, CA (chosen for CONUS SW limit)
# main(-80.1918, 25.7617, 1)    # Miami, FL (chosen for CONUS SE limit)