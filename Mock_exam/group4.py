from pyqgis_scripting_ext.core import *


folder = "/Users/rominalavarello/Downloads"
# folder = r"C:\Users\laura\OneDrive - Scientific Network South Tyrol\Documents\Master\Semester2\3.advanced geomatics"
# folder = "C:/Users/Michele/OneDrive - Scientific Network South Tyrol/EMMA/Year 1/Advanced geomatics"
# folder = r"C:\Users\miria\OneDrive - Scientific Network South Tyrol\Semester 2\Advanced Geomatics"

csvpath = folder + "/test/22yr_T10MN"
gpkgPATH = folder + "/natural_earth_vector.gpkg/packages/natural_earth_vector.gpkg"

with open(csvpath,'r') as file:
    lines = file.readlines()

canvas = HMapCanvas.new()
osm = HMap.get_osm_layer()
canvas.set_layers([osm])

grid = []
temps = []
TempPerCoord = {}

for line in lines[14:]: 
    line = line.strip()
    lineSplit = line.split(" ")
    Lat = float(lineSplit[0])
    Lon = float(lineSplit[1])
    AnnTemp = float(lineSplit[-1])
    
    temps.append(AnnTemp)
    
    # print(Lat, Lon)
    
    coords = [
        [Lon,Lat],
        [Lon,Lat+1],
        [Lon+1,Lat+1],
        [Lon+1,Lat],
        [Lon,Lat]]
    
    rectangle = HPolygon.fromCoords(coords)

    crsHelper = HCrs()
    crsHelper.from_srid(4326) 
    crsHelper.to_srid(3857)

    convertedrec = crsHelper.transform(rectangle)
    
    grid.append(convertedrec)



# GERMANY coords:

countriesName = "ne_50m_admin_0_countries"
countriesLayer = HVectorLayer.open(gpkgPATH, countriesName)

nameIndex = countriesLayer.field_index("NAME")
countriesFeatures = countriesLayer.features()

for feature in countriesFeatures:
    name = feature.attributes[nameIndex]
    if name == 'Germany':
        germanGeom = feature.geometry # get the geometry 
        # print("GEOM:", germanGeom.asWkt()[:100] + "...") 
        crsHelper = HCrs()
        crsHelper.from_srid(4326) 
        crsHelper.to_srid(3857)

        GERMANY = crsHelper.transform(germanGeom)


# print(min(temps))
# print(max(temps))

tempandcolor = {
    -10:'midnightblue',
    -5:'darkblue',
    0:'blue',
    5:'lightblue',
    6:'lightcyan',
    8:'gold',
    9:'yellow',
    15:'orange',
    20:'coral',
    30:'red'}

for rectangle,temp in zip(grid,temps):
    if rectangle.intersects(GERMANY):
        for limit,color in tempandcolor.items():
            
            if temp < limit:
                canvas.add_geometry(rectangle,color,1)
                break

canvas.set_extent([-20037508.34,-20048966.1,20037508.34,20048966.1])
canvas.show()

