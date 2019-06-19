import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# -------------------------------------------------- #
# This function was modified from the original light #
# curve generation script provided by Dale Mudd.     #
# -------------------------------------------------- #
# ------------------- flux_2_mag ------------------- #
# -------------------------------------------------- #
# Calculates the magnitude given the known zeropoint #
# and flux.                                          #
# -------------------------------------------------- #

def flux_2_mag(pass_flux_val, pass_zp):
    pass_flux_val = np.array(pass_flux_val)
    pass_zp = np.array(pass_zp)
    return_m = np.zeros(len(pass_flux_val))

    for j in range(len(pass_flux_val)):
            return_m[j] = float(pass_zp[j]) - 2.5*np.log10(float(pass_flux_val[j]))

    return return_m


# -------------------------------------------------- #
# --------------------- getMags -------------------- #
# -------------------------------------------------- #
# Creates a dataframe with date, mag, error, and     #
# quality flag for the specified bands.              #
# -------------------------------------------------- #

def getMags(data, bands):
    dataB = data.copy()

    # Next get the data for the specified bands (ie we don't use z and Y band data for OzDES RM)
    dataB = dataB[dataB['BAND'].isin(bands)]

    # The next are some quality control measures where something obviously went wrong
    # Just include data with positive dates of observations
    dataB = dataB[dataB['MJD_OBS'] > 0]

    # Only include data with a zero point > -1000
    dataB = dataB[dataB['MAG_ZERO'] > -1000]

    # Negative fluxes are not okay, remove those too
    dataB = dataB[dataB['FLUX_AUTO'] > 0]

    # Exclude data where the quality flag is > 3.  Removing data with 1 <= quality flag < 4 creates very sparse light
    # curves but the data looks okay so I will include it.
    dataB = dataB[dataB['FLAGS'] < 4]

    # Now calculate magnitudes and magnitude errors
    dataB['MAG'] = flux_2_mag(dataB['FLUX_AUTO'], dataB['MAG_ZERO'])
    dataB['MAG_ERR'] = dataB['MAG'] - flux_2_mag(dataB['FLUX_AUTO'] + dataB['FLUXERR_AUTO'], dataB['MAG_ZERO'])

    dataB = dataB[dataB['MAG'] != 99]

    return dataB[['MJD_OBS', 'MAG', 'MAG_ERR', 'BAND']]


# -------------------------------------------------- #
# -------------------- findYear -------------------- #
# -------------------------------------------------- #
# Determines which year an observation belongs to.   #
# -------------------------------------------------- #

def findYear(data, years, yearCut):
    yearClass = []
    for o in range(len(data)):
        for y in range(len(years)):
            if int(data['MJD_OBS'].iloc[o]) in yearCut[years[y]]:
                yearClass.append(years[y])

    data['YEAR'] = yearClass

    return data


# -------------------------------------------------- #
# ------------------ dropOutliers ------------------ #
# -------------------------------------------------- #
# Remove any outliers.  These are determined for a   #
# specific year/band.  The average is found and any  #
# values which higher/lower than the average by the  #
# threshold specified is dropped.                    #
# -------------------------------------------------- #

def dropOutliers(data, years, bands, threshold):

    data['OUTLIER'] = np.zeros(len(data))

    # Loop through each combination of band/year
    for y in years:
        for b in bands:
            # Calculate the average for each band/year
            condition = (data['YEAR'] == y) & (data['BAND'] == b)
            avg = data[condition == True]['MAG'].mean()

            # Only do the rest if avg != NAN, avg = NAN if there is no data in that band/year
            if np.isnan(avg) == False:
                diff = abs(data[condition == True]['MAG'] - avg)
                data.loc[diff.index, 'OUTLIER'] = diff.values

    # Drop the outliers and then the column, we don't need it anymore
    data = data[data['OUTLIER'] < threshold]
    data = data.drop(columns='OUTLIER')

    return data


# -------------------------------------------------- #
# -------------------- sortData -------------------- #
# -------------------------------------------------- #
# This orders the data in the form the other OzDES   #
# RM expects.                                        #
# -------------------------------------------------- #

def sortData(data, bands):
    # For the first band sort by date
    sort_data = data[data['BAND'] == bands[0]].sort_values('MJD_OBS')

    # If there are more bands, sort them and add them to the full dataframe
    if len(bands) > 1:
        b = 1
        while b < len(bands):
            bSort = data[data['BAND'] == bands[b]].sort_values('MJD_OBS')
            sort_data = pd.concat([sort_data, bSort], ignore_index=True)
            b += 1

    return sort_data

