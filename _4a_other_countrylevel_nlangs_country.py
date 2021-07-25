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


# set paths to inputs and outputs
mainpath = "/Users/federica/Documents/MAESTRÍA/2trimestre/herramientas computacionales/clase 5/input"
outpath = "{}/_output/".format(mainpath)
greg = "{}/greg_cleaned.shp".format(outpath)
wlds = "{}/wlds_cleaned.shp".format(outpath)
admin = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)
outcsv = "{}/nlangs_country.csv".format(outpath)

#########################################################################
#########################################################################
# 1) number of languages per country
#########################################################################
#########################################################################

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, languages')
#El algortimo "fix geometries" intenta crear una representación válida de una geometría no válida dada sin perder ninguno de los vértices de entrada. Las geometrías ya válidas se devuelven sin más intervención. Siempre genera una capa de geometría múltiple.(https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectorgeometry.html#fix-geometries)
fg1_dict = {
    'INPUT': wlds,#establece el vector de la capa de entrada a utilizar
    'OUTPUT': 'memory:'#especifica el vector de la capa de salida
}
#ejecutamos el algoritmo usando run()
fixgeo_wlds = processing.run('native:fixgeometries', fg1_dict)['OUTPUT']

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, countries')
#El algortimo "fix geometries" intenta crear una representación válida de una geometría no válida dada sin perder ninguno de los vértices de entrada. Las geometrías ya válidas se devuelven sin más intervención. Siempre genera una capa de geometría múltiple.(https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectorgeometry.html#fix-geometries)
fg2_dict = {
    'INPUT': admin,#establece el vector de la capa de entrada a utilizar
    'OUTPUT': 'memory:'#especifica el vector de la capa de salida
}
#ejecutamos el algoritmo usando run()
fixgeo_countries = processing.run('native:fixgeometries', fg2_dict)['OUTPUT']

#########################################################
# Intersection
#########################################################
print('intersecting')
#El algoritmo "Intersection" extrae las partes de las características de la capa de entrada que se superponen en la capa de superposición.
#A las características de la capa de intersección se les asignan los atributos de las entidades superpuestas de las capas de entrada y de superposición.
#Los atributos no se modifican (https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectoroverlay.html#intersection)
int_dict = {
    'INPUT': fixgeo_wlds,#Capa de la que extraer (partes de) características.
    'INPUT_FIELDS': 'GID',#fields de la capa de entrada que queremos mantener en la capa de salida. Si no se eligen los fields, se mantienen todos por default.
    'OVERLAY': fixgeo_countries,#Capa que contiene las características para comprobar si se superponen. Se espera que la geometría de sus entidades tenga al menos tantas dimensiones (punto: 0D, línea: 1D, polígono: 2D, volumen: 3D) como la capa de entrada.
    'OVERLAY_FIELDS': 'ADMIN',#fields de la capa de superposición que queremos mantener en la capa de salida
    'OUTPUT': 'memory:'#especifica la capa para contener (las partes de) las características de la capa de entrada que se superponen a una o más características de la capa de superposición.
}
#ejecutamos el algoritmo usando run()
intersection = processing.run('native:intersection', int_dict)['OUTPUT']

#########################################################
# Statistics by categories
#########################################################
print('statistics by categories')        
#El algoritmos calcula las estadísticas de un campo en función de una clase principal. La clase principal es una combinación de valores de otros campos.(https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectoranalysis.html#statistics-by-categories)

sbc_dict = {
    'CATEGORIES_FIELD_NAME': 'ADMIN', #fields que (combinados) definen las categorías
    'INPUT': intersection, #Capa de vector de entrada con clases y valores únicos
    'VALUES_FIELD_NAME': None, #Si está vacío, solo se calculará el recuento
    'OUTPUT': outcsv #Tabla de las estadísticas generadas
}
#ejecutamos el algoritmo usando run()
processing.run('qgis:statisticsbycategories', sbc_dict)


print('DONE!')
