# from .models import camx, cmaq, fv3chem, hysplit, ncep_grib, prepchem
# # from .obs import (
# #                   )
# from .obs import aeronet, airnow, aqs, cems, crn, epa_util, icartt, improve,ish, ish_lite, nadp, openaq
# from .profile import tolnet  # , umbc_aerosol
# from .sat import goes, lpdaac_download, nesdis_edr_viirs, nesdis_eps_viirs
# from .sat import volcat
from . import grids, models, obs, profile, sat

__all__ = ['models', 'obs', 'sat', 'util', 'grids', 'profile']


def rename_latlon(ds):
    """Short summary.

    Parameters
    ----------
    ds : type
        Description of parameter `ds`.

    Returns
    -------
    type
        Description of returned object.

    """
    if 'latitude' in ds.coords:
        return ds.rename({'latitude': 'lat', 'longitude': 'lon'})
    elif 'Latitude' in ds.coords:
        return ds.rename({'Latitude': 'lat', 'Longitude': 'lon'})
    elif 'Lat' in ds.coords:
        return ds.rename({'Lat': 'lat', 'Lon': 'lon'})
    else:
        return ds


def rename_to_monet_latlon(ds):
    """Short summary.

    Parameters
    ----------
    ds : type
        Description of parameter `ds`.

    Returns
    -------
    type
        Description of returned object.

    """
    if 'lat' in ds.coords:
        return ds.rename({'lat': 'latitude', 'lon': 'longitude'})
    elif 'Latitude' in ds.coords:
        return ds.rename({'Latitude': 'latitude', 'Longitude': 'longitude'})
    elif 'Lat' in ds.coords:
        return ds.rename({'Lat': 'latitude', 'Lon': 'longitude'})
    elif 'grid_lat' in ds.coords:
        return ds.rename({'grid_lat': 'latitude', 'grid_lon': 'longitude'})
    else:
        return ds


def dataset_to_monet(dset, lat_name='lat', lon_name='lon', latlon2d=False):
    if len(dset[lat_name].shape) != 2:
        latlon2d = False
    if latlon2d is False:
        dset = coards_to_netcdf(dset, lat_name=lat_name, lon_name=lon_name)
    return dset


def coards_to_netcdf(dset, lat_name='lat', lon_name='lon'):
    from numpy import meshgrid, arange
    lon = dset[lon_name]
    lat = dset[lat_name]
    lons, lats = meshgrid(lon, lat)
    x = arange(len(lon))
    y = arange(len(lat))
    dset = dset.rename({lon_name: 'x', lat_name: 'y'})
    dset.coords['longitude'] = (('y', 'x'), lons)
    dset.coords['latitude'] = (('y', 'x'), lats)
    dset['x'] = x
    dset['y'] = y
    dset = dset.set_coords(['latitude', 'longitude'])
    return dset