# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 14:53:42 2021

@author:SharadShingade
"""

from osgeo import gdal, osr
import os
import geopandas as gpd
from shapely.geometry import Point,Polygon,mapping
from fiona.crs import from_epsg  
from osgeo import gdal, ogr, osr
import pandas as pd
import glob, ntpath,shutil
import fiona; fiona.supported_drivers
import shapefile
##


localsws = r"I:\ML_DL\data"

merge_locals = r"I:\ML_DL\out_ws"
timeframe = 'T0'# "T1_T3"

timef = ['T0','T1_T3']
for t in timef:
    print t


dataf = [f for f in os.listdir(r"%s" % (localsws))]

for city in dataf:
    print city 
    newdata_master = gpd.GeoDataFrame()
    newdata_master['geometry']=None

    newdata_master_index = 0
    
    timef = ['T0','T1_T3']
    for t in timef:
        print t
        for xx in glob.glob(r"%s\%s\%s_Blocks\%s_%s\*0.shp" % (localsws,city,city,city,t)):
            print xx
            locale_id = ntpath.basename(xx)[:-5]
            print locale_id
            gdf = gpd.read_file(xx) #LINESTRING
            geom = [x for x in gdf.geometry]
            all_coords = mapping(geom[0])['coordinates']
            lats = [x[1] for x in all_coords]
            lons = [x[0] for x in all_coords]
            polyg = Polygon(zip(lons, lats))
            
            ## 
            lat =  gdf.centroid.y
            lon =  gdf.centroid.x
            
            newdata_master.loc[newdata_master_index,'geometry']=polyg
                
            newdata_master.loc[newdata_master_index,'ID_string']=str(locale_id)
            newdata_master.loc[newdata_master_index,'lat']=lat[0]
            newdata_master.loc[newdata_master_index,'long']=lon[0]
            newdata_master.loc[newdata_master_index,'Locale_No']=int(newdata_master_index)
            newdata_master.loc[newdata_master_index,'Exp_Area']=t
            
            
            
                
            newdata_master_index= newdata_master_index+1

    newdata_master.crs = from_epsg(4326)

    outchip_shp_merge = r"%s/%s" % (merge_locals,city)
    if not os.path.exists(outchip_shp_merge):
        os.makedirs(outchip_shp_merge)
    merge_shape_name = r"%s/%s_Locales_Polygons.shp" %(outchip_shp_merge,city)
    newdata_master.to_file(merge_shape_name)

## blocks
for city in dataf:
    print city 
    newdata_master = gpd.GeoDataFrame()
    newdata_master['geometry']=None

    newdata_master_index = 0
    
    timef = ['T0','T1_T3']
    for t in timef:
        print t
        for xx in glob.glob(r"%s\%s\%s_Blocks\%s_%s\*1.shp" % (localsws,city,city,city,t)):
            print xx
            locale_id = ntpath.basename(xx)[:-5]
            print locale_id
            gdf = gpd.read_file(xx) #LINESTRING
            
            ## 
            #for gdf_obj in gdf:
             #   print gdf_obj
                
            for index, row in gdf.iterrows():
                #print row
                geom = row.geometry 
                #geom = [x for x in gdf.geometry]
                all_coords = mapping(geom)['coordinates']
                lats = [x[1] for x in all_coords]
                lons = [x[0] for x in all_coords]
                polyg = Polygon(zip(lons, lats))
                
                ## 
                #lat =  gdf.centroid.y
                #lon =  gdf.centroid.x
                
                newdata_master.loc[newdata_master_index,'geometry']=polyg
                    
                newdata_master.loc[newdata_master_index,'ID_string']=str(locale_id)
                newdata_master.loc[newdata_master_index,'Land_use']=row['Land_use']
                newdata_master.loc[newdata_master_index,'Exp_Area']=t
                #newdata_master.loc[newdata_master_index,'lat']=lat[0]
                #newdata_master.loc[newdata_master_index,'long']=lon[0]
                #newdata_master.loc[newdata_master_index,'Locale_No']=int(newdata_master_index)
                
                
                
                    
                newdata_master_index= newdata_master_index+1

    newdata_master.crs = from_epsg(4326)

    outchip_shp_merge = r"%s/%s" % (merge_locals,city)
    if not os.path.exists(outchip_shp_merge):
        os.makedirs(outchip_shp_merge)
    merge_shape_name = r"%s/%s_Blocks_Polygons.shp" %(outchip_shp_merge,city)
    newdata_master.to_file(merge_shape_name)    
     
    
# Road file creation
    
locale_gdf = gpd.read_file ( r"%s/%s_Locales_Polygons.shp" %(outchip_shp_merge,city))
blocks_gdf = gpd.read_file (r"%s/%s_Blocks_Polygons.shp" %(outchip_shp_merge,city))
    
erased_gdf = gpd.overlay(locale_gdf, blocks_gdf, how='difference')    
erased_gdf['Land_use'] = '6'

# Save roads
road_shape_name = r"%s/%s_Roads.shp" %(outchip_shp_merge,city)
erased_gdf.to_file(road_shape_name)

# merge block and roadshapefile
complete_gdf = blocks_gdf.append(erased_gdf)
## iterate over Locals polygon

locale_dict = {}
lat_dict = {}
long_dict = {}


for index, row in locale_gdf.iterrows():
                #print row
    #print row
    print index
    #geom = row.geometry 
    #geom = [x for x in gdf.geometry]
    #all_coords = mapping(geom)['coordinates']
    locale_idd = row['ID_string']
    locale_dict[locale_idd] = row['Locale_No']
    lat_dict[locale_idd] = row['lat']
    long_dict[locale_idd] = row['long']
    
   ##
   
## update complete gdf file
complete_gdf_updated = complete_gdf.reset_index(drop=True)

for index,  r in complete_gdf_updated.iterrows():
    locale_id = r['ID_string']
    print locale_id
    complete_gdf_updated.loc[complete_gdf_updated.ID_string == locale_id, "lat"] = lat_dict[locale_id]
    complete_gdf_updated.loc[complete_gdf_updated.ID_string == locale_id, "long"] = long_dict[locale_id]
    complete_gdf_updated.loc[complete_gdf_updated.ID_string == locale_id, "Locale_No"] = locale_dict[locale_id]
    

## Export complete shapefile
Complete_shape_name = r"%s/%s_Complete.shp" %(outchip_shp_merge,city)
complete_gdf_updated.to_file(Complete_shape_name)

# Export complete geojson
# this geojson throwing error: kernel died,restarting
#Complete_geojson_name = r"%s/%s_Complete.geojson" %(outchip_shp_merge,city)
#complete_gdf_updated.to_file(Complete_geojson_name, driver='GeoJSON')


## new code to export geojson

Complete_geojson_name = r"%s/%s_Complete.geojson" %(outchip_shp_merge,city)

reader = shapefile.Reader(Complete_shape_name)
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
buffer = []
for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature", \
    geometry=geom, properties=atr)) 
   
# write the GeoJSON file
from json import dumps
geojson = open(Complete_geojson_name, "w")
geojson.write(dumps({"type": "FeatureCollection",\
"features": buffer}, indent=2) + "\n")
geojson.close()


#end   
