# OzDES_getPhoto
Here are scripts to download and process the photometric data from the
Dark Energy Survey needed for the OzDES RM program.  The resulting data
tables are in the formed needed for use in the OzDES spectrophotometric 
procedures ([OzDES_calibSpec](https://github.com/jhoormann/OzDES_calibSpec)) and can be converted to flux light curves using the [OzDES_makeLC](https://github.com/jhoormann/OzDES_makeLC) scripts.  

## Scripts

### OzDES_photoDownload.py
This code reads in a file with the location (RA and DEC) for all the
sources provided.  It will query the DES database using easyaccess. The
database query will search for entries which are within 0.00027 degrees
from the provided RA and DEC. It saves the necessary data that the other
scripts will use in order to make the photometric light curves.

### OzDES_photoPrep.py
This code reads in the tables downloaded from the DES database.  The data is 
cleaned, magnitudes are calculated from the fluxes/zeropoints, and outliers
are rejected.  The resulting magnitudes are combined based on observation date.
If needed there is a flag to add in the calibration error correction found by
[Burke et al 2018](https://ui.adsabs.harvard.edu/abs/2018AJ....155...41B/abstract).
You also have the option to combine the newly processed data with any archived 
light curves you may have.  The resulting light curves are saved as data tables
and, if the plotFlag = True, the light curves are also saved as .png files.

### OzDES_photoCalc.py
This file contains all the functions that are called as part of the OzDES_photoPrep.py
script.

# Run Requirements
OzDES_photoDownload.py connects to the DES database using easyaccess
(https://github.com/mgckind/easyaccess) which will need to be installed
prior to use.

The code was tested using the following (as stated in requirements.txt)

python==3.5.6

matplotlib==2.2.2

numpy==1.15.2

pandas==0.23.4

easyaccess==1.4.6

To execute just execute >> python OzDES_photoDownload.py to download the data from the database or >> python OzDES_photoPrep.py to clean the data.

# Input Data

## Source Locations
You need to provide a list of sources you are searching for in the
database.  This is a file which has three unlabeled columns: ID RA and
DEC.  RA and DEC are given in units of degrees.  This file will be
called in the OzDES_photoDownload.py script.

# Output Data

## Database Query
The results from the database query performed in OzDES_photoDownload.py
will be saved in a table as prefix + ID + .tab where ID is given in the
source locations file and the prefix (output directory/any desired query
identification) is specified in the code.  These files are then read into
OzDES_photoPrep.py to be cleaned.

## Lightcurve Data Tables
The results from the OzDES_photoPrep.py are saved in a table as prefix + ID
+ \_lc.dat where prefix is the output directory specified in the script.
The data is saved with four columns: date, magnitude, magnitude error, and
band.  The data is saved in accending order based on date and grouped by band.
This is the format that the rest of the OzDES RM scripts assume the lightcurve
data tables will take the form of.

## Lightcurve Figures
If saveFig = True then a figure (prefix + ID + \_lightcurve.png) which includes 
light curves for bands will be generated and saved.

# Reference
If you are using this code please cite the paper where this procedure was first presented and link to this github repository,
[Hoormann et al 2019, MNRAS 487, 3:3650](https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.3650H/abstract)
