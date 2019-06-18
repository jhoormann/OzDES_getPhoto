import numpy as np
import easyaccess as ea

# This is a simple script which will query the DES database, searching for sources based on RA and DEC, and pulls
# the relevant info to get photometric light curves needed for the OzDES RM analysis.

# This code connects to the DES database using easyaccess (https://github.com/mgckind/easyaccess) which will need to be
# installed prior to use.

# The filename with the the following information for each sources you are searching for
# ID Name, RA and DEC (in degrees)
# Assumes columns are NOT labeled

fileName = "RM_Source_Locations.txt"
RM_names = np.loadtxt("RM_Source_Locations.txt", dtype={'names':('ID', 'RA', 'DEC'), 'formats':(np.int, np.float,
                                                                                                np.float)})

length = len(RM_names)

# Connect to the database
connection = ea.connect()

# Directory to save output from query and any filename prefixes to identify your query.
outLoc = "query/DESY6_"

# Now loop through the sources and search for the relevant data and save in the above directory as a .tab file
# identified by the ID specified in the input file.

for i in range(length):
        print("Getting photometry for " + str(RM_names['ID'][i]))
        query = "select fc.FILENAME, fc.BAND, fc.RA, fc.DEC, fc.NITE, fc.EXPNUM, ex.MJD_OBS, fc.FLUX_AUTO, " \
                "fc.FLUXERR_AUTO, fc.FLAGS, zp.MAG_ZERO, zp.SIGMA_MAG_ZERO, zp.INSERT_DATE from Y6A1_FINALCUT_OBJECT " \
                "fc LEFT JOIN Y6A1_ZEROPOINT zp ON fc.FILENAME = zp.CATALOGNAME LEFT JOIN Y6A1_EXPOSURE ex ON " \
                "(fc.EXPNUM = ex.EXPNUM and fc.NITE = ex.NITE) where ra between (" + str(RM_names['RA'][i]) \
                + " - 0.00027) and (" + str(RM_names['RA'][i])+ "+ 0.00027) and dec between (" + \
                str(RM_names['DEC'][i]) + "- 0.00027) and (" + str(RM_names['DEC'][i]) + "+ 0.00027)"

        connection.query_and_save(query, outLoc + str(RM_names['ID'][i]) + '.tab')



