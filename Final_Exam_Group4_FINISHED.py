from pyqgis_scripting_ext.core import *
import json

# ------------------------ FOLDERS -----------------------

#outputfolder = r"C:\Users\laura\OneDrive - Scientific Network South Tyrol\Documents\Master\Semester2\3.advanced geomatics\output"
#geopackageFolder = r"C:\Users\laura\OneDrive - Scientific Network South Tyrol\Documents\Master\Semester2\3.advanced geomatics\natural_earth_vector.gpkg\packages\natural_earth_vector.gpkg"
outputfolder = "/Users/rominalavarello/Desktop/EXAM"
geopackageFolder = "/Users/rominalavarello/Downloads/natural_earth_vector.gpkg/packages/natural_earth_vector.gpkg"
jsonpath = outputfolder + '/result.json'

# ------------------------ CLEAN -------------------------

HMap.remove_layers_by_name(["OpenStreetMap","Lakes","ne_50m_admin_0_countries","FavLakes"])


# ---------------- GET DATA FROM WIKIDATA ----------------
# import the http requests library to get stuff from the internet
import requests
# import the url parsing library to urlencode the query
import urllib.parse

if not os.path.isfile(jsonpath):
    # define the query to launch
    endpointUrl = "https://query.wikidata.org/sparql?query=";
    # define the query to launch
    query = """
    SELECT ?item ?itemLabel ?itemDescription ?area ?elev ?image ?coord WHERE {
      ?item (wdt:P31/wdt:P279*) wd:Q23397.
      {?item wdt:P17 wd:Q38} UNION {?item wdt:P17 wd:Q183} UNION {?item wdt:P17 wd:Q142}.
      ?item wdt:P625 ?coord.
      ?item wdt:P2046 ?area.
      ?item wdt:P2044 ?elev
      OPTIONAL {?item wdt:P18 ?image.}
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    """
    # URL encode the query string
    encoded_query = urllib.parse.quote(query)

    # prepare the final url
    url = f"{endpointUrl}{encoded_query}&format=json"

    # run the query online and get the produced result as a dictionary
    r=requests.get(url)
    result = r.json()
    #print(result)

    with open(jsonpath, 'w') as f:
        json.dump(result, f)
    
    with open(jsonpath, 'r') as openfile:
        data = json.load(openfile)
    
else:
    with open(jsonpath, 'r') as openfile:
        data = json.load(openfile)


# -------------------- GET USEFUL DATA --------------------

coordinates = []
names = []
areas = []
elevations = []

for item in data['results']['bindings']:
    if "coord"in item: 
        coord = item['coord']['value']
        coordinates.append(coord)
    if "itemLabel" in item:
        name = item['itemLabel']['value']
        names.append(name)
    if "area" in item:
        area = item['area']['value']
        areas.append(area)
    if "elev" in item:
        elevation = item['elev']['value']
        elevations.append(elevation)

# print(len(coordinates))
# print(len(names))
# print(len(areas))
# print(len(elevations))


# ------- CREATE LAKE GEOMETRIES AND TRANSFORM THEM -------

crsHelper = HCrs()
crsHelper.from_srid(4326) #spetial reference system ID
crsHelper.to_srid(3857) 

newcoords = []
for coord in coordinates:
    pointGeom = HGeometry.fromWkt(coord)
    newcoord = crsHelper.transform(pointGeom)
    newcoords.append(newcoord)


# --------------------- CREATE LAYER -----------------------

fields = {
    "Name": "String",
    "Area": "Float",
    "Elevation": "Float",
}

LakesLayer = HVectorLayer.new("Lakes", "Point", "EPSG:3857", fields)

saved_names = []
for i, (coord, name, area, elevation) in enumerate(zip(newcoords, names, areas, elevations)):
    if name not in saved_names:
        LakesLayer.add_feature(newcoords[i],[names[i],areas[i],elevations[i]])
        saved_names.append(name)

print(len(saved_names))


# --------------- DUMP TO GEOPACKAGE -----------------------

path = outputfolder + "/Lakes.gpkg"
error = LakesLayer.dump_to_gpkg(path, overwrite=True)
if(error):
    print(error)

# -------------------- COUNTRY BORDERS ---------------------


countriesName = "ne_50m_admin_0_countries"
countriesLayer = HVectorLayer.open(geopackageFolder, countriesName)
countriesLayer.subset_filter("NAME='Italy' OR NAME='Germany' OR NAME='France'")

# COUNTRY coords:
countryit = "Italy"
countryde = "Germany"
countryfr = "France"


nameIndex = countriesLayer.field_index("NAME")
countriesFeatures = countriesLayer.features()

