import access
import plotter
import data_processing as dp
import numpy as np
import time

def main(abi_dp_level, abi_dp_name, start_time, end_time, ncdir, *args):
    gcs_path, gcs_times, local_dir = access.create_path_dirs()
    print('GCS Path: ', gcs_path)
    print('GCS Times: ', gcs_times)
    print('Path created')
    start_time = time.time()
    access.gcs_data_access(gcs_path, gcs_times, local_dir);
    print('Data access + download runtime: %s sec' % (time.time() - start_time)) 
    
    file_list = dp.gather_data(abi_dp_level, abi_dp_name, start_time, end_time, ncdir)
    data_list = dp.goes_data_processor(file_list, *args)
    print('Data processing runtime: %s sec' % (time.time() - start_time))
    i = 0
    for file in data_list: 
        print(np.nanmin(file[0]), np.nanmax(file[0]))
        if i == 0:
            min_val = np.nanmin(file[0])
            max_val = np.nanmax(file[0])
        else:
            if np.nanmin(file[0]) < min_val:
                min_val = np.nanmin(file[0])
            elif np.nanmax(file[0]) > max_val:
                max_val = np.nanmax(file[0])     
        i += 1
            
    print(min_val, max_val)
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
                    bound_box = file[8],)
    
main(2, 'LSTC', 20202500000000, 20202500359599, r'C:\Users\mrgab\Documents\NOAA-CREST\GOES-16 Data\ncdata', -74, 40.8, 1)

### Sample plot implementation
# plot_ncdata(min_val,
#             max_val, 
#             *args,
#             lat_deg = file[1],
#             lon_deg = file[2], 
#             data = file[3], d
#             dataset_name = file[4], 
#             dataset_long_name = file[5], 
#             data_units = file[6], 
#             data_time = file[7],
#             bound_box = file[8],)