# -------------------------------------------------- #
# ------------------ combineExtra ------------------ #
# -------------------------------------------------- #
# Combine this data with any other you may have.     #
# -------------------------------------------------- #

def combineExtra(data, fileName, extraYear, yearCut, bands):

    dataOld = pd.read_table(fileName, delim_whitespace=True)

    # Here is the list of indices from the dataOld dataframe that are in the extra year
    indexList = []

    # Loop over missing years to find relevant data
    for y in extraYear:
        for o in range(len(dataOld)):
            if int(dataOld['MJD_OBS'].iloc[o]) in yearCut[y]:
                indexList.append(o)

    # Combine missing data from previous analysis with new data and sort it
    data = pd.concat([data, dataOld.loc[indexList]], ignore_index=True)
    data = sortData(data, bands)

    return data

# -------------------------------------------------- #
# ------------------- coaddDates ------------------- #
# -------------------------------------------------- #
# Coadd all observations taken on the same night.    #
# There is an option to add in the photometric       #
# calibration error correction from Burke et al 2018.#
# -------------------------------------------------- #

def coaddDates(data, calibFlag):

    # Create the dataframe we will save values to
    coadd_data = pd.DataFrame(columns=['MJD_OBS', 'MAG', 'MAG_ERR', 'BAND'])
    band = data['BAND'][0]
    date = int(data['MJD_OBS'][0])

    avgDate = 0
    avgMag = 0
    avgMagErr = 0
    count = 0

    for index in range(len(data['MJD_OBS'][:])):
        # Combine all data from the same band taken on the same night
        if data['BAND'][index] == band and int(data['MJD_OBS'][index]) == date:
            avgDate += data['MJD_OBS'][index]
            avgMag += data['MAG'][index] / pow(data['MAG_ERR'][index], 2)
            avgMagErr += 1 / pow(data['MAG_ERR'][index], 2)
            count += 1
        else:
            # Calibration uncertainty correction from https://iopscience.iop.org/article/10.3847/1538-3881/aa9f22/meta.
            # Add in correction for other bands uncertainty as needed
            if calibFlag == True:
                if band == 'g':
                    calibErr = 0.0073
                if band == 'r':
                    calibErr = 0.0061
                if band == 'i':
                    calibErr = 0.0057
                else:
                    calibErr = 0
            else:
                calibErr = 0

            # Now we are starting a new night, so we will save the data from the previous
            row_data = pd.DataFrame([[avgDate / count, avgMag / avgMagErr, pow((1 / avgMagErr) + pow(calibErr, 2), 0.5),
                                     band]], columns=['MJD_OBS', 'MAG', 'MAG_ERR', 'BAND'])
            coadd_data = pd.concat([coadd_data, row_data], ignore_index=True)

            # Reset the count for the new night
            avgDate = data['MJD_OBS'][index]
            avgMag = data['MAG'][index] / pow(data['MAG_ERR'][index], 2)
            avgMagErr = 1 / pow(data['MAG_ERR'][index], 2)
            count = 1
            date = int(data['MJD_OBS'][index])
            band = data['BAND'][index]

    # At the end save the last night of data
    row_data = pd.DataFrame([[avgDate / count, avgMag / avgMagErr, pow((1 / avgMagErr) + pow(calibErr, 2), 0.5),
                             band]], columns=['MJD_OBS', 'MAG', 'MAG_ERR', 'BAND'])
    coadd_data = pd.concat([coadd_data, row_data], ignore_index=True)

    return coadd_data

# -------------------------------------------------- #
# ----------------- makeFigSingle ------------------ #
# -------------------------------------------------- #
# Function to make figures pretty.                   #
# -------------------------------------------------- #


title_font = {'size': '22', 'color': 'black', 'weight': 'normal', 'verticalalignment': 'bottom'}
axis_font = {'size': '22'}

def makeFigSingle(title, xlabel, ylabel, xlim=[0, 0], ylim=[0, 0]):
    fig = plt.gcf()
    fig.set_size_inches(14, 10, forward=True)

    ax = fig.add_subplot(111)
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(25)

    ax.set_ylabel(ylabel, **axis_font)
    if ylim != [0, 0] and ylim[0] < ylim[1]:
        ax.set_ylim(ylim)

    ax.set_xlabel(xlabel, **axis_font)
    if xlim != [0, 0] and xlim[0] < xlim[1]:
        ax.set_xlim(xlim)

    ax.set_title(title, **title_font)

    return fig, ax