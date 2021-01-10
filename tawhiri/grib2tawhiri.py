import logging
import logging.handlers
import argparse
import pygrib
import numpy as np
from dataset import Dataset
from datetime import datetime
import datasetconfig

_grib_name_to_variable = {"Geopotential Height": "height",
                          "U component of wind": "wind_u",
                          "V component of wind": "wind_v"}


global logger
# file is inverse from +90 to -90 in .5 steps
# but we reverse the dataset_array in import_grib_file, so A is the top index
# steps are hard coded for now (TODO: FIX)
latA = (180 - datasetconfig.config[3][1] - datasetconfig.config[3][0] + 1)
latE = latA + datasetconfig.config[3][0]
# file is from 0 to 360 in .5 steps
lonA = datasetconfig.config[4][1]
lonE = datasetconfig.config[4][1] + datasetconfig.config[4][0]

# convert grib file to dataset, assuming dataset starts at starttime
def unpack_grib(filename, starttime, dataset=None):
    if dataset is not None:
        dataset_array = np.ndarray(shape=Dataset.shape, dtype=np.float32, buffer=dataset.array, offset=0, order='C')
    else:
        dataset_array = None

    grib = pygrib.open(filename)
    try:
        # first check file
        print("Checking: ")
        _check_grib_file(grib, filename, dataset_array)

        # then import data
        print("Importing: ")
        _import_grib_file(grib, filename, dataset_array)

        logger.info("XXX unpackad %s", filename)
    finally:
        grib.close()


def _import_grib_file(grib, filename, dataset_array):
    for record, location, location_name in _grib_records(grib):
        if dataset_array is not None:
            # comment from orig: "the fact that latitudes are reveresed here must match check_axes!
            t, p, v = location
            dataset_array[t,p,v,::-1,:] = record.values[latA:latE,lonA:lonE]
            logger.info("...unpacked %s %s %s", filename, location_name, location)

    logger.info("YYY unpacked %s", filename)



def _check_grib_file(grib, filename, dataset_array):
    # Maybe check if file contains all records that we expect
    # Maybe check forecast time
    # Maybe check lat and lon coverage?
    checkedLatLon = False
    for record, location, location_name in _grib_records(grib):
        if not checkedLatLon:
            _check_axes(record)
            checkedLatLon = True
        logger.debug("grib contains %s %s %s", filename, location_name, location);


def _grib_records(grib):
    """
    Yield ``(record, location, location_name)`` tuples in the file `grib`

    ... where location and location_name are tuples containing indicies
        or actual axes names/values corresponding to forecast time, level
        and variable.

        e.g., ``(4, 2, 1)`` ``(12, 950, "wind_u")`` (i.e., 12 hours, 950 mb)

    Records that don't have levels specified as pressure, or are not
    variables that we are interested in, are ignored.
    """

    grib.seek(0)
    for record in grib:
        if record.typeOfLevel != "isobaricInhPa":
            #print("skipping type ",record.typeOfLevel,record.level,record.name);
            continue
        if record.name not in _grib_name_to_variable:
            print("not using: ", record.name, record.level)
            continue

        location_name = (record.forecastTime, record.level,
                         _grib_name_to_variable[record.name])

        for i, n in enumerate(location_name):
            print(i,n)

        try:
            location = tuple(Dataset.axes[i].index(n)
                         for i, n in enumerate(location_name))
            print("yielding ", record, location, location_name)
            yield record, location, location_name
        except:
            print("passing")
            pass

def _check_axes(record):
    print("Check_axes called")
    logger.debug(record.distinctLatitudes[::1]);
    logger.debug(record.distinctLongitudes[::1]);
    pass


### main part...
def main():
#d = Dataset({'ds_time': datetime.now()});
    d = Dataset(datetime.now(), new=True);
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    parent = argparse.ArgumentParser()
    parent.add_argument("infile")
    args = parent.parse_args()

    unpack_grib(args.infile, datetime.now(), d);


if __name__ == "__main__":
    main()
