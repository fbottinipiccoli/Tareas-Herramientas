#########################################################################################
#########################################################################################
#Basado en: https://github.com/sebastianhohmann/gis_course/tree/master/QGIS/research_course
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
rint('preliminary setup')
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
mainpath = "/Users/federica/Documents/MAESTRÍA/2trimestre/herramientas computacionales/clase 5/input"
wldsin = "{}/langa.shp".format(mainpath)
outpath = "{}/_output/".format(mainpath)
wldsout = "{}/wlds_cleaned.shp".format(outpath)

if not os.path.exists(outpath): #se utiliza para comprobar si la ruta especificada existe o no, y también se puede usar para verificar si la ruta dada se refiere a un descriptor de archivo abierto o no. (https://www.geeksforgeeks.org/python-os-path-exists-method/) #
	os.mkdir(outpath) #crea un directorio llamado "path" con el modo numérico especificado. Este método genera FileExistsError si el directorio que se va a crear ya existe. (source: https://www.geeksforgeeks.org/python-os-mkdir-method/)

#########################################################
# Fix geometries
#########################################################
print('fixing geometries')
#En primer lugar, arreglamos las geometrías para procesar el shapefile, dado que los polígonos se encuentran encimados. 
#El algortimo "fix geometries" intenta crear una representación válida de una geometría no válida dada sin perder ninguno de los vértices de entrada. Las geometrías ya válidas se devuelven sin más intervención. Siempre genera una capa de geometría múltiple.(https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectorgeometry.html#fix-geometries)
fixgeo_dict = {
    'INPUT': wldsin,#establece el vector de la capa de entrada a utilizar
    'OUTPUT': 'memory:'#especifica el vector de la capa de salida
}
#ejecutamos el algoritmo usando run()
fix_geo = processing.run('native:fixgeometries', fixgeo_dict)['OUTPUT']    

#######################################################################
# Add autoincremental field
#######################################################################
print('adding autoincremental id-field')
#El algoritmo Add autoincremental field agrega un nuevo campo entero a una capa vectorial, con un valor secuencial para cada entidad. Este campo se puede utilizar como un ID único para las entidades de la capa. El nuevo atributo no se agrega a la capa de entrada, sino que se genera una nueva capa. (source: https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectortable.html#add-autoincremental-field)
#En este caso utilizarmos "Add autoincremental field" para ennumerar los países (asignarles un número que los identifique, empezando desde el 1)
aaicf_dict = {
    'FIELD_NAME': 'GID',#nombre del campo que contiene los valores autoincrementales
    'GROUP_FIELDS': None, #selecciona campo (s) de agrupación: en lugar de una sola ejecución de recuento para toda la capa, se procesa un recuento separado para cada valor devuelto por la combinación de estos campos.
    'INPUT': fix_geo,#establece el vector de input
    'SORT_ASCENDING': True,#controla el orden en el que se asignan valores a las funciones.
    'SORT_EXPRESSION': '',#utiliza una expresión para ordenar las entidades de la capa de forma global o, si está configurada, según los campos de grupo.
    'SORT_NULLS_FIRST': False,#opción para establecer si los valores nulos se cuentan primero o último.
    'START': 1,#establece el valor inicial con el que se ennumera
    'OUTPUT': 'memory:'#capa del vector de salida con el campo de incremento automático.
    }
#ejecutamos el algoritmo usando run()
autoinc_id = processing.run('native:addautoincrementalfield', aaicf_dict)['OUTPUT'] 

#########################################################
# Field calculator
#########################################################
print('copying language name into a field with shorter attribute name')
#Se crea una nueva capa con el resultado del algoritmo. https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectortable.html#field-calculator
#En este caso, utilizamos Field Calculator para calcular largo variable NAME PROP. Generamos una nueva variable "lmn" con aquellas observaciones que tienen menos de 10 caracteres 
fc_dict = {
    'FIELD_LENGTH': 10,#La longitud del field de resultado, en este caso: 10 caracteres
    'FIELD_NAME': 'lnm',#el nombre del field que va a contener los resultados
    'FIELD_PRECISION': 0,#precisión del field resultante (de 0 a 15). El default es 3.
    'FIELD_TYPE': 2,#tipo del field: 2- String
    'FORMULA': ' attribute($currentfeature, \'NAME_PROP\')',#fórmula usada para calcular el resultado
    'INPUT': autoinc_id,#capa sobre la que se calcula
    'NEW_FIELD': True, #especifica que el resultado este en un nuevo field
    'OUTPUT': 'memory:'#especifica la capa de output
}
#ejecutamos el algoritmo usando run()
field_calc = processing.run('qgis:fieldcalculator', fc_dict)['OUTPUT']

#########################################################
# Drop field(s)
#########################################################
print('dropping fields except GID, ID, lnm')
# Descartamos las columnas que no utilizaremos: ID_ISO_A3;ID_ISO_A2;ID_FIPS;NAM_LABEL;NAME_PROP;NAME2;NAM_ANSI;CNT;C1;POP;LMP_POP1;G;LMP_CLASS;FAMILYPROP;FAMILY;langpc_km2;length
# getting all attribute fields
allfields = [field.name() for field in field_calc.fields()]
keepfields = ['GID', 'ID', 'lnm'] #establecemos los campos que queremos conservar bajo el nombre "keepfields"
dropfields = [field for field in allfields if field not in keepfields] #especificamos los campos que queremos eliminar como todos los campos que no pertenezcan al grupo "keepfields"

df3_dict = {
   'COLUMN': dropfields, #fields a eliminar
   'INPUT': field_calc, #vector de la capa de input de la cual borrar los fields
   'OUTPUT': wldsout #Especifica el vector que contendrá los fields restantes
}
#ejecutamos el algoritmo usando run()


print('DONE!')
