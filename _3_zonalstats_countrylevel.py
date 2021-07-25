#########################################################################################
#########################################################################################
#Basado en: https://github.com/sebastianhohmann/gis_course/tree/master/QGIS/research_course
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
print('preliminary setup')
#importamos los módulos generales necesarios:
import sys
#sys proporciona funciones y variables que se utilizan para manipular diferentes partes del entorno de ejecución de Python. Nos permite acceder a parámetros y funciones específicos del sistema. source: https://uniwebsidad.com/libros/python/capitulo-10/modulos-de-sistema
import os
#os proporciona un contenedor para módulos específicos de la plataforma, tales como posix, nt y mac. La interfaz de programación para las funciones disponibles en todas las plataformas debe ser la misma, por lo que usar el módulo os ofrece cierta medida de portabilidad. El módulo consta principalmente de funciones para crear y administrar procesos en ejecución o contenido del sistema de archivos (archivos y directorios). source:https://rico-schmidt.name/pymotw-3/os/index.html 
import qgis
#Importamos el módulo qgis.core y configuramos la "prefix path" (la ubicación donde está instalado QGIS en el sistema). source: https://docs.qgis.org/3.4/en/docs/pyqgis_developer_cookbook/intro.html
#Se configura en el script llamando al método setPrefixPath. 
#El segundo argumento de setPrefixPath se establece en True, especificando que se utilizarán las rutas predeterminadas.
#El path de instalación de QGIS varía según la plataforma; la forma más fácil de encontrarlo para su sistema es usar el Scripting en la Consola Python desde dentro de QGIS y mirar el resultado de ejecutar QgsApplication.prefixPath ().
#Una vez configurada la "prefix path", guardamos una referencia a QgsApplication en la variable qgs. 
#El segundo argumento se establece en False, especificando que no planeamos usar la GUI ya que estamos escribiendo un script independiente. 
#Con QgsApplication configurado, cargamos los proveedores de datos de QGIS y el registro de capas llamando al método qgs.initQgis (). Con QGIS inicializado, estamos listos para escribir el resto del script.
from qgis.core import (
    QgsApplication, 
    QgsCoordinateReferenceSystem,
)
#Llamamos al módulo analysys e importamos los módulos de processing. (source: https://remot-technologies.com/processing-pyqgis-en-vs-code/)
from qgis.analysis import QgsNativeAlgorithms

QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Agregamos el path del "Processing framework"
sys.path.append('C:/OSGeo4W64/apps/qgis/python/plugins')

# Importamos e iniciamos Processing framework
#Para poder acceder a todas las opciones, debemos iniciar las herramientas y añadir los algoritmos de procesamiento al registro accediendo a QgsApplication(), subclase de QApplication().
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#Luego de añadir los algoritmos de procesamiento a la aplicación, ya tenemos todo listo para acceder a nuestro geoprocesos desde nuestra IDE, sin necesidad de entrar en QGIS. (https://remot-technologies.com/processing-pyqgis-en-vs-code/)

# set paths to inputs and outputs
mainpath = "/Users/federica/Documents/MAESTRÍA/2trimestre/herramientas computacionales/clase 5/input"
outpath = "{}/_output".format(mainpath)

elevation = "D:/backup_school/Research/IPUMS/_GEO/elrug/elevation/alt.bil"
tpbasepath = "D:/backup_school/Research/worldclim/World"
tpath = tpbasepath + "/temperature"
ppath = tpbasepath + "/precipitation"
temp = tpath + "/TOTtmean6090.tif"
prec = ppath + "/TOTprec6090.tif"
landqual = outpath + "/landquality.tif"
popd1500 = mainpath + "/HYDE/1500ad_pop/popd_1500AD.asc"
popd1990 = mainpath + "/HYDE/1990ad_pop/popd_1990AD.asc"
popd2000 = mainpath + "/HYDE/2000ad_pop/popd_2000AD.asc"
countries = mainpath + "/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"

outcsv = "{}/country_level_zs.csv".format(outpath)
#Agregamos rasters de elevación, land quality y población:
RASTS = [elevation, temp, prec, landqual, popd1500, popd1990, popd2000]
PREFS = ['elev_', 'temp_', 'prec_', 'lqua_', 'pd15_', 'pd19_', 'pd20_']

# elevation, temperature, precipitation are very large raster files,
# take a long time to process. we will see faster processing methods at the end. 
# the code will still run (if you are patient)!
# for now, do only the last four rasters
RASTS = RASTS[3:]
PREFS = PREFS[3:]

##################################################################
# Fix geometries
##################################################################
#En primer lugar, arreglamos las geometrías para procesar el shapefile, dado que los polígonos se encuentran encimados. 
#El algortimo "fix geometries" intenta crear una representación válida de una geometría no válida dada sin perder ninguno de los vértices de entrada. Las geometrías ya válidas se devuelven sin más intervención. Siempre genera una capa de geometría múltiple.(https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectorgeometry.html#fix-geometries)
print('fixing geometries')
fixgeo_dict = {
    'INPUT': countries,#establece el vector de la capa de entrada a utilizar
    'OUTPUT': 'memory:'#especifica el vector de la capa de salida
}
#ejecutamos el algoritmo usando run()
fix_geo = processing.run('native:fixgeometries', fixgeo_dict)['OUTPUT']

