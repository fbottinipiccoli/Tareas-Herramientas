#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
#Basado en: https://github.com/sebastianhohmann/gis_course/tree/master/QGIS/research_course
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
outpath = "{}/_output".format(mainpath)
junkpath = "{}/junk".format(outpath)

coastin = "{}/ne_10m_coastline/ne_10m_coastline.shp".format(mainpath)
adminin = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)

coastout = "{}/coast.shp".format(junkpath)
centroidsout = "{}/centroids.shp".format(junkpath)
distout = "{}/distance.shp".format(junkpath)
nearout = "{}/nearest.shp".format(junkpath)
testout = "{}/testout.shp".format(junkpath)
csvout = "{}/centroids_closest_coast.csv".format(outpath)

if not os.path.exists(junkpath):#se utiliza para comprobar si la ruta especificada existe o no, y también se puede usar para verificar si la ruta dada se refiere a un descriptor de archivo abierto o no. (https://www.geeksforgeeks.org/python-os-path-exists-method/)
    os.mkdir(junkpath) #crea un directorio llamado "path" con el modo numérico especificado. Este método genera FileExistsError si el directorio que se va a crear ya existe. (source: https://www.geeksforgeeks.org/python-os-mkdir-method/)


# #########################################################################
# #########################################################################
# # 2) centroids and distance to coast
# #########################################################################
# #########################################################################

# #########################################################
# # Fix geometries
# #########################################################
print('fixing geometries, coast')
#El algortimo "fix geometries" intenta crear una representación válida de una geometría no válida dada sin perder ninguno de los vértices de entrada. Las geometrías ya válidas se devuelven sin más intervención. Siempre genera una capa de geometría múltiple.(https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectorgeometry.html#fix-geometries)
# fg1_dict = {
   'INPUT': coastin, #establece el vector de la capa de entrada a utilizar
        'OUTPUT': 'memory:' #especifica el vector de la capa de salida
 }
#ejecutamos el algoritmo usando run()
fixgeo_coast = processing.run('native:fixgeometries', fg1_dict)['OUTPUT']


# #########################################################
# # Fix geometries
# #########################################################
 print('fixing geometries, countries')
 #El algortimo "fix geometries" intenta crear una representación válida de una geometría no válida dada sin perder ninguno de los vértices de entrada. Las geometrías ya válidas se devuelven sin más intervención. Siempre genera una capa de geometría múltiple.(https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectorgeometry.html#fix-geometries)
fg2_dict = {
     'INPUT': adminin, #establece el vector de la capa de entrada a utilizar
     'OUTPUT': 'memory:' #especifica el vector de la capa de salida
 }
#ejecutamos el algoritmo usando run()
 fixgeo_countries = processing.run('native:fixgeometries', fg2_dict)['OUTPUT']

# #########################################################
# # Centroids
# #########################################################
 print('finding country centroids')
#El algoritmo crea una nueva capa de puntos, con puntos que representan los centroides de las geometrías de la capa de entrada.
#El centroide es un único punto que representa el baricentro (de todas las partes) de la entidad, por lo que puede estar fuera de los bordes de la entidad. Pero también puede ser un punto en cada parte de la función.
#Los atributos de los puntos en la capa de salida son los mismos que para las características originales

cts_dict = {
    'ALL_PARTS': False, #Si es Verdadero (marcado), se creará un centroide para cada parte de la geometría
     'INPUT': fixgeo_countries, #vector de capa de entrada
     'OUTPUT': 'memory:'#especifica la capa de salida del centroide
 }
#ejecutamos el algoritmo usando run()
 country_centroids = processing.run('native:centroids', cts_dict)['OUTPUT']

# #########################################################
# # Add geometry attributes
# #########################################################    
print('adding co-ordinates to centroids')    
#El algoritmo calcula las propiedades geométricas de las características en una capa vectorial y las incluye en la capa de salida.
#Genera una nueva capa vectorial con el mismo contenido que la de entrada, pero con atributos adicionales, que contiene medidas geométricas basadas en un CRS seleccionado.
 aga1_dict = {
     'CALC_METHOD': 0,#Parámetros de cálculo a utilizar para las propiedades geométricas.0 - Capa CRS
     'INPUT': country_centroids, #Capa de vector de entrada
     'OUTPUT': 'memory:'#Especifica la capa de salida
 }
