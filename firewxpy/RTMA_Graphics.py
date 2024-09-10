import pytz
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import metpy.plots as mpplots
import metpy.calc as mpcalc
import numpy as np
import firewxpy.parsers as parsers
import firewxpy.data_access as da
import firewxpy.geometry as geometry
import firewxpy.colormaps as colormaps
import pandas as pd
import matplotlib.gridspec as gridspec
import math
import firewxpy.settings as settings
import firewxpy.standard as standard


from matplotlib.patheffects import withStroke
from metpy.plots import USCOUNTIES
from datetime import datetime, timedelta
from metpy.plots import colortables
from dateutil import tz
from firewxpy.calc import scaling, Thermodynamics, unit_conversion
from firewxpy.utilities import file_functions

mpl.rcParams['font.weight'] = 'bold'

def plot_relative_humidity(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', show_sample_points=True, sample_point_fontsize=8, alpha=0.5, data=None, time=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    if sample_point_fontsize != 8:
        sp_font_default = False
        sp_fontsize = sample_point_fontsize
    else:
        sp_font_default = True

    contourf = np.arange(0, 101, 1)
    if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
        contours = [0, 10, 20, 30, 40, 60, 80, 100]
        linewidths = 1
        clabel_fontsize = 12
    else:
        contours = np.arange(0, 110, 10)
        linewidths = 0.5

    labels = contourf[::4]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

        if state == 'CA' or state == 'ca':
            title_fontsize = title_fontsize + 2 
            subplot_title_fontsize = subplot_title_fontsize + 2
            

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    
    local_time, utc_time = standard.plot_creation_time()

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.relative_humidity_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, rtma_time = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_dataset(utc_time)
            temp = ds['tmp2m']
            dwpt = ds['dpt2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = temp - 273.15
            dwpt = dwpt - 273.15
            
            rtma_data = Thermodynamics.relative_humidity_from_temperature_and_dewpoint_celsius(temp, dwpt)
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time

            temp = ds['tmp2m']
            dwpt = ds['dpt2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = temp - 273.15
            dwpt = dwpt - 273.15
            
            rtma_data = Thermodynamics.relative_humidity_from_temperature_and_dewpoint_celsius(temp, dwpt)
            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=4)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    plt.title("RTMA Relative Humidity (%)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Analysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, rtma_data[0, :, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha)

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Relative Humidity (%)", size=colorbar_fontsize, fontweight='bold')

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    plot_lon, plot_lat = np.meshgrid(lon[::decimate], lat[::decimate])

    if sp_font_default == False:
        sample_point_fontsize = sp_fontsize
    else:
        sample_point_fontsize = sample_point_fontsize

    if show_sample_points == True:

        stn = mpplots.StationPlot(ax, plot_lon.flatten(), plot_lat.flatten(),
                                     transform=ccrs.PlateCarree(), fontsize=sample_point_fontsize, zorder=7, clip_on=True)
    
        rtma_data = rtma_data[0, ::decimate, ::decimate].to_numpy().flatten()
    
        stn.plot_parameter('C', rtma_data, color='blue', path_effects=[withStroke(linewidth=1, foreground='black')], zorder=7)

    else:
        pass

    path, gif_path = file_functions.check_file_paths(state, gacc_region, 'RTMA RH', reference_system)
    file_functions.update_images(fig, path, gif_path, 'RTMA RH')

def plot_24_hour_relative_humidity_comparison(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', show_sample_points=True, sample_point_fontsize=8, alpha=0.5, data=None, data_24=None, time=None, time_24=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    if sample_point_fontsize != 8:
        sp_font_default = False
        sp_fontsize = sample_point_fontsize
    else:
        sp_font_default = True

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    contourf = np.arange(-50, 51, 1)

    linewidths = 1

    labels = contourf[::4]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    
    local_time, utc_time = standard.plot_creation_time()

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.relative_humidity_change_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, ds_24, rtma_time, rtma_time_24 = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_24_hour_comparison_datasets(utc_time)
            temp = ds['tmp2m']
            dwpt = ds['dpt2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = temp - 273.15
            dwpt = dwpt - 273.15

            temp_24 = ds_24['tmp2m']
            dwpt_24 = ds_24['dpt2m']
            lat_24 = ds_24['lat']
            lon_24 = ds_24['lon']
            temp_24 = temp_24 - 273.15
            dwpt_24 = dwpt_24 - 273.15
            
            rtma_data = Thermodynamics.relative_humidity_from_temperature_and_dewpoint_celsius(temp, dwpt)
            rtma_data_24 = Thermodynamics.relative_humidity_from_temperature_and_dewpoint_celsius(temp_24, dwpt_24)

            diff = rtma_data[0, :, :] - rtma_data_24[0, :, :]
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time
            ds_24 = data_24[0]
            rtma_time_24 = time_24

            temp = ds['tmp2m']
            dwpt = ds['dpt2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = temp - 273.15
            dwpt = dwpt - 273.15

            temp_24 = ds_24['tmp2m']
            dwpt_24 = ds_24['dpt2m']
            lat_24 = ds_24['lat']
            lon_24 = ds_24['lon']
            temp_24 = temp_24 - 273.15
            dwpt_24 = dwpt_24 - 273.15
            
            rtma_data = Thermodynamics.relative_humidity_from_temperature_and_dewpoint_celsius(temp, dwpt)
            rtma_data_24 = Thermodynamics.relative_humidity_from_temperature_and_dewpoint_celsius(temp_24, dwpt_24)

            diff = rtma_data - rtma_data_24

            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)
    
    rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
    rtma_time_24 = rtma_time_24.astimezone(to_zone)
    rtma_time_utc_24 = rtma_time_24.astimezone(from_zone)   

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    plt.title("RTMA 24-Hour Relative Humidity Comparison (Δ%)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Current: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\n[Current - 24HRS]: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_24.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, diff[:, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha, extend='both')

    if sp_font_default == False:
        sample_point_fontsize = sp_fontsize
    else:
        sample_point_fontsize = sample_point_fontsize

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    plot_lon, plot_lat = np.meshgrid(lon[::decimate], lat[::decimate])

    if show_sample_points == True:

        stn = mpplots.StationPlot(ax, plot_lon.flatten(), plot_lat.flatten(),
                                     transform=ccrs.PlateCarree(), fontsize=sample_point_fontsize, zorder=7, clip_on=True)
    
        diff = diff[::decimate, ::decimate].to_numpy().flatten()
    
        stn.plot_parameter('C', diff, color='blue', path_effects=[withStroke(linewidth=1, foreground='black')], zorder=7)

    else:
        pass

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Relative Humidity Trend (Δ%)", size=colorbar_fontsize, fontweight='bold')

    path, gif_path = file_functions.check_file_paths(state, gacc_region, '24HR RTMA RH COMPARISON', reference_system)
    file_functions.update_images(fig, path, gif_path, '24HR RTMA RH COMPARISON')


def plot_temperature(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', show_sample_points=True, sample_point_fontsize=8, alpha=0.5, data=None, time=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    if sample_point_fontsize != 8:
        sp_font_default = False
        sp_fontsize = sample_point_fontsize
    else:
        sp_font_default = True

    local_time, utc_time = standard.plot_creation_time()

    month = utc_time.month

    if month >= 5 and month <= 9:
        contourf = np.arange(30, 111, 1)
    if month == 4 or month == 10:
        contourf = np.arange(10, 91, 1)
    if month >= 11 or month <= 3:
        contourf = np.arange(-10, 71, 1)

    labels = contourf[::4]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

        if state == 'CA' or state == 'ca':
            title_fontsize = title_fontsize + 2 
            subplot_title_fontsize = subplot_title_fontsize + 2

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.temperature_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, rtma_time = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_dataset(utc_time)
            temp = ds['tmp2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = unit_conversion.Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(temp)
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time

            temp = ds['tmp2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = unit_conversion.Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(temp)
            
            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=4)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    plt.title("RTMA Temperature (\N{DEGREE SIGN}F)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Analysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, temp[0, :, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha, extend='both')

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Temperature (\N{DEGREE SIGN}F)", size=colorbar_fontsize, fontweight='bold')

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    plot_lon, plot_lat = np.meshgrid(lon[::decimate], lat[::decimate])

    if sp_font_default == False:
        sample_point_fontsize = sp_fontsize
    else:
        sample_point_fontsize = sample_point_fontsize

    if show_sample_points == True:

        stn = mpplots.StationPlot(ax, plot_lon.flatten(), plot_lat.flatten(),
                                     transform=ccrs.PlateCarree(), fontsize=sample_point_fontsize, zorder=7, clip_on=True)
    
        temp = temp[0, ::decimate, ::decimate].to_numpy().flatten()
    
        stn.plot_parameter('C', temp, color='lime', path_effects=[withStroke(linewidth=1, foreground='black')], zorder=7)

    else:
        pass

    path, gif_path = file_functions.check_file_paths(state, gacc_region, 'RTMA TEMPERATURE', reference_system)
    file_functions.update_images(fig, path, gif_path, 'RTMA TEMPERATURE')

def plot_24_hour_temperature_comparison(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', show_sample_points=True, sample_point_fontsize=8, alpha=0.5, data=None, data_24=None, time=None, time_24=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    if sample_point_fontsize != 8:
        sp_font_default = False
        sp_fontsize = sample_point_fontsize
    else:
        sp_font_default = True

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    contourf = np.arange(-25, 26, 1)

    linewidths = 1

    labels = contourf[::2]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    
    local_time, utc_time = standard.plot_creation_time()

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.temperature_change_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, ds_24, rtma_time, rtma_time_24 = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_24_hour_comparison_datasets(utc_time)
            temp = ds['tmp2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = unit_conversion.Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(temp)

            temp_24 = ds_24['tmp2m']
            lat_24 = ds_24['lat']
            lon_24 = ds_24['lon']
            temp_24 = unit_conversion.Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(temp_24)

            diff = temp[0, :, :] - temp_24[0, :, :]
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time
            ds_24 = data_24[0]
            rtma_time_24 = time_24

            temp = ds['tmp2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = temp - 273.15

            temp_24 = ds_24['tmp2m']
            lat_24 = ds_24['lat']
            lon_24 = ds_24['lon']
            temp_24 = temp_24 - 273.15

            diff = temp[0, :, :] - temp_24[0, :, :]

            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)
    
    rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
    rtma_time_24 = rtma_time_24.astimezone(to_zone)
    rtma_time_utc_24 = rtma_time_24.astimezone(from_zone)   

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    plt.title("RTMA 24-Hour Temperature Comparison (Δ\N{DEGREE SIGN}F)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Current: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\n[Current - 24HRS]: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_24.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, diff[:, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha, extend='both')

    if sp_font_default == False:
        sample_point_fontsize = sp_fontsize
    else:
        sample_point_fontsize = sample_point_fontsize

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    plot_lon, plot_lat = np.meshgrid(lon[::decimate], lat[::decimate])

    if show_sample_points == True:

        stn = mpplots.StationPlot(ax, plot_lon.flatten(), plot_lat.flatten(),
                                     transform=ccrs.PlateCarree(), fontsize=sample_point_fontsize, zorder=7, clip_on=True)
    
        diff = diff[::decimate, ::decimate].to_numpy().flatten()
    
        stn.plot_parameter('C', diff, color='lime', path_effects=[withStroke(linewidth=1, foreground='black')], zorder=7)

    else:
        pass

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Temperature Trend (Δ\N{DEGREE SIGN}F)", size=colorbar_fontsize, fontweight='bold')

    path, gif_path = file_functions.check_file_paths(state, gacc_region, '24HR RTMA TEMPERATURE COMPARISON', reference_system)
    file_functions.update_images(fig, path, gif_path, '24HR RTMA TEMPERATURE COMPARISON')

def plot_dew_point(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', show_sample_points=True, sample_point_fontsize=8, alpha=0.5, data=None, time=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    if sample_point_fontsize != 8:
        sp_font_default = False
        sp_fontsize = sample_point_fontsize
    else:
        sp_font_default = True

    local_time, utc_time = standard.plot_creation_time()

    month = utc_time.month

    if month >= 5 and month <= 9:
        contourf = np.arange(10, 71, 1)
    if month == 4 or month == 10:
        contourf = np.arange(0, 61, 1)
    if month >= 11 or month <= 3:
        contourf = np.arange(-10, 51, 1)

    labels = contourf[::4]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

        if state == 'CA' or state == 'ca':
            title_fontsize = title_fontsize + 2 
            subplot_title_fontsize = subplot_title_fontsize + 2

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.dew_point_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, rtma_time = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_dataset(utc_time)
            temp = ds['dpt2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = unit_conversion.Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(temp)
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time

            temp = ds['dpt2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = unit_conversion.Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(temp)
            
            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=4)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    plt.title("RTMA Dew Point (\N{DEGREE SIGN}F)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Analysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, temp[0, :, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha, extend='both')

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Dew Point (\N{DEGREE SIGN}F)", size=colorbar_fontsize, fontweight='bold')

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    plot_lon, plot_lat = np.meshgrid(lon[::decimate], lat[::decimate])

    if sp_font_default == False:
        sample_point_fontsize = sp_fontsize
    else:
        sample_point_fontsize = sample_point_fontsize

    if show_sample_points == True:

        stn = mpplots.StationPlot(ax, plot_lon.flatten(), plot_lat.flatten(),
                                     transform=ccrs.PlateCarree(), fontsize=sample_point_fontsize, zorder=7, clip_on=True)
    
        temp = temp[0, ::decimate, ::decimate].to_numpy().flatten()
    
        stn.plot_parameter('C', temp, color='darkred', path_effects=[withStroke(linewidth=1, foreground='black')], zorder=7)

    else:
        pass

    path, gif_path = file_functions.check_file_paths(state, gacc_region, 'RTMA DEW POINT', reference_system)
    file_functions.update_images(fig, path, gif_path, 'RTMA DEW POINT')

def plot_24_hour_dew_point_comparison(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', show_sample_points=True, sample_point_fontsize=8, alpha=0.5, data=None, data_24=None, time=None, time_24=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    if sample_point_fontsize != 8:
        sp_font_default = False
        sp_fontsize = sample_point_fontsize
    else:
        sp_font_default = True

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    contourf = np.arange(-25, 26, 1)

    linewidths = 1

    labels = contourf[::2]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    
    local_time, utc_time = standard.plot_creation_time()

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.dew_point_change_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, ds_24, rtma_time, rtma_time_24 = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_24_hour_comparison_datasets(utc_time)
            temp = ds['dpt2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = unit_conversion.Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(temp)

            temp_24 = ds_24['dpt2m']
            lat_24 = ds_24['lat']
            lon_24 = ds_24['lon']
            temp_24 = unit_conversion.Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(temp_24)

            diff = temp[0, :, :] - temp_24[0, :, :]
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time
            ds_24 = data_24[0]
            rtma_time_24 = time_24

            temp = ds['dpt2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = temp - 273.15

            temp_24 = ds_24['dpt2m']
            lat_24 = ds_24['lat']
            lon_24 = ds_24['lon']
            temp_24 = temp_24 - 273.15

            diff = temp[0, :, :] - temp_24[0, :, :]

            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)
    
    rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
    rtma_time_24 = rtma_time_24.astimezone(to_zone)
    rtma_time_utc_24 = rtma_time_24.astimezone(from_zone)   

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    plt.title("RTMA 24-Hour Dew Point Comparison (Δ\N{DEGREE SIGN}F)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Current: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\n[Current - 24HRS]: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_24.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, diff[:, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha, extend='both')

    if sp_font_default == False:
        sample_point_fontsize = sp_fontsize
    else:
        sample_point_fontsize = sample_point_fontsize

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    plot_lon, plot_lat = np.meshgrid(lon[::decimate], lat[::decimate])

    if show_sample_points == True:

        stn = mpplots.StationPlot(ax, plot_lon.flatten(), plot_lat.flatten(),
                                     transform=ccrs.PlateCarree(), fontsize=sample_point_fontsize, zorder=7, clip_on=True)
    
        diff = diff[::decimate, ::decimate].to_numpy().flatten()
    
        stn.plot_parameter('C', diff, color='darkred', path_effects=[withStroke(linewidth=1, foreground='black')], zorder=7)

    else:
        pass

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Dew Point Trend (Δ\N{DEGREE SIGN}F)", size=colorbar_fontsize, fontweight='bold')

    path, gif_path = file_functions.check_file_paths(state, gacc_region, '24HR RTMA DEW POINT COMPARISON', reference_system)
    file_functions.update_images(fig, path, gif_path, '24HR RTMA DEW POINT COMPARISON')

def plot_total_cloud_cover(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', show_sample_points=True, sample_point_fontsize=8, alpha=0.5, data=None, time=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    if sample_point_fontsize != 8:
        sp_font_default = False
        sp_fontsize = sample_point_fontsize
    else:
        sp_font_default = True

    local_time, utc_time = standard.plot_creation_time()

    month = utc_time.month

    contourf = np.arange(0, 101, 1)

    labels = contourf[::4]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

        if state == 'CA' or state == 'ca':
            title_fontsize = title_fontsize + 1 
            subplot_title_fontsize = subplot_title_fontsize + 1

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.cloud_cover_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, rtma_time = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_dataset(utc_time)
            lat = ds['lat']
            lon = ds['lon']
            tcdcclm = ds['tcdcclm']
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time

            tcdcclm = ds['tcdcclm']
            lat = ds['lat']
            lon = ds['lon']
            
            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=4)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    plt.title("RTMA Total Cloud Cover (% Of Sky)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Analysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, tcdcclm[0, :, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha)

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Total Cloud Cover (% Of Sky)", size=colorbar_fontsize, fontweight='bold')

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    plot_lon, plot_lat = np.meshgrid(lon[::decimate], lat[::decimate])

    if sp_font_default == False:
        sample_point_fontsize = sp_fontsize
    else:
        sample_point_fontsize = sample_point_fontsize

    if show_sample_points == True:

        stn = mpplots.StationPlot(ax, plot_lon.flatten(), plot_lat.flatten(),
                                     transform=ccrs.PlateCarree(), fontsize=sample_point_fontsize, zorder=7, clip_on=True)
    
        tcdcclm = tcdcclm[0, ::decimate, ::decimate].to_numpy().flatten()
    
        stn.plot_parameter('C', tcdcclm, color='red', path_effects=[withStroke(linewidth=1, foreground='black')], zorder=7)

    else:
        pass

    path, gif_path = file_functions.check_file_paths(state, gacc_region, 'RTMA TOTAL CLOUD COVER', reference_system)
    file_functions.update_images(fig, path, gif_path, 'RTMA TOTAL CLOUD COVER')

def plot_24_hour_total_cloud_cover_comparison(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', show_sample_points=True, sample_point_fontsize=8, alpha=0.5, data=None, data_24=None, time=None, time_24=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    if sample_point_fontsize != 8:
        sp_font_default = False
        sp_fontsize = sample_point_fontsize
    else:
        sp_font_default = True

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    contourf = np.arange(-60, 61, 1)

    linewidths = 1

    labels = contourf[::5]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

        if state == 'CA' or state == 'ca':
            title_fontsize = title_fontsize - 1 
         #   subplot_title_fontsize = subplot_title_fontsize - 1

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    
    local_time, utc_time = standard.plot_creation_time()

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.cloud_cover_change_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, ds_24, rtma_time, rtma_time_24 = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_24_hour_comparison_datasets(utc_time)
            tcdcclm= ds['tcdcclm']
            lat = ds['lat']
            lon = ds['lon']

            tcdcclm_24 = ds_24['tcdcclm']
            lat_24 = ds_24['lat']
            lon_24 = ds_24['lon']

            diff = tcdcclm[0, :, :] - tcdcclm_24[0, :, :]
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time
            ds_24 = data_24[0]
            rtma_time_24 = time_24

            temp = ds['tmp2m']
            lat = ds['lat']
            lon = ds['lon']
            temp = temp - 273.15

            temp_24 = ds_24['tmp2m']
            lat_24 = ds_24['lat']
            lon_24 = ds_24['lon']
            temp_24 = temp_24 - 273.15

            diff = temp[0, :, :] - temp_24[0, :, :]

            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)
    
    rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
    rtma_time_24 = rtma_time_24.astimezone(to_zone)
    rtma_time_utc_24 = rtma_time_24.astimezone(from_zone)   

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    plt.title("RTMA 24-Hour Total Cloud Cover Comparison (Δ% Of Sky)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Current: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\n[Current - 24HRS]: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_24.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, diff[:, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha, extend='both')

    if sp_font_default == False:
        sample_point_fontsize = sp_fontsize
    else:
        sample_point_fontsize = sample_point_fontsize

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    plot_lon, plot_lat = np.meshgrid(lon[::decimate], lat[::decimate])

    if show_sample_points == True:

        stn = mpplots.StationPlot(ax, plot_lon.flatten(), plot_lat.flatten(),
                                     transform=ccrs.PlateCarree(), fontsize=sample_point_fontsize, zorder=7, clip_on=True)
    
        diff = diff[::decimate, ::decimate].to_numpy().flatten()
    
        stn.plot_parameter('C', diff, color='red', path_effects=[withStroke(linewidth=1, foreground='black')], zorder=7)

    else:
        pass

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Total Cloud Cover Trend (Δ% Of Sky)", size=colorbar_fontsize, fontweight='bold')

    path, gif_path = file_functions.check_file_paths(state, gacc_region, '24HR RTMA TOTAL CLOUD COVER COMPARISON', reference_system)
    file_functions.update_images(fig, path, gif_path, '24HR RTMA TOTAL CLOUD COVER COMPARISON')


def plot_wind_speed(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', show_sample_points=True, sample_point_fontsize=8, alpha=0.5, data=None, time=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    if sample_point_fontsize != 8:
        sp_font_default = False
        sp_fontsize = sample_point_fontsize
    else:
        sp_font_default = True

    local_time, utc_time = standard.plot_creation_time()

    month = utc_time.month

    contourf = np.arange(0, 61, 1)

    labels = contourf[::4]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

        if state == 'CA' or state == 'ca':
            title_fontsize = title_fontsize + 1 
            subplot_title_fontsize = subplot_title_fontsize + 1

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.wind_speed_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, rtma_time = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_dataset(utc_time)
            lat = ds['lat']
            lon = ds['lon']
            ws = ds['wind10m']
            ws = unit_conversion.meters_per_second_to_mph(ws)
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time

            ws = ds['wind10m']
            lat = ds['lat']
            lon = ds['lon']
            ws = unit_conversion.meters_per_second_to_mph(ws)
            
            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=4)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    plt.title("RTMA Wind Speed (MPH)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Analysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, ws[0, :, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha, extend='max')

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Wind Speed (MPH)", size=colorbar_fontsize, fontweight='bold')

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    plot_lon, plot_lat = np.meshgrid(lon[::decimate], lat[::decimate])

    if sp_font_default == False:
        sample_point_fontsize = sp_fontsize
    else:
        sample_point_fontsize = sample_point_fontsize

    if show_sample_points == True:

        stn = mpplots.StationPlot(ax, plot_lon.flatten(), plot_lat.flatten(),
                                     transform=ccrs.PlateCarree(), fontsize=sample_point_fontsize, zorder=7, clip_on=True)
    
        ws = ws[0, ::decimate, ::decimate].to_numpy().flatten()
    
        stn.plot_parameter('C', ws, color='lime', path_effects=[withStroke(linewidth=1, foreground='black')], zorder=7)

    else:
        pass

    path, gif_path = file_functions.check_file_paths(state, gacc_region, 'RTMA WIND SPEED', reference_system)
    file_functions.update_images(fig, path, gif_path, 'RTMA WIND SPEED')

def plot_24_hour_wind_speed_comparison(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', show_sample_points=True, sample_point_fontsize=8, alpha=0.5, data=None, data_24=None, time=None, time_24=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    if sample_point_fontsize != 8:
        sp_font_default = False
        sp_fontsize = sample_point_fontsize
    else:
        sp_font_default = True

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    contourf = np.arange(-20, 21, 1)

    linewidths = 1

    labels = contourf[::2]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

      #  if state == 'CA' or state == 'ca':
       #     title_fontsize = title_fontsize + 1 
        #    subplot_title_fontsize = subplot_title_fontsize + 1

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    
    local_time, utc_time = standard.plot_creation_time()

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.wind_speed_change_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, ds_24, rtma_time, rtma_time_24 = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_24_hour_comparison_datasets(utc_time)
            ws = ds['wind10m']
            lat = ds['lat']
            lon = ds['lon']
            ws = unit_conversion.meters_per_second_to_mph(ws)

            ws_24 = ds_24['wind10m']
            lat_24 = ds_24['lat']
            lon_24 = ds_24['lon']
            ws_24 = unit_conversion.meters_per_second_to_mph(ws_24)

            diff = ws[0, :, :] - ws_24[0, :, :]
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time
            ds_24 = data_24[0]
            rtma_time_24 = time_24

            ws = ds['wind10m']
            lat = ds['lat']
            lon = ds['lon']
            ws = unit_conversion.meters_per_second_to_mph(ws)

            ws_24 = ds_24['wind10m']
            lat_24 = ds_24['lat']
            lon_24 = ds_24['lon']
            ws_24 = unit_conversion.meters_per_second_to_mph(ws_24)

            diff = ws[0, :, :] - ws_24[0, :, :]

            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)
    
    rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
    rtma_time_24 = rtma_time_24.astimezone(to_zone)
    rtma_time_utc_24 = rtma_time_24.astimezone(from_zone)   

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    plt.title("RTMA Wind Speed Comparison (ΔMPH)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Current: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\n[Current - 24HRS]: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_24.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, diff[:, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha, extend='both')

    if sp_font_default == False:
        sample_point_fontsize = sp_fontsize
    else:
        sample_point_fontsize = sample_point_fontsize

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    plot_lon, plot_lat = np.meshgrid(lon[::decimate], lat[::decimate])

    if show_sample_points == True:

        stn = mpplots.StationPlot(ax, plot_lon.flatten(), plot_lat.flatten(),
                                     transform=ccrs.PlateCarree(), fontsize=sample_point_fontsize, zorder=7, clip_on=True)
    
        diff = diff[::decimate, ::decimate].to_numpy().flatten()
    
        stn.plot_parameter('C', diff, color='darkred', path_effects=[withStroke(linewidth=1, foreground='black')], zorder=7)

    else:
        pass

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Wind Speed Difference (ΔMPH)", size=colorbar_fontsize, fontweight='bold')

    path, gif_path = file_functions.check_file_paths(state, gacc_region, '24HR RTMA WIND SPEED COMPARISON', reference_system)
    file_functions.update_images(fig, path, gif_path, '24HR RTMA WIND SPEED COMPARISON')

def plot_wind_speed_and_direction(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', alpha=0.5, data=None, data_24=None, time=None, time_24=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8, barbs_or_quivers='barbs', barb_quiver_alpha=1, minshaft=0.5, headlength=5, headwidth=3, barb_quiver_fontsize=6, barb_linewidth=0.5, quiver_linewidth=0.5):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region

    if barbs_or_quivers == 'barbs' or barbs_or_quivers == 'Barbs' or barbs_or_quivers == 'BARBS' or barbs_or_quivers == 'B' or barbs_or_quivers == 'b':

        barbs = True

    if barbs_or_quivers == 'quivers' or barbs_or_quivers == 'Quivers' or barbs_or_quivers == 'QUIVERS' or barbs_or_quivers == 'Q' or barbs_or_quivers == 'q':

        barbs = False

    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    local_time, utc_time = standard.plot_creation_time()

    month = utc_time.month

    contourf = np.arange(0, 61, 1)

    labels = contourf[::4]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

        if state == 'CA' or state == 'ca':
            title_fontsize = title_fontsize + 1 
            subplot_title_fontsize = subplot_title_fontsize + 1

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.wind_speed_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, rtma_time = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_dataset(utc_time)
            u = ds['ugrd10m']
            v = ds['vgrd10m']
            ws = ds['wind10m']
            lon = ds['lon']
            lat = ds['lat']
            ws = unit_conversion.meters_per_second_to_mph(ws)
            lon_2d, lat_2d = np.meshgrid(lon, lat)
            u = unit_conversion.meters_per_second_to_mph(u)
            v = unit_conversion.meters_per_second_to_mph(v)    
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time

            u = ds['ugrd10m']
            v = ds['vgrd10m']
            ws = ds['wind10m']
            lon = ds['lon']
            lat = ds['lat']
            ws = unit_conversion.meters_per_second_to_mph(ws)
            lon_2d, lat_2d = np.meshgrid(lon, lat)
            u = unit_conversion.meters_per_second_to_mph(u)
            v = unit_conversion.meters_per_second_to_mph(v)         
            
            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=4)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass
    
    if barbs == True:
    
        plt.title("RTMA Wind Speed & Direction Comparison (MPH [Shaded] + Wind Barbs)", fontsize=title_fontsize, fontweight='bold', loc='left')

    if barbs == False:

        plt.title("RTMA Wind Speed & Direction Comparison (MPH [Shaded] + Wind Vectors)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Analysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, ws[0, :, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha, extend='max')

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Wind Speed (MPH)", size=colorbar_fontsize, fontweight='bold')

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    if barbs == True:

        stn = mpplots.StationPlot(ax, lon_2d[::decimate, ::decimate], lat_2d[::decimate, ::decimate],
                         transform=ccrs.PlateCarree(), zorder=9, fontsize=barb_quiver_fontsize, clip_on=True)

        stn.plot_barb(u[0, :, :][::decimate, ::decimate], v[0, :, :][::decimate, ::decimate], color='lime', label=rtma_time.strftime('%m/%d %H:00'), alpha=barb_quiver_alpha, zorder=9, linewidth=barb_linewidth)

        file_name_end = ' WIND BARBS'

    if barbs == False:

        ax.quiver(lon_2d[::decimate, ::decimate], lat_2d[::decimate, ::decimate], u[0, :, :][::decimate, ::decimate], v[0, :, :][::decimate, ::decimate], color='lime', minshaft=minshaft, headlength=headlength, headwidth=headwidth, alpha=barb_quiver_alpha, label=rtma_time.strftime('%m/%d %H:00'), zorder=9, linewidth=quiver_linewidth, transform=ccrs.PlateCarree())

        file_name_end = ' WIND VECTORS'

    fname = 'RTMA WIND SPEED & DIRECTION COMPARISON'+ file_name_end

    path, gif_path = file_functions.check_file_paths(state, gacc_region, fname, reference_system)
    file_functions.update_images(fig, path, gif_path, fname)

def plot_24_hour_wind_speed_and_direction_comparison(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=1, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, reference_system='States & Counties', show_state_borders=False, show_county_borders=False, show_gacc_borders=False, show_psa_borders=False, show_cwa_borders=False, show_nws_firewx_zones=False, show_nws_public_zones=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, cwa_border_linewidth=1, nws_firewx_zones_linewidth=0.5, nws_public_zones_linewidth=0.5, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', cwa_border_linestyle='-', nws_firewx_zones_linestyle='-', nws_public_zones_linestyle='-', psa_color='black', gacc_color='black', cwa_color='black', fwz_color='black', pz_color='black', alpha=0.5, data=None, data_24=None, time=None, time_24=None, state='us', gacc_region=None, colorbar_pad=0.02, clabel_fontsize=8, barbs_or_quivers='barbs', barb_quiver_alpha=1, minshaft=0.5, headlength=5, headwidth=3, barb_quiver_fontsize=6, barb_quiver_fontsize=5, barb_linewidth=0.5, quiver_linewidth=0.5):

    r'''
        This function does the following:
                                        1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                        2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                        3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                        4) Plots the relative humidity data overlayed with the METAR reports. 

        

        Inputs:

            1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

            12) decimate (Integer) - Distance in meters to decimate METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

            13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

            14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

            15) title_font_size (Integer) - The fontsize of the title of the figure. 

            16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

            17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

            18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                       Default setting is 0.05.
                                       Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                       Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

            19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                        will not display on the map. 


        Returns:
                1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
    
    '''
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()
    data = data
    time = time
    state = state
    gacc_region = gacc_region


    if barbs_or_quivers == 'barbs' or barbs_or_quivers == 'Barbs' or barbs_or_quivers == 'BARBS' or barbs_or_quivers == 'B' or barbs_or_quivers == 'b':

        barbs = True

    if barbs_or_quivers == 'quivers' or barbs_or_quivers == 'Quivers' or barbs_or_quivers == 'QUIVERS' or barbs_or_quivers == 'Q' or barbs_or_quivers == 'q':

        barbs = False


    reference_system = reference_system
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    contourf = np.arange(-20, 21, 1)

    linewidths = 1

    labels = contourf[::2]

    if reference_system == 'Custom' or reference_system == 'custom':
        show_state_borders = show_state_borders
        show_county_borders = show_county_borders
        show_gacc_borders = show_gacc_borders
        show_psa_borders = show_psa_borders
        show_cwa_borders = show_cwa_borders
        show_nws_firewx_zones = show_nws_firewx_zones
        show_nws_public_zones = show_nws_public_zones

    if reference_system != 'Custom' and reference_system != 'custom':
        
        show_state_borders = False
        show_county_borders = False
        show_gacc_borders = False
        show_psa_borders = False
        show_cwa_borders = False
        show_nws_firewx_zones = False
        show_nws_public_zones = False

        if reference_system == 'States Only':
            show_state_borders = True
        if reference_system == 'States & Counties':
            show_state_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC Only':
            show_gacc_borders = True
        if reference_system == 'GACC & PSA':
            show_gacc_borders = True
            show_psa_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.25
        if reference_system == 'CWA Only':
            show_cwa_borders = True
        if reference_system == 'NWS CWAs & NWS Public Zones':
            show_cwa_borders = True
            show_nws_public_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_public_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & NWS Fire Weather Zones':
            show_cwa_borders = True
            show_nws_firewx_zones = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                nws_firewx_zones_linewidth=0.25
        if reference_system == 'NWS CWAs & Counties':
            show_cwa_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
        if reference_system == 'GACC & PSA & NWS Fire Weather Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_firewx_zones = True
            nws_firewx_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS Public Zones':
            show_gacc_borders = True
            show_psa_borders = True
            show_nws_public_zones = True
            nws_public_zones_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & NWS CWA':
            show_gacc_borders = True
            show_psa_borders = True
            show_cwa_borders = True
            cwa_border_linewidth=0.25
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                psa_border_linewidth=0.5
        if reference_system == 'GACC & PSA & Counties':
            show_gacc_borders = True
            show_psa_borders = True
            show_county_borders = True
            county_border_linewidth=0.25
        if reference_system == 'GACC & Counties':
            show_gacc_borders = True
            show_county_borders = True
            if state == 'US' or state == 'us' or state == 'USA' or state == 'usa':
                county_border_linewidth=0.25
    
    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_state_data_and_coords(state, 'rtma')

      #  if state == 'CA' or state == 'ca':
       #     title_fontsize = title_fontsize + 1 
        #    subplot_title_fontsize = subplot_title_fontsize + 1

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, legend_fontsize, mapcrs, datacrs, title_x_position, aspect, tick = settings.get_gacc_region_data_and_coords(gacc_region, 'rtma')

        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick


    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None and state == None and gacc_region == None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound
        state = 'Custom'
        mpl.rcParams['xtick.labelsize'] = tick
        mpl.rcParams['ytick.labelsize'] = tick
        aspect=aspect

    
    local_time, utc_time = standard.plot_creation_time()

    PSAs = geometry.import_shapefiles(f"PSA Shapefiles/National_PSA_Current.shp", psa_color, 'psa')
    
    GACC = geometry.import_shapefiles(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", gacc_color, 'gacc')

    CWAs = geometry.import_shapefiles(f"NWS CWA Boundaries/w_05mr24.shp", cwa_color, 'cwa')

    FWZs = geometry.import_shapefiles(f"NWS Fire Weather Zones/fz05mr24.shp", fwz_color, 'fwz')

    PZs = geometry.import_shapefiles(f"NWS Public Zones/z_05mr24.shp", pz_color, 'pz')

    cmap = colormaps.wind_speed_change_colormap()

    try:
        if data == None:
            test = True
    except Exception as a:
        test = False


    if test == True and time == None:
        
        try:
            ds, ds_24, rtma_time, rtma_time_24 = da.NOMADS_OPENDAP_Downloads.RTMA_CONUS.get_RTMA_24_hour_comparison_datasets(utc_time)
            u = ds['ugrd10m']
            v = ds['vgrd10m']
            u_24 = ds_24['ugrd10m']
            v_24 = ds_24['vgrd10m']
            ws = ds['wind10m']
            ws_24 = ds_24['wind10m']
            lon = ds['lon']
            lat = ds['lat']
            lon_24 = ds_24['lon']
            lat_24 = ds_24['lat']
            ws = unit_conversion.meters_per_second_to_mph(ws)
            ws_24 = unit_conversion.meters_per_second_to_mph(ws_24)
            diff = ws[0, :, :] - ws_24[0, :, :]
            lon_2d, lat_2d = np.meshgrid(lon, lat)
            lon_24_2d, lat_24_2d = np.meshgrid(lon_24, lat_24)
            u = unit_conversion.meters_per_second_to_mph(u)
            v = unit_conversion.meters_per_second_to_mph(v)
            u_24 = unit_conversion.meters_per_second_to_mph(u_24)
            v_24 = unit_conversion.meters_per_second_to_mph(v_24)            
                        
            print("Unpacked the data successfully!")
        except Exception as e:
            pass

    elif test == False and time != None:
        try:
            ds = data[0]
            rtma_time = time
            ds_24 = data_24[0]
            rtma_time_24 = time_24

            u = ds['ugrd10m']
            v = ds['vgrd10m']
            u_24 = ds_24['ugrd10m']
            v_24 = ds_24['vgrd10m']
            ws = ds['wind10m']
            ws_24 = ds_24['wind10m']
            lon = ds['lon']
            lat = ds['lat']
            lon_24 = ds_24['lon']
            lat_24 = ds_24['lat']
            ws = unit_conversion.meters_per_second_to_mph(ws)
            ws_24 = unit_conversion.meters_per_second_to_mph(ws_24)
            diff = ws[0, :, :] - ws_24[0, :, :]
            lon_2d, lat_2d = np.meshgrid(lon, lat)
            lon_24_2d, lat_24_2d = np.meshgrid(lon_24, lat_24)
            u = unit_conversion.meters_per_second_to_mph(u)
            v = unit_conversion.meters_per_second_to_mph(v)
            u_24 = unit_conversion.meters_per_second_to_mph(u_24)
            v_24 = unit_conversion.meters_per_second_to_mph(v_24)     

            print("Unpacked the data successfully!")
        except Exception as e:
            pass
        
    else:
        print("Error! Both values either need to have a value of None or have an array of the RTMA Data and RTMA Timestamp.")

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    rtma_time = rtma_time.replace(tzinfo=from_zone)
    rtma_time = rtma_time.astimezone(to_zone)
    rtma_time_utc = rtma_time.astimezone(from_zone)
    
    rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
    rtma_time_24 = rtma_time_24.astimezone(to_zone)
    rtma_time_utc_24 = rtma_time_24.astimezone(from_zone)   

    fig = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig.set_facecolor('aliceblue')

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75, zorder=9)
    ax.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=8)
    ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=4)
    if show_rivers == True:
        ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    else:
        pass

    if show_gacc_borders == True:
        ax.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    if show_cwa_borders == True:
        ax.add_feature(CWAs, linewidth=cwa_border_linewidth, linestyle=cwa_border_linestyle, zorder=5)
    else:
        pass
    if show_nws_firewx_zones == True:
        ax.add_feature(FWZs, linewidth=nws_firewx_zones_linewidth, linestyle=nws_firewx_zones_linestyle, zorder=5)
    else:
        pass
    if show_nws_public_zones == True:
        ax.add_feature(PZs, linewidth=nws_public_zones_linewidth, linestyle=nws_public_zones_linestyle, zorder=5)
    else:
        pass

    if barbs == True:
    
        plt.title("RTMA Wind Speed & Direction Comparison (ΔMPH [Shaded] + Wind Barbs)", fontsize=title_fontsize, fontweight='bold', loc='left')

    if barbs == False:

        plt.title("RTMA Wind Speed & Direction Comparison (ΔMPH [Shaded] + Wind Vectors)", fontsize=title_fontsize, fontweight='bold', loc='left')
    
    plt.title("Current: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\n[Current - 24HRS]: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_24.strftime('%H:00 UTC')+")", fontsize=subplot_title_fontsize, fontweight='bold', loc='right')

    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nReference System: "+reference_system+"\nData Source: NOAA/NCEP/NOMADS\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", transform=ax.transAxes, fontsize=signature_fontsize, fontweight='bold', verticalalignment='top', bbox=props, zorder=10)

    cs = ax.contourf(lon, lat, diff[:, :], 
                     transform=ccrs.PlateCarree(), levels=contourf, cmap=cmap, alpha=alpha, extend='both')

    decimate = scaling.get_nomads_decimation(western_bound, eastern_bound, southern_bound, northern_bound, True)

    if barbs == True:

        stn = mpplots.StationPlot(ax, lon_2d[::decimate, ::decimate], lat_2d[::decimate, ::decimate],
                         transform=ccrs.PlateCarree(), zorder=9, fontsize=barb_quiver_fontsize, clip_on=True)
    
        stn1 = mpplots.StationPlot(ax, lon_24_2d[::decimate, ::decimate], lat_24_2d[::decimate, ::decimate],
                         transform=ccrs.PlateCarree(), zorder=9, fontsize=barb_quiver_fontsize, clip_on=True)

        stn.plot_barb(u[0, :, :][::decimate, ::decimate], v[0, :, :][::decimate, ::decimate], color='green', label=rtma_time.strftime('%m/%d %H:00'), alpha=barb_quiver_alpha, zorder=9, linewidth=barb_linewidth)

        stn1.plot_barb(u_24[0, :, :][::decimate, ::decimate], v_24[0, :, :][::decimate, ::decimate], color='blue', label=rtma_time_24.strftime('%m/%d %H:00'), alpha=barb_quiver_alpha, zorder=9, linewidth=barb_linewidth)

        file_name_end = ' WIND BARBS'

    if barbs == False:

        ax.quiver(lon_2d[::decimate, ::decimate], lat_2d[::decimate, ::decimate], u[0, :, :][::decimate, ::decimate], v[0, :, :][::decimate, ::decimate], color='lime', minshaft=minshaft, headlength=headlength, headwidth=headwidth, alpha=barb_quiver_alpha, label=rtma_time.strftime('%m/%d %H:00'), zorder=9, linewidth=quiver_linewidth, transform=ccrs.PlateCarree())
    
        ax.quiver(lon_24_2d[::decimate, ::decimate], lat_24_2d[::decimate, ::decimate], u_24[0, :, :][::decimate, ::decimate], v_24[0, :, :][::decimate, ::decimate], color='deepskyblue', minshaft=minshaft, headlength=headlength, headwidth=headwidth, alpha=barb_quiver_alpha, label=rtma_time_24.strftime('%m/%d %H:00'), zorder=9, linewidth=quiver_linewidth, transform=ccrs.PlateCarree())

        file_name_end = ' WIND VECTORS'

    cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad, location='bottom', aspect=aspect, ticks=labels)
    cbar.set_label(label="Wind Speed Difference (ΔMPH)", size=colorbar_fontsize, fontweight='bold')
    ax.legend(loc=(1, 0.75))

    fname = '24HR RTMA WIND SPEED & DIRECTION COMPARISON'+ file_name_end
    
    path, gif_path = file_functions.check_file_paths(state, gacc_region, fname, reference_system)
    file_functions.update_images(fig, path, gif_path, fname)