##################################################################
# Drop field(s)
##################################################################
# Descartamos las columnas que no utilizaremos: featurecla;scalerank;LABELRANK;SOVEREIGNT;SOV_A3;ADM0_DIF;LEVEL;TYPE;ADM0_A3;GEOU_DIF;GEOUNIT;GU_A3;SU_DIF;SUBUNIT;SU_A3;BRK_DIFF;NAME;NAME_LONG;BRK_A3;BRK_NAME;BRK_GROUP;ABBREV;POSTAL;FORMAL_EN;FORMAL_FR;NAME_CIAWF;NOTE_ADM0;NOTE_BRK;NAME_SORT;NAME_ALT;MAPCOLOR7;MAPCOLOR8;APCOLOR9;MAPCOLOR13;POP_EST;POP_RANK;GDP_MD_EST;POP_YEAR;LASTCENSUS;GDP_YEAR;ECONOMY;INCOME_GRP;WIKIPEDIA;FIPS_10_;ISO_A2;ISO_A3_EH;ISO_N3;UN_A3;WB_A2;WB_A3;WOE_ID;WOE_ID_EH;WOE_NOTE;ADM0_A3_IS;ADM0_A3_US;ADM0_A3_UN;ADM0_A3_WB;CONTINENT;REGION_UN;SUBREGION;REGION_WB;NAME_LEN;LONG_LEN;ABBREV_LEN;TINY;HOMEPART;MIN_ZOOM;MIN_LABEL;MAX_LABEL;NE_ID;WIKIDATAID;NAME_AR;NAME_BN;NAME_DE;NAME_EN;NAME_ES;NAME_FR;NAME_EL;NAME_HI;NAME_HU;NAME_ID;NAME_IT;NAME_JA;NAME_KO;NAME_NL;NAME_PL;NAME_PT;NAME_RU;NAME_SV;NAME_TR;NAME_VI;NAME_ZH;MAPCOLOR9
print('dropping unnecessary fields')
# Obtenemos todos los fields de atributos
allfields = [field.name() for field in fix_geo.fields()]
keepfields = ['ADMIN', 'ISO_A3'] #establecemos los campos que queremos conservar bajo el nombre "keepfields"
dropfields = [field for field in allfields if field not in keepfields] #especificamos los campos que queremos eliminar como todos los campos que no pertenezcan al grupo "keepfields"

drop_dict = {
    'COLUMN': dropfields, #fields a eliminar
    'INPUT': fix_geo, #vector de la capa de input de la cual borrar los fields
    'OUTPUT': 'memory:' #Especifica el vector que contendrá los fields restantes
}
#ejecutamos el algoritmo usando run()
drop_fields = processing.run('qgis:deletecolumn', drop_dict)['OUTPUT']

# Hacemos un lopp sobre los rasters

for idx, rast in enumerate(RASTS):

	pref = PREFS[idx]

	# not needed, can use rast directly as 'INPUT_RASTER' for zs
	# rlayer = QgsRasterLayer(rast, "rasterlayer", "gdal")

	###################################################################
	# Zonal statistics
	###################################################################
	#Esta función permite realizar cálculos sobre la base de los valores de píxeles de ráster existentes. Los resultados se escriben en una nueva capa ráster con un formato compatible con GDAL. (source: https://docs.qgis.org/2.14/en/docs/user_manual/working_with_raster/raster_analysis.html)
    print('computing zonal stats {}'.format(pref))
	zs_dict = {
	    'COLUMN_PREFIX': pref,#Prefijo para los nombres de las columnas de salida.
	    'INPUT_RASTER': rast,#capa raster que se usa de input
	    'INPUT_VECTOR': drop_fields,#vector de la capa que utiliza como input
	    'RASTER_BAND': 1,#Si el ráster es multibanda, se elige una banda para las estadísticas.
	    'STATS': [2] #Lista de operador estadístico para la salida. Opciones: 2 - Media
	}
    #ejecutamos el algoritmo usando run()
	processing.run('qgis:zonalstatistics', zs_dict)


###################################################################
# write to CSV
###################################################################
print('outputting the data')
#Exportamos los datos a un archivo .csv
with open(outcsv, 'w') as output_file: #seleccionamos el path de salida donde se va a crear el archivo con el nuevo contenido
    fieldnames = [field.name() for field in drop_fields.fields()] #obtiene fields con ese nombre
    line = ','.join(name for name in fieldnames) + '\n'
    output_file.write(line)
    for f in drop_fields.getFeatures():
        line = ','.join(str(f[name]) for name in fieldnames) + '\n' #método string que devuelve a los elementos de la secuencia como string unidos por un separador str.
        output_file.write(line) #cada elemento se escribe en el archivo de output
      
print('DONE!')
