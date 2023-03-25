import altair as alt
import pandas as pd
import folium
from folium.plugins import HeatMap
import numpy as np

MAP_HEIGHT = 500
MAP_WIDTH = 700

################### Draw #####################
def draw_map(data_geo):
    """Draw map
    
    Arguments:
        data_geo {pandas.DataFrame} -- DataFrame of map geojson
    
    Returns:
        altair -- Map visualization generate by altair
    """
    background = alt.Chart(data_geo).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        width=MAP_WIDTH,
        height=MAP_HEIGHT
    )
    # Add Labels Layer
    map_labels = background.mark_text(
        baseline='middle',
        align='center'
    ).encode(
        longitude='properties.cp[0]:Q',
        latitude='properties.cp[1]:Q',
        text='properties.name:O',
        size=alt.value(15),
        opacity=alt.value(1)
    )
    return background + map_labels

def draw_points(data, background):
    """Draw points
    
    Arguments:
        data {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
        background {altair} -- Map visualization generate by altair
    
    Returns:
        altair -- Map visualization generate by altair
    """
    points = alt.Chart(data).mark_circle().encode(
        longitude='lng:Q',
        latitude='lat:Q',
        color=alt.value('steelblue'),
        tooltip=['address:N']
    ).properties(
        title='Location'
    )
    result = background + points
    return result

def draw_cluster(data, centersDf, background):
    """Draw cluster and points
    
    Arguments:
        data {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
        centersDf {pandas.DataFrame} -- DataFrame containing cluster centroid coordinate information, i.e. lat and lng
        background {altair} -- Map visualization generate by altair
    
    Returns:
        altair -- Map visualization generate by altair
    """
    outlier = alt.Chart(data[data['cluster_id'] == -1]).mark_circle().encode(
        longitude='lng:Q',
        latitude='lat:Q',
        color=alt.value('black')
    )

    points = alt.Chart(data[data['cluster_id'] != -1]).mark_circle().encode(
        longitude='lng:Q',
        latitude='lat:Q',
        color=alt.Color('cluster_id:N', scale=alt.Scale(scheme='category20')),
        tooltip=['address:N', 'cluster_id']
    ).properties(
        title='Clustering'
    )
    
    centers = alt.Chart(centersDf).mark_circle().encode(
        longitude='lng:Q',
        latitude='lat:Q',
        color=alt.value('black'),
        size=alt.value(100),
        tooltip=['cluster_id', 'lng', 'lat']
    )
    
    result = background + outlier + points + centers
    return result

def draw_heatmap(geoData):
    # Require chrome browser, doesn't work in Edge
    max_amount = 100.0

    hmap = folium.Map(location=[23, 113], zoom_start=7, )

    hm_wide = HeatMap( list(zip(geoData.lat.values, geoData.lng.values, np.ones(len(geoData)))),
                    min_opacity=0.2,
                    max_val=max_amount,
                    radius=17, blur=15, 
                    max_zoom=1, 
                    )

    # folium.GeoJson(guangDong).add_to(hmap)
    hmap.add_child(hm_wide)
    return hmap
