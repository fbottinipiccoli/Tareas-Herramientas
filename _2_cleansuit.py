#########################################################################################
#########################################################################################
#Basado en: https://github.com/sebastianhohmann/gis_course/tree/master/QGIS/research_course
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
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
########################################################################################
#########################################################################################

# set paths to inputs and outputs
mainpath = "Users/federica/Documents/MAESTRÍA/2trimestre/herramientas computacionales/clase 5/input"
suitin = "{}/suit/suit/hdr.adf".format(mainpath)
outpath = "{}/_output/".format(mainpath)
suitout = "{}/landquality.tif".format(outpath)

# defining WGS 84 SR (#CRS (coordinate reference system) define una proyección de mapa específica, así como las transformaciones entre diferentes sistemas de referencia de coordenadas.)
crs_wgs84 = QgsCoordinateReferenceSystem("epsg:4326")

##################################################################
# Warp (reproject)
##################################################################
# note: Warp does not accept memory output
# could also specify: 'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
# this will create new files in your OS temp directory (in my (Windows) case:
# /user/Appdata/Local/Temp/processing_somehashkey
print('defining projection for the suitability data')
#Definimos el diccionario para el algoritmo de WARP y pasamos los valores de los parámetros originales de "input" y "output"
warp_dict = {
    'DATA_TYPE': 0, #Define el formato del archivo ráster de salida.Opciones: 0 — Use input layer data type
    'EXTRA': '', #Agrega opciones adicionales de línea de comando GDAL.
    'INPUT': suitin, #Input layer
    'MULTITHREADING': False, #Se utilizarán dos subprocesos para procesar fragmentos de la imagen y realizar operaciones de entrada / salida simultáneamente.
    'NODATA': None, #Establece el valor de nodata para las bandas de salida. Si no se proporciona, los valores nodata se copiarán del conjunto de datos de origen.
    'OPTIONS': '', #Para agregar una o más opciones de creación que controlen el ráster a crear (colores, tamaño de bloque, compresión de archivos…). Para conveniencia, utilizamos los perfiles predeterminados.
    'RESAMPLING': 0, #Método de remuestreo de valor de píxel a utilizar. Opciones: 0- Nearest neighbour
    'SOURCE_CRS': None, #Define el CRS de la capa ráster de entrada.
    'TARGET_CRS': crs_wgs84, #CRS de la capa raster de salida
    'TARGET_EXTENT': None, #Establece la extensión georreferenciada del archivo de salida que se creará (en Target CRS de forma predeterminada.
    'TARGET_EXTENT_CRS': None, #Especifica el CRS en el que interpretar las coordenadas dadas para la extensión del archivo de salida.
    'TARGET_RESOLUTION': None, #Define la resolución del archivo de salida del resultado de la reproyección.
    'OUTPUT': suitout #La capa ráster de salida (con la nueva información de proyección)
}
#ejecutamos el algoritmo usando run()
processing.run('gdal:warpreproject', warp_dict)


##################################################################
# Extract projection
##################################################################
print('extracting the projection for land suitability')
#Extrae la proyección de un archivo ráster y lo escribe en un archivo mundial. El algoritmo se deriva de la utilidad GDAL srsinfo (https://docs.qgis.org/2.18/en/docs/user_manual/processing_algs/gdalogr/gdal_projections.html)
extpr_dict = {
    'INPUT': suitout,#archivo raster de entrada
    'PRJ_FILE_CREATE': True #Si está activado, también se crea un archivo * .prj que contiene la información de la proyección. Default: False
}
#ejecutamos el algoritmo usando run()
processing.run('gdal:extractprojection', extpr_dict)

print('DONE!')
