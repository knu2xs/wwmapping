from arcgis.gis import GIS

url = 'https://jdm1cc.maps.arcgis.com'
username = 'joel_mccune'
password = 'K3mosabe'

gis = GIS(url, username, password)

print(gis._con._token)