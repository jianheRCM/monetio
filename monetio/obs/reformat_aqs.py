#!/usr/bin/env python
# coding: utf-8

# ## MONET-Analysis Speciated PM prep notebook
# 
# ### How to use
# 
# - start notebook and 
# - in cell 2 set the start date and end date
# - in cell 2 set the filename output (something like AERONET_L15_STARTDATE_ENDDATE.nc with STARTDATE and ENDDATE in YYYYMMDD format)

# In[ ]:


import monetio as mio
import numpy as np
import pandas as pd
import xarray as xr
from melodies_monet.util import write_util


# In[ ]:


# helper function for local time.  Could be important for EPA statistics
def get_local_time(ds):
    from numpy import zeros
    if 'utcoffset' in ds.data_vars:
        tim = t.time.copy()
        o = tim.expand_dims({'x':t.x.values}).transpose('time','x')
        on = xr.Dataset({'time_local':o,'utcoffset':t.utcoffset})
        y = on.to_dataframe()
        y['time_local'] = y.time_local + pd.to_timedelta(y.utcoffset, unit='H')
        time_local = y[['time_local']].to_xarray()
        ds = xr.merge([ds,time_local])
    else:
        print('set time_local = time')
        tim = t.time.copy()
        o = tim.expand_dims({'x':t.x.values}).transpose('time','x')
        on = xr.Dataset({'time_local':o})
        y = on.to_dataframe()
        y['time_local'] = y.time_local
        time_local = y[['time_local']].to_xarray()
        ds = xr.merge([ds,time_local])
    return ds


# In[ ]:


# set the dates
obs_freq = 'Daily'  # Daily or Hourly
dates = pd.date_range(start='2019-04-01',end='2019-08-31',freq='H') # note this just get the start year for these 

#SET NETWORK
network = 'IMPROVE'  # CSN NCORE CASTNET IMPROVE
#network = None # CSN NCORE CASTNET IMPROVE

# set the output filename
if network is None:
    outname = 'AQS_'+obs_freq+'_2019.nc'
else:
    outname = network+'_'+obs_freq+'_2019.nc'

# add the data, need to set meta=True for AQS obs, recommand daily data for PM species
if obs_freq == 'Daily':
    df = mio.aqs.add_data(dates,param=['PM2.5','SPEC'], wide_fmt=False, daily=True, meta=True, network=network)
    #df = mio.aqs.add_data(dates,param=['PM10SPEC','SPEC'], wide_fmt=False, daily=True, meta=True, network=network)
else:
    df = mio.aqs.add_data(dates,param=['OZONE','CO','PM2.5','NO2','NONOxNOy'], wide_fmt=False, daily=False, meta=True, network=network)
    #df = mio.aqs.add_data(dates,param=['PM2.5'], wide_fmt=False, daily=False, meta=True)

#drop any data with nans 
df['obs'][df.obs <= 0] = np.nan
df = df.rename({'latitude_x':'latitude','longitude_x':'longitude','gmt_offset':'utcoffset'}, axis=1).dropna(subset=['obs']).dropna(subset=['latitude','longitude'])
#print(df['utcoffset'].dtypes)
df['utcoffset']=df['utcoffset'].astype(int)
# In[ ]:

df = df.dropna(subset=['latitude','longitude']) # drop all values without an assigned latitude and longitude
if obs_freq == 'Daily':
    df['time']=df.time_local.values
dfp = df.rename({'siteid':'x'},axis=1).pivot_table(values='obs',index=['time','x'], columns=['variable']) # convert to wide format
dfx = dfp.to_xarray() # convert to xarray

# When converting to wide format we have to remerge the site data back into the file.
dfpsite = df.rename({'siteid':'x'},axis=1).drop_duplicates(subset=['x']) # droping duplicates and renaming
# convert sites to xarray
test = dfpsite.drop(['time','time_local','variable','obs'],axis=1).set_index('x').dropna(subset=['latitude','longitude']).to_xarray()
# merge sites back into the data
t = xr.merge([dfx,test])

if obs_freq == 'Hourly':
    # get local time
    tt = get_local_time(t)
else:
    tim = t.time.copy()
    o = tim.expand_dims({'x':t.x.values}).transpose('time','x')
    on = xr.Dataset({'time_local':o})
    yy = on.to_dataframe()
    yy['time_local'] = yy.time_local
    time_local = yy[['time_local']].to_xarray()
    tt = xr.merge([t,time_local])

# add siteid back as a variable and create x as an array of integers
tt['siteid'] = (('x'),tt.x.values)
tt['x'] = range(len(tt.x))
# expand dimensions so that it is (time,y,x)
t = tt.expand_dims('y').set_coords(['siteid','latitude','longitude']).transpose('time','y','x')

#wite out to filename set in cell 2
write_util.write_ncf(t,outname)





