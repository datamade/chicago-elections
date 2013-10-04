wget https://data.cityofchicago.org/download/sgsc-bb4n/application/zip
unzip dsv15pWE6oiZTEMkQEowJ5f4bmF7zvlR_Qh53s1Ub7A\?filename\=WardPrecincts.zip 
ogr2ogr -f "GeoJSON" ward_precints.json WardPrecincts.shp -t_srs EPSG:4269
