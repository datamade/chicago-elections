wget https://data.cityofchicago.org/download/sgsc-bb4n/application/zip
unzip dsv15pWE6oiZTEMkQEowJ5f4bmF7zvlR_Qh53s1Ub7A\?filename\=WardPrecincts.zip 
export OGR_WKT_PRECISION=5
ogr2ogr -f "GeoJSON" -lco COORDINATE_PRECISION=5 ward_precincts.geojson WardPrecincts.shp -t_srs EPSG:4269
