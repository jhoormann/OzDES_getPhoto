# OzDES_getPhoto
Here are scripts to download and process the photometric data from the
Dark Energy Survey needed for the OzDES RM program.  The resulting data
tables are in the formed needed for use in the spectrophotometric 
procedures [OzDES_calibSpec](https://github.com/jhoormann/OzDES_calibSpec)

# Scripts

## OzDES_photoDownload.py
This code reads in a file with the location (RA and DEC) for all the
sources provided.  It will query the DES database using easyaccess. The
database query will search for entries which are within 0.00027 degrees
from the provided RA and DEC. It saves the necessary data that the other
scripts will use in order to make the photometric light curves.

## OzDES_photoPrep.py
This code reads in the tables downloaded from the DES database 

# Run Requirements
OzDES_photoDownload.py connects to the DES database using easyaccess
(https://github.com/mgckind/easyaccess) which will need to be installed
prior to use.

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
identification) is specified in the code.

## Light Curve Data Tables

