import numpy as np
import os
from qgis.core import QgsApplication, QgsVectorLayer, QgsProject

qgs = QgsApplication([], False)
qgs.initQgis()

# Ścieżka do pliku shapefile
layer_path = r"BDOT\kujawsko_pomorskie_m_Torun\fragment_roads.shp"

if not os.path.isfile(layer_path):
    raise FileNotFoundError("Plik nie istnieje!")
else:

    # Wczytanie warstwy
    layer = QgsVectorLayer(layer_path, "fragment_roads", "ogr")

    if not layer.isValid():
        raise FileNotFoundError("Warstwa nie została załadowana!")
    
    # Iteracja po cechach
    for feature in layer.getFeatures():

        geom = feature.geometry()
        
        # Pobranie punktów startowego i końcowego
        if geom.isMultipart():  # multi-linia
            line = geom.asMultiPolyline()[0]  # pierwsza linia w multipart
        else:
            line = geom.asPolyline()

        if line:  # jeśli geometria istnieje
            start_point = line[0]
            end_point = line[-1]
            # Drukowanie FID i punktów
            # QgsPointXY ma x i y
            print(feature.id(),
                  round(geom.length(), 2),
                (round(start_point.x(), 2), round(start_point.y(), 2)),
                (round(end_point.x(), 2), round(end_point.y(), 2)))
        
qgs.exitQgis()