#ejecutamos el algoritmo usando run()
 centroids_with_coordinates = processing.run('qgis:exportaddgeometrycolumns', aga1_dict)['OUTPUT']

# ##################################################################
# # Drop field(s)
# ##################################################################
 print('dropping unnecessary fields, coast')
    # Descartamos las columnas que no utilizaremos
 allfields = [field.name() for field in fixgeo_coast.fields()]  #Obtenemos todos los fields de atributos
 keepfields = ['featurecla'] #establecemos los campos que queremos conservar bajo el nombre "keepfields"
 dropfields = [field for field in allfields if field not in keepfields] #especificamos los campos que queremos eliminar como todos los campos que no pertenezcan al grupo "keepfields"

 df1_dict = {
     'COLUMN': dropfields, #fields a eliminar
     'INPUT': fixgeo_coast, #vector de la capa de input de la cual borrar los fields
     'OUTPUT': coastout #Especifica el vector que contendrá los fields restantes
 }
#ejecutamos el algoritmo usando run()
 processing.run('qgis:deletecolumn', df1_dict)
    
# ##################################################################
# # Drop field(s)
# ##################################################################
# Descartamos las columnas que no utilizaremos
 print('dropping unnecessary fields, countries')
 allfields = [field.name() for field in centroids_with_coordinates.fields()] #Obtenemos todos los fields de atributos
 keepfields = ['ne_10m_adm', 'ADMIN', 'ISO_A3', 'xcoord', 'ycoord'] #establecemos los campos que queremos conservar bajo el nombre "keepfields"
 dropfields = [field for field in allfields if field not in keepfields] #especificamos los campos que queremos eliminar como todos los campos que no pertenezcan al grupo "keepfields"

 df2_dict = {
     'COLUMN': dropfields, #fields a eliminar
     'INPUT': centroids_with_coordinates, #vector de la capa de input de la cual borrar los fields
     'OUTPUT': centroidsout #Especifica el vector que contendrá los fields restantes
 }
#ejecutamos el algoritmo usando run()
 processing.run('qgis:deletecolumn', df2_dict)

##################################################################
# v.distance
##################################################################
#Busca el elemento más cercano en el mapa vectorial 'to' para los elementos en el mapa vectorial 'from'. (https://grass.osgeo.org/grass78/manuals/v.distance.html)
print('vector distance')
vd_dict = {
'from': centroidsout,#Nombre del mapa vectorial existente (from)
    'from_type': [0],#tipo del atributo 
    'to': coastout,#Nombre del mapa vectorial existente (to)
    'to_type': [1],#Tipo de característica (to)
    'dmax': -1,#Distancia máxima o -1 para sin límite
    'dmin': -1,#Distancia mínima o -1 para sin límite
    'upload': [1],#Valores que describen la relación entre dos características más cercanas
    'column': ['xcoord'],#Nombre (s) de columna donde se cargarán los valores especificados por la opción 'upload'
    'to_column': None,#Nombre de columna de la característica más cercana
    'from_output': nearout,
    'output': distout,#Nombre del mapa vectorial de salida que contiene las líneas que conectan los elementos más cercanos
    'GRASS_REGION_PARAMETER': None,
    'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
    'GRASS_MIN_AREA_PARAMETER': 0.0001,
    'GRASS_OUTPUT_TYPE_PARAMETER': 0,
    'GRASS_VECTOR_DSCO': '',
    'GRASS_VECTOR_LCO': '',
    'GRASS_VECTOR_EXPORT_NOCAT': False
}
#ejecutamos el algoritmo usando run()
processing.run('grass7:v.distance', vd_dict)


# #########################################################################################################
# #########################################################################################################
# #########################################################################################################
# #########################################################################################################


