import pandas as pd
import geopandas as gpd
import os
from sklearn.cluster import DBSCAN, KMeans
import yaml

with open(r'departamentos_config.yaml') as file:
    departamentos_config = yaml.full_load(file)


departamentos_nombres = departamentos_config.keys()

for departamento_nombre in departamentos_nombres:

    pois = gpd.read_file(os.path.join('data',departamento_nombre,'pois.geojson'))

    X = pois.loc[:,['x','y']].values

    dbscan_lineas = DBSCAN(eps=departamentos_config[departamento_nombre]['eps'],
                           min_samples=departamentos_config[departamento_nombre]['min_samples']).fit(X)

    pois['cluster']=dbscan_lineas.labels_
    
    etiquetas_clusters = pois.cluster.value_counts()[pois.cluster.value_counts().index>-1].index
    etiquetas_por_tamanio = {k:v for k,v in zip(etiquetas_clusters,range(len(etiquetas_clusters)))}
    pois.cluster = pois.cluster.replace(etiquetas_por_tamanio)

    for n in range(1,11):
        kmeans = KMeans(n_clusters=n, random_state=0).fit(X)
        pois['k_'+str(n)] = kmeans.labels_

    pois['municipio'] = departamento_nombre
    
    if not os.path.isdir(os.path.join('clusters',departamento_nombre)):
        os.mkdir(os.path.join('clusters',departamento_nombre))

    pois.to_file(os.path.join('clusters',departamento_nombre))
