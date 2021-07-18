setwd("C:/Users/Cristel/Desktop/Carolina/Herramientas computacionales/Clase 4/videos 2 y 3")
install.packages(x) 
install.packages("ggmap")
install.packages("rgeos")
install.packages("maptools")
install.packages("dplyr")
install.packages("tidyr")
install.packages("tmap")
install.packages("rgdal")

x <- c("ggmap","rgdal" , "rgeos", "maptools", "dplyr", "tidyr", "tmap")
lapply(x, library, character.only = TRUE) # load the required packages
library(rgdal)
lnd <- readOGR(dsn = "data/london_sport.shp")
head(lnd@data, n = 10)
sapply(lnd@data, class)
lnd$Pop_2001 <- as.numeric(as.character(lnd$Pop_2001))
sapply(lnd@data, class)
lnd@proj4string

# Grafico poligonos: 
plot(lnd)  
lnd@proj4string
plot(lnd) 

# Merge
library(rgdal) 
lnd <- readOGR("data/london_sport.shp")
plot(lnd) 
nrow(lnd) 
crime_data <- read.csv("data/mps-recordedcrime-borough.csv",
                       stringsAsFactors = FALSE)

head(crime_data$CrimeType) # information about crime type
crime_theft <- crime_data[crime_data$CrimeType == "Theft & Handling", ]
crime_ag <- aggregate(CrimeCount ~ Borough, FUN = sum, data = crime_theft)
lnd$name %in% crime_ag$Borough
lnd$name[!lnd$name %in% crime_ag$Borough]
library(dplyr)
head(lnd$name,100) # observaciones --> dataset to add to 
head(crime_ag$Borough,100) # observaciones --> the variables to join
head(left_join(lnd@data, crime_ag)) # you will need "by"
lnd@data <- left_join(lnd@data, crime_ag, by = c('name' = 'Borough'))
head(lnd)

lnd$Pop_2001 <- as.integer(as.character(lnd$Pop_2001))
sapply(lnd@data, class)
lnd@proj4string

lnd$tpop <- lnd$CrimeCount / lnd$Pop_2001*1000

############## Creo mapa con qtm 
qtm(lnd, "tpop") # plot the basic map
qtm(shp = lnd, fill = "tpop", fill.palette = "Reds", fill.title = "")+ 
  tm_legend(legend.title.size=1,legend.text.size = 0.8,legend.position = c("right", "bottom"), main.title = "Robos (cada 1000 habitantes)", main.title.position = "left")+
  tm_credits("Mapa de Londres", position = "left")

############# Creo mapa con ggplot
library(ggplot2)
lnd_f <- broom::tidy(lnd)                                                                                                    
lnd$id <- row.names(lnd) # allocate an id variable to the sp data
head(lnd@data, n = 2) # final check before join (requires shared variable name)
lnd_f <- left_join(lnd_f, lnd@data) # join the data

map <- ggplot(lnd_f, aes(long, lat, group = group, fill = tpop)) +
  geom_polygon() + coord_equal() +
  labs(x = "Easting (m)", y = "Northing (m)",
       fill = "") +
  ggtitle("Robos en Londres", subtitle = "(cada 1000 habitantes)")
map2 <- map + scale_fill_gradient(low = "White", high = "Red")
map2



