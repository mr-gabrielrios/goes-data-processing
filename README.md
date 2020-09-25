# GOES Data Processing

The objective of this repo is to host a series of scripts that allows for processing of data from the GOES satellites (GOES-East & GOES-West). Please note that this script is purely intended to facilitate my research work for data scraping, processing, and visualization. Use beyond my own is not protected and not guaranteed. Results *will* vary.

### Known bugs:
* Data processing for non-LST data products (e.g. SSTF) is warped and 'data_processing.py' appears to be processing data incorrectly, likely due to the filtering algorithm.
* Entering coordinates beyond the GOES satellite ranges (typically in the Eastern Hemisphere) will yield unpredictable results

On the very off-chance you do try this out, please call out any issues you see - your input is much appreciated!
