#########################################################################################
#########################################################################################
#Basado en: https://github.com/sebastianhohmann/gis_course/tree/master/QGIS/research_course
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
#En primer lugar, descargamos los datos que utilizaremos. 
#El objetivo de este trabajo es construir un modelo para calcular la idoneidad agr ́ıcola media de todos los condados de EE.UU.
#Descargamos los condados de EE.UU. de https://gadm.org/data.html. Del ZIP que les descarga, usamos el archivo gadm36 USA 2.shp
#Descargamos los datos rasterizados globales de idoneidad agr ́ıcola de https://nelson.wisc.edu/sage/data-and-models/ atlas/data.php?incdataset=Suitability%20for% 20Agriculture.

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

# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix 
QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Add the path to Processing framework  
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
# NOTE: if you run this script directly from the command line, you can specify relative
# paths, e.g. mainpath = "../gis_data", but this doesnt work with the QGIS python console
mainpath = "/Users/magibbons/Desktop/Herramientas/Clase5/input"
suitin = "{}/suit/suit/hdr.adf".format(mainpath)
adm2in = "{}/USA_adm_shp/USA_adm2.shp".format(mainpath)
outpath = "{}/_output/counties_agrisuit.csv".format(mainpath)
junkpath = "{}/_output/junk".format(mainpath)
junkfile = "{}/_output/junk/agrisuit.tif".format(mainpath)
if not os.path.exists(mainpath + "/_output"):#se utiliza para comprobar si la ruta especificada existe o no, y también se puede usar para verificar si la ruta dada se refiere a un descriptor de archivo abierto o no. (https://www.geeksforgeeks.org/python-os-path-exists-method/)
    os.mkdir(mainpath + "/_output")# #crea un directorio llamado "path" con el modo numérico especificado. Este método genera FileExistsError si el directorio que se va a crear ya existe. (source: https://www.geeksforgeeks.org/python-os-mkdir-method/)
if not os.path.exists(junkpath):
    os.mkdir(junkpath)

# defining WGS 84 SR
#CRS (coordinate reference system) define una proyección de mapa específica, así como las transformaciones entre diferentes sistemas de referencia de coordenadas.
crs_wgs84 = QgsCoordinateReferenceSystem("epsg:4326")

##################################################################
# Warp (reproject)
##################################################################
# note: Warp does not accept memory output
# could also specify: 'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
# this will create new files in your OS temp directory (in my (Windows) case:
# /user/Appdata/Local/Temp/processing_somehashkey
#Utilizamos la función Warp(reproject): Reproyecta una capa ráster en otro Sistema de referencia de coordenadas (CRS). Se puede elegir la resolución del archivo de salida y el método de remuestreo. (source: https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/gdal/rasterprojections.html)
print('defining projection for the suitability data')
#Definimos los parámetros para el algoritmo de WARP y pasamos los valores de los parámetros originales de "input" y "output"
alg_params = {
    'DATA_TYPE': 0, #Define el formato del archivo ráster de salida.Opciones: 0 — Use input layer data type
    'EXTRA': '', #Agrega opciones adicionales de línea de comando GDAL.
    'INPUT': suitin, #Input layer
    'MULTITHREADING': False, #Se utilizarán dos subprocesos para procesar fragmentos de la imagen y realizar operaciones de entrada / salida simultáneamente.
    'NODATA': None, #Establece el valor de nodata para las bandas de salida. Si no se proporciona, los valores nodata se copiarán del conjunto de datos de origen.
    'OPTIONS': '', #Para agregar una o más opciones de creación que controlen el ráster a crear (colores, tamaño de bloque, compresión de archivos…). Para conveniencia, utilizamos los perfiles predeterminados.
    'RESAMPLING': 0, #Método de remuestreo de valor de píxel a utilizar. Opciones: 0- Nearest neighbour
    'SOURCE_CRS': None,#Define el CRS de la capa ráster de entrada.
    'TARGET_CRS': crs_wgs84, #CRS de la capa raster de salida
    'TARGET_EXTENT': None, #Establece la extensión georreferenciada del archivo de salida que se creará (en Target CRS de forma predeterminada.
    'TARGET_EXTENT_CRS': None, #Especifica el CRS en el que interpretar las coordenadas dadas para la extensión del archivo de salida.
    'TARGET_RESOLUTION': None, #Define la resolución del archivo de salida del resultado de la reproyección.
    'OUTPUT': junkfile #La capa ráster de salida (con la nueva información de proyección)
}
#ejecutamos el algoritmo usando run()
suit_proj = processing.run('gdal:warpreproject', alg_params)['OUTPUT']