for feature in countriesFeatures:
    name = feature.attributes[nameIndex]
    if name == "Italy":
        for country in countryit:
            countryGeom = feature.geometry # get the geometry 
            crsHelper = HCrs()
            crsHelper.from_srid(4326) 
            crsHelper.to_srid(3857)
            Italy = crsHelper.transform(countryGeom)
    elif name == "Germany":
        for country in countryde:
            countryGeom = feature.geometry # get the geometry 
            crsHelper = HCrs()
            crsHelper.from_srid(4326) 
            crsHelper.to_srid(3857)
            Germany = crsHelper.transform(countryGeom)
    elif name == "France":
        for country in countryfr:
            countryGeom = feature.geometry # get the geometry 
            crsHelper = HCrs()
            crsHelper.from_srid(4326) 
            crsHelper.to_srid(3857)
            France = crsHelper.transform(countryGeom)

union1 = Germany.union(Italy)
# union = union1.union(France)
buffer = union1.buffer(200000)

# ----------------------- STYLING --------------------------

# LAKES

ranges = [
    [float('-inf'),10],
    [11,100],
    [101,1000],
    [1001,float('inf')]
]

styles = [
    HMarker("circle",1) + HFill("skyblue") + HStroke("skyblue",0.5),
    HMarker("circle",1) + HFill("cornflowerblue") + HStroke("cornflowerblue",0.5),
    HMarker("circle",1) + HFill("blue") + HStroke("blue",0.5),
    HMarker("circle",1) + HFill("black") + HStroke("black",0.5),
]

#labelstlye = HLabel("name") + HHalo("white",1)
#LakesLayer.set_graduated_style('Area', ranges, styles, labelstyle)
LakesLayer.set_graduated_style('Area', ranges, styles)


#---
name_liste = [ "Lake Garda", "Kalterer See", "Völser Weiher","Lake Constance", "Langener Waldsee","Lake Como", "Lake Trasimeno","Lac Blanc", "Lac du Bourget", "Lake of Sainte-Croix","Lac de Cap-de-Long"]
liste = [item for item in zip(newcoords, names, areas, elevations) if item[1] in name_liste]

fields = {
    "Name": "String",
    "Area": "Float",
    "Elevation": "Float",
}

FavLakesLayer = HVectorLayer.new("FavLakes", "Point", "EPSG:3857", fields)

saved_names = []
for coord, name, area, elevation in liste:
    if name not in saved_names:
        FavLakesLayer.add_feature(coord, [name, area, elevation])
        saved_names.append(name)

nameProperties = {
    "font": "Arial",
    "color": "black",
    "size": 10,
    "field": 'name',
    "xoffset": 2,
    "yoffset": 6,
}

namestyle = HLabel(**nameProperties) + HHalo("white", 1)

FavLakesLayer.set_style(namestyle)
#---


# COUNTRIES 

style = HFill('rgba(0,0,0,0)') + HStroke('black',0.5)
countriesLayer.set_style(style)

# ----------------------- MAP SHOW -------------------------

osm = HMap.get_osm_layer()
HMap.add_layer(FavLakesLayer)
HMap.add_layer(osm)
HMap.add_layer(countriesLayer)
HMap.add_layer(LakesLayer)

# -------------------- LAYOUT AS PDF ---------------------

printer=HPrinter(iface)
mapProperties ={
        "x":5,
        "y":25,
        "width": 285,
        "height":180,
        "frame": True,
        "extent": buffer.bbox()
    }
printer.add_map(**mapProperties)
    
legendProperties={
       "x":218,
        "y":30,
        "width": 150,
        "height":100,
       "frame":True 
    }
printer.add_legend(**legendProperties)
    
labelProperties={
        "x":105,
        "y":8,
        "text":"LAKES in Germany, Italy and France",
        "bold":True,
        "font_size":20
    }
printer.add_label(**labelProperties)

subtitleProperties={
        "x":97,
        "y":17,
        "text":"by: Miriam Färber, Romina Lavarello, Luisa Menestrina, Laura Morass",
        "bold":False,
        "italic":True,
        "font_size":10
    }
printer.add_label(**subtitleProperties)

scalebarProperties = {
    'x': 10,
    'y': 190,
    'units': "km",
    'segments': 4,
    'style': "Single Box",
}
printer.add_scalebar(**scalebarProperties)
    

imageName= f"LakesMapLayout.png"
imagePath = f"{outputfolder}/{imageName}"
pdfName= f"LakesMapLayout.pdf"
pdfPath = f"{outputfolder}/{pdfName}"
    
printer.dump_to_image(imagePath)
printer.dump_to_pdf(pdfPath)


# -------------------- PRINTING OUTPUTS --------------------

saved_names = []
lakesabove2000 =[]
lakes500_1000 = []
all_others =[]

for i, (coord, name, area, elevation) in enumerate(zip(newcoords, names, areas, elevations)):
    if name not in saved_names:
        saved_names.append(name)
        
        if float(elevation) > 2000:
            lakesabove2000.append(name)
        elif float(elevation) > 500 and float(elevation) < 1000:
            lakes500_1000.append(name)
        else:
            all_others.append(name)

print(len(saved_names))
print("Lakes above 2000 masl:")
print(len(lakesabove2000))

print("Lakes between 500 and 1000 masl:")
print(len(lakes500_1000))

print("Other lakes:")
print(len(all_others))