# ##################################################################
# # Field calculator
# ##################################################################
 print('adjusting the "cat" field in the nearest centroids to merge with distance lines')
 #Se crea una nueva capa con el resultado del algoritmo. https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectortable.html#field-calculator

fc1_dict = {
     'FIELD_LENGTH': 4,#La longitud del field de resultado
     'FIELD_NAME': 'cat', #el nombre del field que va a contener los resultados
     'FIELD_PRECISION': 3,#precisión del field resultante (de 0 a 15). El default es 3.
     'FIELD_TYPE': 1,#tipo del field: 1 — Integer
     'FORMULA': 'attribute($currentfeature, \'cat\')-1', #fórmula usada para calcular el resultado
     'INPUT': nearout,#capa sobre la que se calcula
     'NEW_FIELD': False,#especifica que el resultado no este en un nuevo field
     'OUTPUT': 'memory:'#especifica la capa de output
 }
#ejecutamos el algoritmo usando run()
 nearest_cat_adjust = processing.run('qgis:fieldcalculator', fc1_dict)['OUTPUT']


# ##################################################################
# # Drop field(s)
# ##################################################################
 print('dropping unnecessary fields, nearest (the co-ordinates get screwed up')
    # Descartamos las columnas que no utilizaremos
 df3_dict = {
     'COLUMN': ['xcoord', 'ycoord'],#fields a eliminar
     'INPUT': nearest_cat_adjust,#vector de la capa de input de la cual borrar los fields
     'OUTPUT': 'memory:'#Especifica el vector que contendrá los fields restantes
 }
#ejecutamos el algoritmo usando run()
 nearest_cat_adjust_dropfields = processing.run('qgis:deletecolumn', df3_dict)['OUTPUT']

# ##################################################################
# # Join attributes by field value
# ##################################################################
print('merging the two tables: nearest and centroids: correct co-ordiantes')
#Toma una capa de vector de entrada y crea una nueva capa de vector que es una versión extendida de la de entrada, con atributos adicionales en su tabla de atributos.
#Los atributos adicionales y sus valores se toman de una segunda capa vectorial. En cada uno de ellos se selecciona un atributo para definir los criterios de unión
 jafv1_dict = {
     'DISCARD_NONMATCHING': False,#Comprueba si no desea conservar las funciones a las que no se pudo unir
     'FIELD': 'ne_10m_adm',#Campo de la capa de origen que se utilizará para la unión
     'FIELDS_TO_COPY': None,#Selecciona los fields específicos que se desean agregar. De forma predeterminada, se agregan todos los fields.
     'FIELD_2': 'ne_10m_adm',#field de la segunda capa (combinación) que se utilizará para la combinación. El tipo de field debe ser igual (o compatible) con el tipo de field de la tabla de entrada.
     'INPUT': centroidsout,#Capa de vector de entrada. La capa de salida constará de las características de esta capa con atributos de las características coincidentes en la segunda capa.
     'INPUT_2': nearest_cat_adjust_dropfields,#Capa con la tabla de atributos para unir
     'METHOD': 1, #tipo de la última capa unida. 1 - Tomar atributos de la primera característica coincidente únicamente (uno a uno)
     'PREFIX': '',#Agrega un prefijo a los fields unidos para identificarlos fácilmente y evitar la colisión de nombres de cfield
     'OUTPUT': 'memory:'#Especifique la capa del vector de salida para la unión.
 }
#ejecutamos el algoritmo usando run()
 centroids_nearest_coast_joined = processing.run('native:joinattributestable', jafv1_dict)['OUTPUT']

