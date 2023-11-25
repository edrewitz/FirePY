# THIS SCRIPT DOWNLOADS FORECAST DATA FROM THE NOAA/NWS FTP SERVER
#
# THIS IS THE NWS FTP DATA ACCESS FILE FOR FIREPY
#
# DEPENDENCIES INCLUDE:
# 1. MATPLOTLIB
# 2. DATETIME
# 3. PYTZ
# 4. CARTOPY
# 5. METPY
#
#  (C) ERIC J. DREWITZ
#       METEOROLOGIST
#         USDA/USFS

#### IMPORTS ####
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
from metpy.plots import colortables
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import metpy.plots as mpplots
from metpy.plots import USCOUNTIES
import numpy as np

def plot_creation_time():
    '''
    FUNCTION TO GET THE CURRENT DATE/TIME FOR PLOT HEADER/FOOTER

    RETURNS VALUES IN THE ORDER OF:
    1. CURRENT LOCAL DATE/TIME
    2. CURRENT UTC DATE/TIME

    PYTHON MODULE DEPENDENCIES:
    1. DATETIME
    2. PYTZ
    
    COPYRIGHT (C) ERIC J. DREWITZ 2023
    '''

    now = datetime.now()
    UTC = now.astimezone(pytz.utc)
    
    sec = now.second
    mn = now.minute
    hr = now.hour
    dy = now.day
    mon = now.month
    yr = now.year
    
    sec1 = UTC.second
    mn1 = UTC.minute
    hr1 = UTC.hour
    dy1 = UTC.day
    mon1 = UTC.month
    yr1 = UTC.year
    
    Local_Time_Now = datetime(yr, mon, dy, hr, mn, sec)
    UTC_Now = datetime(yr1, mon1, dy1, hr1, mn1, sec1)
    
    return Local_Time_Now, UTC_Now


