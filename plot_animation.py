import plotter
from matplotlib import pyplot as plt

plt.rcParams['animation.convert_path'] = r"C:\Program Files\ImageMagick-7.0.10-Q16\magick.exe"

def animate(data_list, min_val, max_val, *args):
    imlist = []
    i = 0
    for file in data_list:
            print(file[-2]) # Print timestamps for each file read
            [im, im_null] = plotter.plot_ncdata(min_val,
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
            i += 1
            imlist.append(im)
    
    plt.show()

