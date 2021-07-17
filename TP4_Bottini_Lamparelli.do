**TP4: Herramientas Computacionales**

/* Bottini Piccoli, Federica 
Lamparelli, Carolina 

* Trabajo basado en
"Econometría Espacial usando Stata. Guía Teórico-Aplicada"	 					 
Autor: Marcos Herrera (CONICET-IELDE, UNSa, Argentina)
e-mail: mherreragomez@gmail.com
  
* Comandos para generar las siguientes acciones:

1. Análisis exploratorio de datos espaciales:  
	- Representación por medio de Mapas.
*/
	
global DATA = "/Users/federica/Documents/MAESTRÍA/2ºtrimestre/herramientas computacionales/clase 4/videos 2 y 3/data" 
cd "$DATA"

********************************************************************************************
/* 					  INSTALACIÓN DE LOS PAQUETES NECESARIOS    						  */
********************************************************************************************

ssc install spmap
ssc install shp2dta
*net install sg162, from(http://www.stata.com/stb/stb60)
*net install st0292, from(http://www.stata-journal.com/software/sj13-2)
net install spwmatrix, from(http://fmwww.bc.edu/RePEc/bocode/s)
*net install splagvar, from(http://fmwww.bc.edu/RePEc/bocode/s)
*ssc install xsmle.pkg
*ssc install xtcsd
*net install st0446.pkg

************************************************************************************
************************************************************************************
/*            CHAPTER 2: ANÁLISIS EXPLORATORIO DE DATOS ESPACIALES  		   	  */
************************************************************************************
************************************************************************************

************************************************************************************
/*                      (1) LECTURA Y MAPAS DE DATOS  	  		                  */
************************************************************************************

* Leer la información shape en Stata

shp2dta using london_sport.shp, database(ls) coord(coord_ls) genc(c) genid(id) replace

/* El comando anterior genera dos nuevos archivos: datos_shp.dta y coord.dta
El primero contiene los atributos (variables) del shape. 
El segundo contiene la información sobre la formas geográficas. 
Se generan en el archivo de datos tres variables:
id: identifica a la región. 
c: genera el centroide por medio de las variables: x_c: longitud, y_c: latitud
*/

use ls, clear
describe

use coord_ls, clear
describe
*base que tiene ID, x e y para cada polígono 

*Vamos a juntar las dos bases de datos

/* Importamos y transformamos los datos de Excel a formato Stata */
import delimited "$DATA/mps-recordedcrime-borough.csv", clear 
* Nos quedamos con los datos de robos:
keep if crimetype=="Theft & Handling"
* En Stata necesitamos que la variable tenga el mismo nombre en ambas bases para juntarlas
rename borough name
* preserve
collapse (sum) crimecount, by(name)
*sumo por barrios la cantidad de crímenes
save "crime.dta", replace

describe

/* Uniremos ambas bases: london_sport y crime. Su usa la función merge con la variable name que se encuentra en ambas bases  */

use ls, clear
merge 1:1 name using crime.dta
*unimos las bases por el nombre, pero lo ideal sería hacer merge con código identificador
*merge 1:1 name using crime.dta, keep(3) nogen
keep if _m==3
drop _m

save london_crime_shp.dta, replace

************************************************************************************
* Representación por medio de mapas

use london_crime_shp.dta, clear

* Mapa de cuantiles:
*en STATA 15, el comando spmap cambió a grmap (https://www.statalist.org/forums/forum/general-stata-discussion/general/1431518-spmap-option-la-not-allowed)
*spmap crimecount using coord_ls, id(id) clmethod(q) cln(6)
gen thefts_per=crimecount/Pop_2001*1000
*Para que la variable quede con dos decimales:
 format (thefts_per) %12.2f
 *mapa:
grmap thefts_per using coord_ls, id(id) clmethod(q) cln(6) title("Robos per cápita") legend(size(small) position(5) xoffset(17.5)) fcolor(Purples) plotregion(margin(b+15)) ndfcolor(gray) name(g2,replace) note("Mapa de Londres")  

