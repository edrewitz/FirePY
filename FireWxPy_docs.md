# FireWxPy Documentation

**Welcome To FireWxPy**

Thank you for choosing to use FireWxPy in your weather operations and/or research. The purpose of this package is to help fellow meteorologists create realtime data visualizations of weather data with an emphasis on fire weather. The goal of this project is to make creating these graphics with the least amount of work required for the user. These graphics are designed to be part of a script that is being automatically run via either a Cron Job or via the Windows Task Scheduler. These plots display National Weather Service forecast data as well as 2.5km x 2.5km Real Time Mesoscale Analysis data from the UCAR THREDDS server: https://www.unidata.ucar.edu/software/tds/

**The Role of the User**

FireWxPy does at least 95% of the work for the user to create data visualizations of various types of weather analysis and forecast data. However, there is still plenty of customization for the users. 

Here is what the user will still be responsible for:

1. Importing the needed Python modules
2. Choosing the bounds for the plot in latitude/longitude coordinates. 
3. There is a function where the user can customize the title, colorscale, colorbar, figure size and weather parameter of a plot. 
4. There are also plenty of preset plots that the user will be able to call functions from the `FireWxPy_Plots` module.

**Data Access Module**

The `data_access` module hosts functions that retrieve data from the National Weather Service FTP Server and the UCAR THREDDS Server. 









**Parser Module**

The `parser` module hosts functions that parse through the various datasets within the downloaded files and returns organized data arrays to make plotting graphics easier. 








**FireWxPy_Plots Module**

The `FireWxPy_Plots` module hosts a variety of different functions for the user to plot various types of real-time analysis and forecast weather data. 