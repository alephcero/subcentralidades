
#%%
import osmnx as ox
import pandas as pd
import geopandas as gpd
import os
import yaml

with open(r'departamentos_config.yaml') as file:
    departamentos_config = yaml.full_load(file)

with open(r'pois_config.yaml') as file:
    pois_config = yaml.full_load(file)

shops_eliminar = pois_config['shops_eliminar']
amenities_eliminar = pois_config['amenities_eliminar']

with open(r'departamentos_config.yaml') as file:
    departamentos_config = yaml.full_load(file)

departamentos_nombres = departamentos_config.keys()


for departamento_nombre in departamentos_nombres:

    departamento_osm = departamentos_config[departamento_nombre]['nombre_osm']    
    query = ox.geometries_from_place(departamento_osm, {'amenity':True, 'shop':True})

    #extraer shops
    shops = query.reset_index()\
        .reindex(columns = ['osmid','shop','geometry'])\
        .dropna(subset=['shop'])\
        .rename(columns = {'shop':'type'})

    #detectar poligono de shoppings
    shoppings = shops.loc[shops['type'].isin(['department_store','mall']),['geometry']].copy()
    shoppings = shoppings.to_crs(epsg=5348)

    #extraer amenities
    amenities = query.reset_index()\
        .reindex(columns = ['osmid','amenity','geometry'])\
        .dropna(subset=['amenity'])\
        .rename(columns = {'amenity':'type'})

    #eliminar las cateogrias no deseadas 
    amenities = amenities.loc[~amenities['type'].isin(amenities_eliminar),:] 
    shops = shops.loc[~shops['type'].isin(shops_eliminar),:] 

    # unificar en pois
    pois = pd.concat([amenities,shops])
    pois = pois.to_crs(epsg=5348)
    pois['geometry'] = pois.geometry.centroid

    # eliminar pois en shoppings
    shoppings_ids = gpd.sjoin(pois,shoppings).osmid
    pois = pois.loc[~pois.osmid.isin(shoppings_ids),:]

    pois['id'] = range(len(pois))
    pois['x'] = pois.geometry.x
    pois['y'] = pois.geometry.y

    # guardar los datos
    if not os.path.isdir(os.path.join('data',departamento_nombre)):
        os.mkdir(os.path.join('data',departamento_nombre))

    if len(pois) > 0:
        pois.to_file('data/'+departamento_nombre+'/pois.geojson',driver='GeoJSON')
    else:
        print('No hay POIs en '+departamento_nombre)

