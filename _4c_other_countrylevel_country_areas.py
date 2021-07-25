#########################################################################################
#########################################################################################
#Basado en: https://github.com/sebastianhohmann/gis_course/tree/master/QGIS/research_course
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
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

#########################################################################################
#########################################################################################

# set paths to inputs and outputs
mainpath = "Users/federica/Documents/MAESTRÍA/2trimestre/herramientas computacionales/clase 5/input"
admin_in = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)
areas_out = "{}/_output/country_areas.csv".format(mainpath)

# defining world cylindrical equal area SR. (#CRS (coordinate reference system) define una proyección de mapa específica, así como las transformaciones entre diferentes sistemas de referencia de coordenadas.)
crs_wcea = QgsCoordinateReferenceSystem('ESRI:54034')

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields')
# Descartamos las variables que no utilizaremos:featurecla;scalerank;LABELRANK;SOVEREIGNT;SOV_A3;ADM0_DIF;LEVEL;TYPE;ADM0_A3;GEOU_DIF;GEOUNIT;GU_A3;SU_DIF;SUBUNIT;SU_A3;BRK_DIFF;NAME;NAME_LONG;BRK_A3;BRK_NAME;BRK_GROUP;ABBREV;POSTAL;FORMAL_EN;FORMAL_FR;NAME_CIAWF;NOTE_ADM0;NOTE_BRK;NAME_SORT;NAME_ALT;MAPCOLOR7;MAPCOLOR8;APCOLOR9;MAPCOLOR13;POP_EST;POP_RANK;GDP_MD_EST;POP_YEAR;LASTCENSUS;GDP_YEAR;ECONOMY;INCOME_GRP;WIKIPEDIA;FIPS_10_;ISO_A2;ISO_A3_EH;ISO_N3;UN_A3;WB_A2;WB_A3;WOE_ID;WOE_ID_EH;WOE_NOTE;ADM0_A3_IS;ADM0_A3_US;ADM0_A3_UN;ADM0_A3_WB;CONTINENT;REGION_UN;SUBREGION;REGION_WB;NAME_LEN;LONG_LEN;ABBREV_LEN;TINY;HOMEPART;MIN_ZOOM;MIN_LABEL;MAX_LABEL;NE_ID;WIKIDATAID;NAME_AR;NAME_BN;NAME_DE;NAME_EN;NAME_ES;NAME_FR;NAME_EL;NAME_HI;NAME_HU;NAME_ID;NAME_IT;NAME_JA;NAME_KO;NAME_NL;NAME_PL;NAME_PT;NAME_RU;NAME_SV;NAME_TR;NAME_VI;NAME_ZH;MAPCOLOR9
# making a layer so we can get all attribute fields
worldlyr = QgsVectorLayer(admin_in, 'ogr')
allfields = [field.name() for field in worldlyr.fields()] #Obtenemos todos los fields de atributos
keepfields = ['ne_10m_adm', 'ADMIN', 'ISO_A3'] #establecemos los campos que queremos conservar bajo el nombre "keepfields"
dropfields = [field for field in allfields if field not in keepfields]#especificamos los campos que queremos eliminar como todos los campos que no pertenezcan al grupo "keepfields"

drop_dict = {
    'COLUMN': dropfields, #fields a eliminar
    'INPUT': admin_in, #vector de la capa de input de la cual borrar los fields
    'OUTPUT': 'memory:'#Especifica el vector que contendrá los fields restantes
}
#ejecutamos el algoritmo usando run()
countries_drop_fields = processing.run('qgis:deletecolumn', drop_dict)['OUTPUT']


##################################################################
# Reproject layer
##################################################################
print('projecting to world cylindical equal area')
#Reproyecta una capa vectorial en un CRS diferente. La capa reproyectada tendrá las mismas características y atributos que la capa de entrada.
reproj_dict = {
    'INPUT': countries_drop_fields,#vector de capa de entrada a reproyectar
    'TARGET_CRS': crs_wcea, #Sistema de referencia de coordenadas (CRS) de destino
    'OUTPUT': 'memory:'#especifica vector de capa de salida
}
#ejecutamos el algoritmo usando run()
countries_reprojected = processing.run('native:reprojectlayer', reproj_dict)['OUTPUT']

##################################################################
# Fix geometries
##################################################################
print('fixing geometries')
#El algortimo "fix geometries" intenta crear una representación válida de una geometría no válida dada sin perder ninguno de los vértices de entrada. Las geometrías ya válidas se devuelven sin más intervención. Siempre genera una capa de geometría múltiple.(https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectorgeometry.html#fix-geometries)
fixgeo_dict = {
    'INPUT': countries_reprojected,#establece el vector de la capa de entrada a utilizar
    'OUTPUT': 'memory:'#especifica el vector de la capa de salida
}
#ejecutamos el algoritmo usando run()
countries_fix_geo = processing.run('native:fixgeometries', fixgeo_dict)['OUTPUT']

##################################################################
# Field calculator, output to csv
##################################################################
print('calculating country areas')
#Se crea una nueva capa con el resultado del algoritmo. https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectortable.html#field-calculator
#En este caso, calculamos el area de los países 
fcalc_dict = {
    'FIELD_LENGTH': 10, #La longitud del field de resultado
    'FIELD_NAME': 'km2area',#el nombre del field que va a contener los resultados
    'FIELD_PRECISION': 3,#precisión del field resultante (de 0 a 15). El default es 3.
    'FIELD_TYPE': 0,#tipo del field: 0 — Float
    'FORMULA': 'area($geometry)/1000000',#fórmula usada para calcular el resultado
    'INPUT': countries_fix_geo,#capa sobre la que se calcula
    'NEW_FIELD': True,#especifica que el resultado este en un nuevo field
    'OUTPUT': areas_out#especifica la capa de output
}
#ejecutamos el algoritmo usando run()
processing.run('qgis:fieldcalculator', fcalc_dict)


print('DONE!')