def plot_NWS_forecast(first_GRIB_file, second_GRIB_file, third_GRIB_file, fourth_GRIB_file, fifth_GRIB_file, count_of_GRIB_files, local_time, utc_time, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, color_table, color_table_start, color_table_stop, color_table_step): 

    '''
    THIS FUNCTION MAKES A GENERIC CUSTOMIZED PLOT OF THE LATEST NOAA/NWS NDFD GRID FORECAST DATA

    THE FOLLOWING IS CUSTOMIZABLE BY THE USER:
    1. LATITUDE/LONGITUDE BOUNDS OF THE PLOT
    2. CENTRAL LATITUDE/LONGITUDE AND STANDARD PARALLELS FOR PLOT
    3. WEATHER PARAMETER 
    4. COLOR TABLE FOR PLOT 
    5. COLOR TABLE START, STOP AND STEP

    PYTHON MODULE DEPENDENCIES:
    1. CARTOPY
    2. METPY
    3. NUMPY
    4. MATPLOTLIB
    '''

    files = count_of_GRIB_files
    mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
    datacrs = ccrs.PlateCarree()
    
   
    if files == 1:
        grb_1_vals = first_GRIB_file.values
        grb_1_date = first_GRIB_file.validDate
        lats, lons = first_GRIB_file.latlons()

        fig = plt.figure(figsize=(10,10))
        fig.text(0.13, 0.08, 'Plot Created With FirePY (C) Eric J. Drewitz 2023 | Data Source: NOAA/NWS/NDFD\n               Image Created: ' + local_time.strftime('%m/%d/%Y %H:%M Local') + ' | ' + utc.strftime('%m/%d/%Y %H:%M UTC'), fontweight='bold')
        fig.suptitle("National Weather Service Forecast", fontweight='bold')
        
        ax = plt.subplot(1, 1, 1, projection=mapcrs)
        ax.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Valid: ' + grb_1_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs = ax.contourf(lons, lats, grb_1_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar = fig.colorbar(cs, shrink=0.80)

    if files == 2:
        grb_1_vals = first_GRIB_file.values
        grb_1_date = first_GRIB_file.validDate
        grb_2_vals = second_GRIB_file.values
        grb_2_date = second_GRIB_file.validDate        
        
        lats_1, lons_1 = first_GRIB_file.latlons()
        lats_2, lons_2 = second_GRIB_file.latlons()

        fig = plt.figure(figsize=(9,5))
        fig.text(0.13, 0.08, 'Plot Created With FirePY (C) Eric J. Drewitz 2023 | Data Source: NOAA/NWS/NDFD\n               Image Created: ' + local_time.strftime('%m/%d/%Y %H:%M Local') + ' | ' + utc_time.strftime('%m/%d/%Y %H:%M UTC'), fontweight='bold')
        fig.suptitle("National Weather Service Forecast", fontweight='bold')
        
        ax0 = plt.subplot(1, 2, 1, projection=mapcrs)
        ax0.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax0.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax0.add_feature(cfeature.STATES, linewidth=0.5)
        ax0.add_feature(USCOUNTIES, linewidth=0.75)
        ax0.set_title('Valid: ' + grb_1_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs0 = ax0.contourf(lons_1, lats_1, grb_1_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar0 = fig.colorbar(cs0, shrink=0.80)

        ax1 = plt.subplot(1, 2, 2, projection=mapcrs)
        ax1.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Valid: ' + grb_2_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs1 = ax1.contourf(lons_2, lats_2, grb_2_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar1 = fig.colorbar(cs1, shrink=0.80)

    if files == 3:
        grb_1_vals = first_GRIB_file.values
        grb_1_date = first_GRIB_file.validDate
        grb_2_vals = second_GRIB_file.values
        grb_2_date = second_GRIB_file.validDate
        grb_3_vals = third_GRIB_file.values
        grb_3_date = third_GRIB_file.validDate  
        
        lats_1, lons_1 = first_GRIB_file.latlons()
        lats_2, lons_2 = second_GRIB_file.latlons()
        lats_3, lons_3 = third_GRIB_file.latlons()

        fig = plt.figure(figsize=(15,5))
        fig.text(0.13, 0.08, 'Plot Created With FirePY (C) Eric J. Drewitz 2023 | Data Source: NOAA/NWS/NDFD\n               Image Created: ' + local_time.strftime('%m/%d/%Y %H:%M Local') + ' | ' + utc_time.strftime('%m/%d/%Y %H:%M UTC'), fontweight='bold')
        fig.suptitle("National Weather Service Forecast", fontweight='bold')
        
        ax0 = plt.subplot(1, 3, 1, projection=mapcrs)
        ax0.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax0.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax0.add_feature(cfeature.STATES, linewidth=0.5)
        ax0.add_feature(USCOUNTIES, linewidth=0.75)
        ax0.set_title('Valid: ' + grb_1_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs0 = ax0.contourf(lons_1, lats_1, grb_1_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar0 = fig.colorbar(cs0, shrink=0.80)

        ax1 = plt.subplot(1, 3, 2, projection=mapcrs)
        ax1.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Valid: ' + grb_2_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs1 = ax1.contourf(lons_2, lats_2, grb_2_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar1 = fig.colorbar(cs1, shrink=0.80)

        ax2 = plt.subplot(1, 3, 3, projection=mapcrs)
        ax2.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Valid: ' + grb_3_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs2 = ax2.contourf(lons_3, lats_3, grb_3_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar2 = fig.colorbar(cs2, shrink=0.80)

    if files == 4:
        grb_1_vals = first_GRIB_file.values
        grb_1_date = first_GRIB_file.validDate
        grb_2_vals = second_GRIB_file.values
        grb_2_date = second_GRIB_file.validDate
        grb_3_vals = third_GRIB_file.values
        grb_3_date = third_GRIB_file.validDate 
        grb_4_vals = fourth_GRIB_file.values
        grb_4_date = fourth_GRIB_file.validDate 
        
        lats_1, lons_1 = first_GRIB_file.latlons()
        lats_2, lons_2 = second_GRIB_file.latlons()
        lats_3, lons_3 = third_GRIB_file.latlons()
        lats_4, lons_4 = fourth_GRIB_file.latlons()

        fig = plt.figure(figsize=(12,10))
        fig.text(0.13, 0.08, 'Plot Created With FirePY (C) Eric J. Drewitz 2023 | Data Source: NOAA/NWS/NDFD\n               Image Created: ' + local_time.strftime('%m/%d/%Y %H:%M Local') + ' | ' + utc_time.strftime('%m/%d/%Y %H:%M UTC'), fontweight='bold')
        fig.suptitle("National Weather Service Forecast", fontweight='bold')
        
        ax0 = plt.subplot(2, 2, 1, projection=mapcrs)
        ax0.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax0.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax0.add_feature(cfeature.STATES, linewidth=0.5)
        ax0.add_feature(USCOUNTIES, linewidth=0.75)
        ax0.set_title('Valid: ' + grb_1_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs0 = ax0.contourf(lons_1, lats_1, grb_1_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar0 = fig.colorbar(cs0, shrink=0.80)

        ax1 = plt.subplot(2, 2, 2, projection=mapcrs)
        ax1.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Valid: ' + grb_2_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs1 = ax1.contourf(lons_2, lats_2, grb_2_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar1 = fig.colorbar(cs1, shrink=0.80)

        ax2 = plt.subplot(2, 2, 3, projection=mapcrs)
        ax2.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Valid: ' + grb_3_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs2 = ax2.contourf(lons_3, lats_3, grb_3_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar2 = fig.colorbar(cs2, shrink=0.80)

        ax3 = plt.subplot(2, 2, 4, projection=mapcrs)
        ax3.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.STATES, linewidth=0.5)
        ax3.add_feature(USCOUNTIES, linewidth=0.75)
        ax3.set_title('Valid: ' + grb_4_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs3 = ax3.contourf(lons_4, lats_4, grb_4_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar3 = fig.colorbar(cs3, shrink=0.80) 

    if files >= 5:
        grb_1_vals = first_GRIB_file.values
        grb_1_date = first_GRIB_file.validDate
        grb_2_vals = second_GRIB_file.values
        grb_2_date = second_GRIB_file.validDate
        grb_3_vals = third_GRIB_file.values
        grb_3_date = third_GRIB_file.validDate 
        grb_4_vals = fourth_GRIB_file.values
        grb_4_date = fourth_GRIB_file.validDate 
        grb_5_vals = fifth_GRIB_file.values
        grb_5_date = fifth_GRIB_file.validDate
          
        
        lats_1, lons_1 = first_GRIB_file.latlons()
        lats_2, lons_2 = second_GRIB_file.latlons()
        lats_3, lons_3 = third_GRIB_file.latlons()
        lats_4, lons_4 = fourth_GRIB_file.latlons()
        lats_5, lons_5 = fifth_GRIB_file.latlons()

        fig = plt.figure(figsize=(25,5))
        fig.text(0.13, 0.08, 'Plot Created With FirePY (C) Eric J. Drewitz 2023 | Data Source: NOAA/NWS/NDFD\n               Image Created: ' + local_time.strftime('%m/%d/%Y %H:%M Local') + ' | ' + utc_time.strftime('%m/%d/%Y %H:%M UTC'), fontweight='bold')
        fig.suptitle("National Weather Service Forecast", fontweight='bold')
        
        ax0 = plt.subplot(1, 5, 1, projection=mapcrs)
        ax0.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax0.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax0.add_feature(cfeature.STATES, linewidth=0.5)
        ax0.add_feature(USCOUNTIES, linewidth=0.75)
        ax0.set_title('Valid: ' + grb_1_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs0 = ax0.contourf(lons_1, lats_1, grb_1_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar0 = fig.colorbar(cs0, shrink=0.80)

        ax1 = plt.subplot(1, 5, 2, projection=mapcrs)
        ax1.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Valid: ' + grb_2_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs1 = ax1.contourf(lons_2, lats_2, grb_2_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar1 = fig.colorbar(cs1, shrink=0.80)

        ax2 = plt.subplot(1, 5, 3, projection=mapcrs)
        ax2.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Valid: ' + grb_3_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs2 = ax2.contourf(lons_3, lats_3, grb_3_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar2 = fig.colorbar(cs2, shrink=0.80)

        ax3 = plt.subplot(1, 5, 4, projection=mapcrs)
        ax3.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.STATES, linewidth=0.5)
        ax3.add_feature(USCOUNTIES, linewidth=0.75)
        ax3.set_title('Valid: ' + grb_4_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs3 = ax3.contourf(lons_4, lats_4, grb_4_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar3 = fig.colorbar(cs3, shrink=0.80)

        ax4 = plt.subplot(1, 5, 4, projection=mapcrs)
        ax4.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax4.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax4.add_feature(cfeature.STATES, linewidth=0.5)
        ax4.add_feature(USCOUNTIES, linewidth=0.75)
        ax4.set_title('Valid: ' + grb_5_date.strftime('%m/%d/%Y %HZ'), fontweight='bold')

        cs4 = ax4.contourf(lons_5, lats_5, grb_5_vals, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, transform=datacrs)
        cbar4 = fig.colorbar(cs4, shrink=0.80) 

    return fig
