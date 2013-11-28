from vincent import *
import json
import pandas as pd
#Map the county codes we have in our geometry to those in the
#county_data file, which contains additional rows we don't need
state_topo= "us_states.topo.json"
or_topo = "or_counties.topo.json"



#Oregon County-level population data
or_data = pd.read_table('data/OR_County_Data.txt', delim_whitespace=True)
or_data['July_2012_Pop']= or_data['July_2012_Pop'].astype(int)
#Standardize keys
with open('or_counties.topo.json', 'r') as f:
    counties = json.load(f)

def split_county(name):
    parts = name.split(' ')
    parts.pop(-1)
    return ''.join(parts).upper()

#A little FIPS code munging
new_geoms = []
for geom in counties['objects']['or_counties.geo']['geometries']:
    geom['properties']['COUNTY'] = split_county(geom['properties']['COUNTY'])
    new_geoms.append(geom)

counties['objects']['or_counties.geo']['geometries'] = new_geoms

with open('or_counties.topo.json', 'w') as f:
    json.dump(counties, f)

geo_data = [{'name': 'states',
             'url': state_topo,
             'feature': 'us_states.geo'},
            {'name': 'or_counties',
             'url': or_topo,
             'feature': 'or_counties.geo'}]

vis = Map(data=or_data, geo_data=geo_data, scale=1700,
                  translate=[48, 73.94], projection='albersUsa',
                  data_bind='July_2012_Pop', data_key='NAME',
                  map_key={'or_counties': 'properties.COUNTY'})
vis.marks[0].properties.update.fill.value = '#c2c2c2'
vis.to_json('vega.json')

