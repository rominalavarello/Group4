# ----------------- COVID CASES ------------------

from pyqgis_scripting_ext.core import *

# ----------------- FOLDERS ----------------------

folder = "/Users/rominalavarello/Downloads"
# folder = r"C:\Users\laura\OneDrive - Scientific Network South Tyrol\Documents\Master\Semester2\3.advanced geomatics"
# folder = "C:/Users/Michele/OneDrive - Scientific Network South Tyrol/EMMA/Year 1/Advanced geomatics"
#folder = r"C:\Users\miria\OneDrive - Scientific Network South Tyrol\Semester 2\Advanced Geomatics"

gpkgPATH = folder + "/natural_earth_vector.gpkg/packages/natural_earth_vector.gpkg"

data = "/Users/rominalavarello/Desktop/Group4"
# data = r"C:\Users\laura\OneDrive - Scientific Network South Tyrol\Documents\Master\Semester2\3.advanced geomatics\Group4"
# data = r"C:\Users\miria\OneDrive - Scientific Network South Tyrol\Semester 2\Advanced Geomatics\Group4"
# data = r""C:\Users\Michele\OneDrive - Scientific Network South Tyrol\EMMA\Year 1\Advanced geomatics\Group4""

covidPATH = data + "/Covid_data/dpc-covid19-ita-regioni.csv"

# -----------------------------------------------
with open(covidPATH,'r') as file:
    lines = file.readlines()
    print(lines[:20])
    
    
    
    