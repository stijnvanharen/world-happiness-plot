#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import geopandas as gpd
import math
import json

from bokeh.io import output_notebook, show, output_file, curdoc
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, NumeralTickFormatter, Select
from bokeh.palettes import brewer
from bokeh.layouts import widgetbox, row, column

hap_df = pd.read_pickle('hap_df.pkl')
gdf = gpd.read_file("countries.geo.json")[['admin', 'adm0_a3', 'geometry']]
gdf = gdf.drop(gdf.index[159])
gdf.columns = ['country', 'country_code', 'geometry']

# This dictionary contains the formatting for the data in the plots
format_data = [('ladder', 1, 156, '0', 'World Happiness Report ranking', 'Greens', 9),
               ('average_wine_rating', 83, 92, '90,0', 'Average rating of wine', 'Reds', 9),
               ('spirit_servings', 0, 380, '0', 'Total servings of spirit per year', 'GnBu', 9),
               ('wine_servings', 0, 380, '0', 'Total servings of wine per year', 'Reds', 9),
               ('total_litres_of_pure_alcohol', 0, 15, '0,0', 'Total liters of alcohol per year', 'RdPu', 9),
               ('rest_top_50_count', 0, 7, '0', 'Number of restaurants in top 50', 'Greens', 9),
               ('data_scientist_av_salary', 17000, 300000, '$100,000', 
                'Average yearly data scientist salary', 'Oranges', 9),
               ('data_engineer_av_salary', 9000, 185000, '$100,000', 'Average yearly data engineer salary', 'Purples', 9),
               ('count_nob', 1, 276, '0', 'Number of Nobel prizes', 'BuGn', 9),
               ('count_sat', 1, 181, '0', 'Number of active satellites', 'YlOrRd', 9)              
              ]
 
#Create a DataFrame object from the dictionary 
format_df = pd.DataFrame(format_data, columns = ['field' , 'min_range', 'max_range', 'format', 
                                                 'verbage', 'colors', 'color_no'])

#Create merged DataFrame from geodata and hap_df
merged = gdf.merge(hap_df, on = 'country_code', how = 'left')
merged.replace({None : 'No data'},inplace=True)

#Read data to json.
merged_json = json.loads(merged.to_json())

#Convert to String like object.
json_data = json.dumps(merged_json)

# Define the callback function: update_plot
def update_plot(attr, old, new):
    
    # The input cr is the criteria selected from the select box
    cr = select.value
    input_field = format_df.loc[format_df['verbage'] == cr, 'field'].iloc[0]
    
    # Update the plot based on the changed inputs
    p = make_plot(input_field)
    
    # Update the layout, clear the old document and display the new document
    layout = column(widgetbox(select), p)
    curdoc().clear()
    curdoc().add_root(layout)
    
# Create a plotting function
def make_plot(field_name):    
    # Set the format of the colorbar
    min_range = format_df.loc[format_df['field'] == field_name, 'min_range'].iloc[0]
    max_range = format_df.loc[format_df['field'] == field_name, 'max_range'].iloc[0]
    field_format = format_df.loc[format_df['field'] == field_name, 'format'].iloc[0]

    # Define a sequential multi-hue color palette.
    # Update the color palette
    
    color = format_df.loc[format_df['field'] == field_name, 'colors'].iloc[0]
    shades = format_df.loc[format_df['field'] == field_name, 'color_no'].iloc[0]
    
    colors = brewer[color][shades]
    
    palette = colors
    
    # Reverse color order so that dark blue is highest obesity.
    palette = palette[::-1]
    
    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette = palette, low = min_range, high = max_range)

    # Create color bar.
    format_tick = NumeralTickFormatter(format=field_format)
    color_bar = ColorBar(color_mapper=color_mapper, width = 500, label_standoff=10, formatter=format_tick,
    border_line_color=None, location = (0, 0), orientation = 'horizontal')

    # Create figure object.
    verbage = format_df.loc[format_df['field'] == field_name, 'verbage'].iloc[0]
    
    TOOLTIPS = [('Country','@country_x'),(str(verbage), '@'+str(field_name)+'{'+str(field_format)+'}')]

    p = figure(title = None, plot_height = 550, plot_width = 1100, tooltips=TOOLTIPS)
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False

    # Add patch renderer to figure.
    p.patches('xs','ys', source = geosource, fill_color = {'field' : field_name, 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
  
    # Specify color bar layout.
    p.add_layout(color_bar, 'below')
    
    return p

# Input geojson source that contains features for plotting for:
# initial year 2018 and initial criteria sale_price_median
geosource = GeoJSONDataSource(geojson = json_data)
input_field = 'ladder'

# Call the plotting function
p = make_plot(input_field)

# Make a selection object: select
select = Select(title='Select category:', value='World Happiness Report ranking', 
                options=['World Happiness Report ranking',
                         'Average rating of wine',
                         'Total servings of spirit per year',
                         'Total servings of wine per year',
                         'Total liters of alcohol per year',
                         'Number of restaurants in top 50',
                         'Average yearly data scientist salary',
                         'Average yearly data engineer salary',
                         'Number of Nobel prizes',
                         'Number of active satellites'
                        ])
select.on_change('value', update_plot)

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
# Display the current document
layout = column(widgetbox(select), p)
curdoc().add_root(layout)


# In[ ]:




