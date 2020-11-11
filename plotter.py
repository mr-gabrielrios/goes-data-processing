import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cartopy
import cartopy.crs as ccrs

def plot_ncdata(min_val, max_val, *args, **kwargs):
    
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

    # Define desired projection.
    # GOES-16 default is PlateCarree. Orthographic is chosen as final projection
    proj = [ccrs.PlateCarree(), ccrs.Orthographic(central_lon, central_lat)];
    ax = plt.axes(projection=proj[1])
    ax.set_extent(bound_box)
    gl = ax.gridlines(draw_labels=True, dms=True)
    gl.xlabels_top = False
    gl.ylabels_right = False
    ax.coastlines(resolution='10m')
    ax.add_feature(cartopy.feature.BORDERS, linestyle=':')
    ax.add_feature(cartopy.feature.LAKES, alpha=0.5)

    ### Figure metadata
    # Figure title
    fontname = "FreeSans" # Change to Arial on Windows, Helvetica on Mac
    plt.title('%s \n %s UTC' % (dataset_long_name, data_time), fontname=fontname)
    # Figure colormap
    im = ax.pcolormesh(lon_deg.data, 
                       lat_deg.data, 
                       data, 
                       vmin = min_val,
                       vmax = max_val,
                       transform=proj[0], 
                       cmap=plt.get_cmap('jet'))
    # Scales colorbar to height of plot
    cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])    
    cb = plt.colorbar(im, cax=cax)
    
    cb.set_label(r'%s [%s]' % (dataset_name, data_units), fontname=fontname) 
    gl.xlabel_style = {'fontfamily': fontname}
    gl.ylabel_style = {'fontfamily': fontname}
    for label in cb.ax.yaxis.get_ticklabels():
        label.set_family(fontname)
    
    plt.show()
    return fig, im