# ##################################################################
# # Drop field(s)
# ##################################################################
#Descartamos las variables: featurecla;scalerank;LABELRANK;SOVEREIGNT;SOV_A3;ADM0_DIF;LEVEL;TYPE;ADM0_A3;GEOU_DIF;GEOUNIT;GU_A3;SU_DIF;SUBUNIT;SU_A3;BRK_DIFF;NAME;NAME_LONG;BRK_A3;BRK_NAME;BRK_GROUP;ABBREV;POSTAL;FORMAL_EN;FORMAL_FR;NAME_CIAWF;NOTE_ADM0;NOTE_BRK;NAME_SORT;NAME_ALT;MAPCOLOR7;MAPCOLOR8;APCOLOR9;MAPCOLOR13;POP_EST;POP_RANK;GDP_MD_EST;POP_YEAR;LASTCENSUS;GDP_YEAR;ECONOMY;INCOME_GRP;WIKIPEDIA;FIPS_10_;ISO_A2;ISO_A3_EH;ISO_N3;UN_A3;WB_A2;WB_A3;WOE_ID;WOE_ID_EH;WOE_NOTE;ADM0_A3_IS;ADM0_A3_US;ADM0_A3_UN;ADM0_A3_WB;CONTINENT;REGION_UN;SUBREGION;REGION_WB;NAME_LEN;LONG_LEN;ABBREV_LEN;TINY;HOMEPART;MIN_ZOOM;MIN_LABEL;MAX_LABEL;NE_ID;WIKIDATAID;NAME_AR;NAME_BN;NAME_DE;NAME_EN;NAME_ES;NAME_FR;NAME_EL;NAME_HI;NAME_HU;NAME_ID;NAME_IT;NAME_JA;NAME_KO;NAME_NL;NAME_PL;NAME_PT;NAME_RU;NAME_SV;NAME_TR;NAME_VI;NAME_ZH;MAPCOLOR9;ADMIN_2;ISO_A3_2
 print('dropping unnecessary fields, nearest and centroids merge')
 df4_dict = {
     'COLUMN': ['ne_10m_adm_2', 'ADMIN_2', 'ISO_A3_2'], #fields a eliminar
     'INPUT': centroids_nearest_coast_joined, #vector de la capa de input de la cual borrar los fields
     'OUTPUT': 'memory:'#Especifica el vector que contendrá los fields restantes
 }
#ejecutamos el algoritmo usando run()
 centroids_nearest_coast_joined_dropfields = processing.run('qgis:deletecolumn', df4_dict)['OUTPUT']

# ##################################################################
# # Join attributes by field value
# ##################################################################
 print('merging the two tables: nearest (adjusted) and distance (this adds countries to each centroid-coast line)')
#Toma una capa de vector de entrada y crea una nueva capa de vector que es una versión extendida de la de entrada, con atributos adicionales en su tabla de atributos.
#Los atributos adicionales y sus valores se toman de una segunda capa vectorial. En cada uno de ellos se selecciona un atributo para definir los criterios de unión 
jafv2_dict = {
     'DISCARD_NONMATCHING': False, #Comprueba si no desea conservar las funciones a las que no se pudo unir
     'FIELD': 'cat',#Campo de la capa de origen que se utilizará para la unión
     'FIELDS_TO_COPY': None,#Selecciona los fields específicos que se desean agregar. De forma predeterminada, se agregan todos los fields.
     'FIELD_2': 'cat',#field de la segunda capa (combinación) que se utilizará para la combinación. El tipo de field debe ser igual (o compatible) con el tipo de field de la tabla de entrada.
     'INPUT': distout,#Capa de vector de entrada. La capa de salida constará de las características de esta capa con atributos de las características coincidentes en la segunda capa.
     'INPUT_2': centroids_nearest_coast_joined_dropfields,#Capa con la tabla de atributos para unir
     'METHOD': 1,#tipo de la última capa unida. 1 - Tomar atributos de la primera característica coincidente únicamente (uno a uno)
     'PREFIX': '',#Agrega un prefijo a los fields unidos para identificarlos fácilmente y evitar la colisión de nombres de cfield
     'OUTPUT': 'memory:'#Especifique la capa del vector de salida para la unión.
 }
 #ejecutamos el algoritmo usando run()
 centroids_nearest_coast_distance_joined = processing.run('native:joinattributestable', jafv2_dict)['OUTPUT']


# ##################################################################
# # Extract vertices
# ##################################################################   
 print('extracting vertices (get endpoints of each line)')   
#Toma una capa vectorial y genera una capa de puntos con puntos que representan los vértices en las geometrías de entrada.
#Los atributos asociados a cada punto son los mismos asociados a la característica a la que pertenece el vértice.
#Se agregan fields adicionales a los vértices que indican el índice del vértice (comenzando en 0), la parte de la entidad y su índice dentro de la parte (así como su anillo para polígonos), la distancia a lo largo de la geometría original y el ángulo bisector del vértice para la geometría original.
 ev_dict = {
     'INPUT': centroids_nearest_coast_distance_joined,#capa de entrada
     'OUTPUT': 'memory:'#capa de salida
 }
  #ejecutamos el algoritmo usando run()
 extract_vertices = processing.run('native:extractvertices', ev_dict)['OUTPUT']

# ##################################################################
# # Extract by attribute
# ##################################################################
 print('keeping only vertices on coast')
    #Crea dos capas vectoriales a partir de una capa de entrada: una contendrá solo caracteristicas coincidentes mientras que la segunda contendrá todas las características no coincidentes.
    #Los criterios para agregar características a la capa resultante se basan en los valores de un atributo de la capa de entrada.
 eba_dict = {
     'FIELD': 'distance', #Campo de filtrado de la capa
     'INPUT': extract_vertices,#capa de la cual se extraen las características
     'OPERATOR': 2,#2 — >
     'VALUE': '0',#Valor a evaluar
     'OUTPUT': 'memory:'#Especifica la capa del vector de salida para las entidades coincidentes.
 }
  #ejecutamos el algoritmo usando run()
 extract_by_attribute = processing.run('native:extractbyattribute', eba_dict)['OUTPUT']

# ##################################################################
# # Field calculator
# ##################################################################
 print('creating new field: centroid latitude (keep field names straight)')
    # #Se crea una nueva capa con el resultado del algoritmo.
 fc2_dict = {
     'FIELD_LENGTH': 10,#La longitud del field de resultado
     'FIELD_NAME': 'cent_lat',#el nombre del field que va a contener los resultados
     'FIELD_PRECISION': 10,#precisión del field resultante (de 0 a 15). El default es 3.
     'FIELD_TYPE': 0,#tipo del field:0 — Float
     'FORMULA': 'attribute($currentfeature, \'ycoord\')',#fórmula usada para calcular el resultado
     'INPUT': extract_by_attribute,#capa sobre la que se calcula
     'NEW_FIELD': False,#especifica que el resultado no este en un nuevo field
     'OUTPUT': 'memory:'#especifica la capa de output
 }
  #ejecutamos el algoritmo usando run()
 added_field_cent_lat = processing.run('qgis:fieldcalculator', fc2_dict)['OUTPUT']

 print('creating new field: centroid longitude (keep field names straight)')
 fc3_dict = {
     'FIELD_LENGTH': 10,#La longitud del field de resultado
     'FIELD_NAME': 'cent_lon',#el nombre del field que va a contener los resultados
     'FIELD_PRECISION': 10,#precisión del field resultante (de 0 a 15). El default es 3.
     'FIELD_TYPE': 0,#tipo del field:0 — Float
     'FORMULA': 'attribute($currentfeature, \'xcoord\')',#fórmula usada para calcular el resultado
     'INPUT': added_field_cent_lat,#capa sobre la que se calcula
     'NEW_FIELD': False,#especifica que el resultado no este en un nuevo field
     'OUTPUT': 'memory:' #especifica la capa de output
 }
  #ejecutamos el algoritmo usando run()
 added_field_cent_lon = processing.run('qgis:fieldcalculator', fc3_dict)['OUTPUT']

# ##################################################################
# # Drop field(s)
# ##################################################################
 print('dropping unnecessary fields')
    #Descartamos las variables: fid;cat;xcoord;ycoord;fid_2;cat_2;vertex_index;vertex_part;vertex_part;_index;angle
 allfields = [field.name() for field in added_field_cent_lon.fields()]#Obtenemos todos los fields de atributos
 keepfields = ['ne_10m_adm', 'ADMIN', 'ISO_A3', 'cent_lat', 'cent_lon']#establecemos los campos que queremos conservar bajo el nombre "keepfields"
 dropfields = [field for field in allfields if field not in keepfields]#especificamos los campos que queremos eliminar como todos los campos que no pertene

 df5_dict = {
     'COLUMN': dropfields,#fields a eliminar
     'INPUT': added_field_cent_lon,#vector de la capa de input de la cual borrar los fields
     'OUTPUT': 'memory:'#Especifica el vector que contendrá los fields restantes
 }
      #ejecutamos el algoritmo usando run()
 centroids_lat_lon_drop_fields = processing.run('qgis:deletecolumn', df5_dict)['OUTPUT']

# #########################################################
# # Add geometry attributes
# #########################################################    
print('adding co-ordinates to coast points')    
#El algoritmo calcula las propiedades geométricas de las características en una capa vectorial y las incluye en la capa de salida.
#Genera una nueva capa vectorial con el mismo contenido que la de entrada, pero con atributos adicionales, que contiene medidas geométricas basadas en un CRS seleccionado.
 aga2_dict = {
     'CALC_METHOD': 0,#Parámetros de cálculo a utilizar para las propiedades geométricas.0 - Capa CRS
     'INPUT': centroids_lat_lon_drop_fields,#capa de vector de entrada
     'OUTPUT': 'memory:'#capa de salida
 }
    #ejecutamos el algoritmo usando run()
 add_geo_coast = processing.run('qgis:exportaddgeometrycolumns', aga2_dict)['OUTPUT']

# ##################################################################
# # Field calculator
# ##################################################################
 print('creating new field: centroid latitude (keep field names straight)')
# Se crea una nueva capa con el resultado del algoritmo.
     fc4_dict = {
     'FIELD_LENGTH': 10,#La longitud del field de resultado
     'FIELD_NAME': 'coast_lat',#el nombre del field que va a contener los resultados
     'FIELD_PRECISION': 10,#precisión del field resultante (de 0 a 15). El default es 3.
     'FIELD_TYPE': 0,#tipo del field:0 — Float
     'FORMULA': 'attribute($currentfeature, \'ycoord\')',#fórmula usada para calcular el resultado
     'INPUT': add_geo_coast,#capa sobre la que se calcula
     'NEW_FIELD': False,#especifica que el resultado no este en un nuevo field
     'OUTPUT': 'memory:'#especifica la capa de output
 }
    #ejecutamos el algoritmo usando run()
 added_field_coast_lat = processing.run('qgis:fieldcalculator', fc4_dict)['OUTPUT']

 print('creating new field: centroid longitude (keep field names straight)')
 fc5_dict = {
     'FIELD_LENGTH': 10,#La longitud del field de resultado
     'FIELD_NAME': 'coast_lon',#el nombre del field que va a contener los resultados
     'FIELD_PRECISION': 10,#precisión del field resultante (de 0 a 15). El default es 3.
     'FIELD_TYPE': 0,#tipo del field:0 — Float
     'FORMULA': 'attribute($currentfeature, \'xcoord\')',#fórmula usada para calcular el resultado
     'INPUT': added_field_coast_lat,#capa sobre la que se calcula
     'NEW_FIELD': False,#especifica que el resultado no este en un nuevo field
     'OUTPUT': 'memory:'#especifica la capa de output
 }
#ejecutamos el algoritmo usando run()
 added_field_coast_lon = processing.run('qgis:fieldcalculator', fc5_dict)['OUTPUT']

# ##################################################################
# # Drop field(s)
# ##################################################################
 print('dropping unnecessary fields')
#Descartamos las variables: xcoord;ycoord
 df6_dict = {
     'COLUMN': ['xcoord', 'ycoord'],#fields a eliminar
     'INPUT': added_field_coast_lon,#vector de la capa de input de la cual borrar los fields
     'OUTPUT': csvout#Especifica el vector que contendrá los fields restantes
 }
    #ejecutamos el algoritmo usando run()
 processing.run('qgis:deletecolumn', df6_dict)


print('DONE!')
