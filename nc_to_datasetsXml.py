
# coding: utf-8

# # Create ERDDAP dataset.xml from NetCDF file
# Create an ERDDAP <dataset> snippet by reading a NetCDF CF-1.6 DSG **`featureType=TimeSeries`** file

# In[1]:

import numpy as np
import netCDF4
import uuid
import string
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


# In[2]:

# generate random 12 digit string for DatasetID
rstr = uuid.uuid4().hex[0:12]
rstr=('{}_{}_{}'.format(rstr[:4],rstr[4:8],rstr[8:]))
print(rstr)


# In[3]:

ncfile = '20170129.superv.nc'
#ncfile = 'joe_example.nc'
nc = netCDF4.Dataset(ncfile)


# In[4]:

# information specific to dataset
datasetID='ooi_'+rstr
reloadEveryNMinutes='10'
fileDir='/usgs/data2/rsignell/data/ooi'
fileNameRegex='.*superv\.nc'
subsetVariables='feature_type_instance, latitude, longitude, platform'
infoUrl='http://ceoas.oregonstate.edu/ooi'
cdm_timeseries_variables = subsetVariables
keywords = ','.join(list(nc.variables))


# ERDDAP Valid values are: double (64-bit floating point), float (32-bit floating point), long (64-bit signed integer), int (32-bit signed integer), short (16-bit signed integer), byte (8-bit signed integer), char (essentially: 16-bit unsigned integer), boolean, and String (any length).

# In[5]:

dmap = {'float64':'double',
        'float32':'float',
        'int64':'long',
        'int32':'int',
        'int16':'short',
        'b':'byte',
        'uint16':'char',
        'bool':'boolean',
        'S1':'String',
        'bytes8':'String'}


# In[6]:

# Assign sourceName:[destinationName, ioos_category, dataType, colorBarMinimum, colorBarMaximum]
dvars={}
for var in list(nc.variables):
    # default is ioos_category "Unknown".  Don't calculate limits yet.
    erddap_type = dmap[nc[var].dtype.name]
    dvars[var]={'destinationName':var, 
                'ioos_category':'Unknown', 
                'dataType':erddap_type, 
                'colorBarMinimum':None, 
                'colorBarMaximum':None}
    # calculate limits for all vars that are not strings
    if erddap_type is not 'String':
        dvars[var]['colorBarMinimum']= nc[var][:].min()
        dvars[var]['colorBarMaximum']= nc[var][:].max()
    if np.ma.is_masked(dvars[var]['colorBarMaximum']):
         dvars[var]['colorBarMaximum'] = None
    if np.ma.is_masked(dvars[var]['colorBarMinimum']):
         dvars[var]['colorBarMinimum'] = None

# set destinationName, ioos_category, datatype and limits for coordinate variables
tvar = nc.get_variables_by_attributes(axis='T')[0]
dvars[tvar.name]={'destinationName':'time', 
            'ioos_category':'Time', 
            'dataType':dmap[tvar.dtype.name], 
            'colorBarMinimum':None, 
            'colorBarMaximum':None}

xvar = nc.get_variables_by_attributes(axis='X')[0]
dvars[xvar.name]={'destinationName':'longitude', 
            'ioos_category':'Location', 
            'dataType':dmap[xvar.dtype.name], 
            'colorBarMinimum':-180.0, 
            'colorBarMaximum':180.0}

yvar = nc.get_variables_by_attributes(axis='Y')[0]
dvars[yvar.name]={'destinationName':'latitude', 
            'ioos_category':'Location', 
            'dataType':dmap[yvar.dtype.name], 
            'colorBarMinimum':-90.0, 
            'colorBarMaximum':90.0}

zvar = nc.get_variables_by_attributes(axis='Z')[0]
dvars[zvar.name]={'destinationName':'altitude', 
            'ioos_category':'Location', 
            'dataType':dmap[zvar.dtype.name], 
            'colorBarMinimum':-8000.0, 
            'colorBarMaximum':8000.0}


# In[7]:

dvars


# In[8]:

template = env.get_template('timeSeries.xml')
ds_xml = template.render(datasetID=datasetID,
                      reloadEveryNMinutes=reloadEveryNMinutes,
                      fileDir=fileDir,
                      fileNameRegex=fileNameRegex,
                      subsetVariables=subsetVariables,
                      infoUrl=infoUrl,
                      cdm_timeseries_variables=cdm_timeseries_variables,
                      keywords=keywords,
                      dvars=dvars)   


# In[9]:

with open("Output.xml", "w") as text_file:
    text_file.write("{}".format(ds_xml))


# In[ ]:



