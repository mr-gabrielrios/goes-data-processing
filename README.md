# GOES Data Processing

The objective of this repo is to host a series of scripts that allows for processing of data from the GOES satellites (GOES-East & GOES-West). Please note that this script is purely intended to facilitate my research work for data scraping, processing, and visualization. Use beyond my own is not protected and not guaranteed. Results *will* vary.

### Known bugs:
* Data processing for non-LST data products (e.g. SSTF) is warped and `data_processing.py` appears to be processing data incorrectly, likely due to the filtering algorithm.
* Entering coordinates beyond the GOES satellite ranges (typically in the Eastern Hemisphere) will yield unpredictable results

On the very off-chance you do try this out, please call out any issues you see - your input is much appreciated!

## Sample Plots
In the unlikely scenario that this repo works on your end, you can get plots that look something like the following. Note that there is no data if satellite image quality is too low or if cloud cover is present.

- Miami, 11/10/2020 @ 09:03 UTC
![Ah damn it, this didn't work, huh?'](https://github.com/mr-gabrielrios/goes-data-processing/blob/master/plots/ABI_L2%2B_LST_Miami_20201110090349.png)

- New York, 11/10/2020 @ 21:03 UTC
![Ah damn it, this didn't work, huh?'](https://github.com/mr-gabrielrios/goes-data-processing/blob/master/plots/ABI_L2%2B_LST_New-York-City_20201110210349.png)

- Los Angeles, 11/10/2020 @ 19:03 UTC
![Ah damn it, this didn't work, huh?'](https://github.com/mr-gabrielrios/goes-data-processing/blob/master/plots/ABI_L2%2B_LST_Los-Angeles_20201110190349.png)