##################################################################
# Drop field(s)
##################################################################
print('dropping fields from the county data')
# Descartamos las variables que no utilizaremos de la capa que contiene la información de los counties. Descartamos las siguientes variables: GID_0;NAME_0;GID_1;GID_2;HASC_2;CC_2;TYPE_2;ENGTYPE_2;NL_NAME 2;VARNAME_2;NL_NAME_1;NL_NAME_2;ENG_TYPE
alg_params = {
    'COLUMN': [' ISO','ID_0','NAME_0','ID_1','ID_2',
               'HASC_2','CCN_2','CCA_2','TYPE_2',
               'ENGTYPE_2','NL_NAME_2','VARNAME_2'], #fields a eliminar
    'INPUT': adm2in,#vector de la capa de input de la cual borrar los fields
    'OUTPUT': 'memory:'#Especifica el vector que contendrá los fields restantes
}
#ejecutamos el algoritmo usando run()
counties_fields_dropped = processing.run('qgis:deletecolumn', alg_params)['OUTPUT']

###################################################################
# Add autoincremental field
###################################################################
#El algoritmo Add autoincremental field agrega un nuevo campo entero a una capa vectorial, con un valor secuencial para cada entidad. Este campo se puede utilizar como un ID único para las entidades de la capa. El nuevo atributo no se agrega a la capa de entrada, sino que se genera una nueva capa. (source: https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectortable.html#add-autoincremental-field)
print('adding unique ID to county data')
alg_params = {
    'FIELD_NAME': 'cid',#nombre del campo que contiene los valores autoincrementales
    'GROUP_FIELDS': [''],#selecciona campo (s) de agrupación: en lugar de una sola ejecución de recuento para toda la capa, se procesa un recuento separado para cada valor devuelto por la combinación de estos campos.
    'INPUT': counties_fields_dropped,#establece el vector de input
    'SORT_ASCENDING': True,#controla el orden en el que se asignan valores a las funciones.
    'SORT_EXPRESSION': '',#utiliza una expresión para ordenar las entidades de la capa de forma global o, si está configurada, según los campos de grupo.
    'SORT_NULLS_FIRST': False,#opción para establecer si los valores nulos se cuentan primero o último.
    'START': 1,#establece el valor inicial con el que se ennumera
    'OUTPUT': 'memory:'#capa del vector de salida con el campo de incremento automático.
}
#ejecutamos el algoritmo usando run()
counties_fields_autoid = processing.run('native:addautoincrementalfield', alg_params)['OUTPUT']

###################################################################
# Zonal statistics
###################################################################
print('computing zonal stats')
#Utilizamos la función Zonal statistics para calcular la idoneidad agrícola promedio.
#Esta función permite realizar cálculos sobre la base de los valores de píxeles de ráster existentes. Los resultados se escriben en una nueva capa ráster con un formato compatible con GDAL. (source: https://docs.qgis.org/2.14/en/docs/user_manual/working_with_raster/raster_analysis.html)
print('computing zonal stats')
alg_params = {
    'COLUMN_PREFIX': '_',#Prefijo para los nombres de las columnas de salida.
    'INPUT_RASTER': suit_proj,#capa raster que se usa de input
    'INPUT_VECTOR': counties_fields_autoid,#vector de la capa que utiliza como input
    'RASTER_BAND': 1,#Si el ráster es multibanda, se elige una banda para las estadísticas.
    'STATISTICS': 2 #Lista de operador estadístico para la salida. Opciones: 2 - Media
}
#ejecutamos el algoritmo usando run()
processing.run('native:zonalstatistics', alg_params)

#Exportamos el modelo que ejecutamos a Python. 
###################################################################
# write to CSV
###################################################################
print('outputting the data')
#Exportamos los datos a un archivo .csv

with open(outpath, 'w') as output_file: #seleccionamos el path de salida donde se va a crear el archivo con el nuevo contenido
    fieldnames = [field.name() for field in counties_fields_autoid.fields()] #obtiene fields con ese nombre
    line = ','.join(name for name in fieldnames) + '\n'
    output_file.write(line)
    for f in counties_fields_autoid.getFeatures():
        line = ','.join(str(f[name]) for name in fieldnames) + '\n' #método string que devuelve a los elementos de la secuencia como string unidos por un separador str.
        output_file.write(line)#cada elemento se escribe en el archivo de output

print('DONE!')
