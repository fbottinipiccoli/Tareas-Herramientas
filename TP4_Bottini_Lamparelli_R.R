#Prior to use, install the following packages:
  install.packages("ggplot2")
install.packages("tibble")
install.packages("dplyr")
install.packages("gridExtra")
install.packages("Lock5Data")
install.packages("ggthemes")

install.packages("maps")
install.packages("mapproj")
install.packages("corrplot")
install.packages("fun")
install.packages("zoo")

#Used datafiles and sources:
  #a) gapminder.csv - Modified dataset from various datasets available at: https://www.gapminder.org/data/
  #b) xAPI-Edu-Data.csv: https://www.kaggle.com/aljarah/xAPI-Edu-Data/data
  #c) LoanStats.csv: Loan Data from Lending Tree - https://www.lendingclub.com/info/download-data.action
  #d) Lock5Data

#Load Libraries
library("ggplot2")
library("tibble")
library("gridExtra")
library("dplyr")
library("Lock5Data")
library("ggthemes")
library("fun")
library("zoo")
library("corrplot")
library("maps")
library("mapproj")

#Set pathname for the directory where you have data
setwd("~/Documents/MAESTRÍA/2ºtrimestre/herramientas computacionales/clase 4/video 1/Applied-Data-Visualization-with-R-and-ggplot2-master")
#Check working directory
getwd()

#Load the data files
df <- read.csv("data/gapminder-data.csv")
df2 <- read.csv("data/xAPI-Edu-Data.csv")
df3 <- read.csv("data/LoanStats.csv")

#1. GRÁFICO ORIGINAL DE CRÉDITOS
#Activity B:Using faceting to understand data
#"Aquí quiere ver la distribución de las cantidades de los préstamos para diferentes grados de crédito.
# Objetivo: Trazar el monto del préstamo para diferentes grados de crédito usando el faceting.
df3s <- subset(df3,grade %in% c("A","B","C","D","E","F","G"))
pb1<-ggplot(df3s,aes(x=loan_amnt))
pb1
pb2<-pb1+geom_histogram(bins=10,fill="cadetblue4")
pb2
#Facet_wrap
pb3<-pb2+facet_wrap(~grade) 
pb3
#Free y coordinate for the subplots
pb4<-pb3+facet_wrap(~grade, scale="free_y")
labs(title="Weight histogram plot",x="Weight(kg)", y = "Count")+
  theme_classic()
pb4

#GRÁFICO CORREGIDO DE CRÉDITOS
df3s <- subset(df3,grade %in% c("A","B","C","D","E","F","G"))
pb1<-ggplot(df3s,aes(x=loan_amnt, color=grade))
pb1
pb2<-pb1+geom_histogram(bins=10,fill="white")
pb2
#Facet_wrap
pb3<-pb2+facet_wrap(~grade) 
pb3
#Free y coordinate for the subplots
pb4<-pb3+facet_wrap(~grade, scale="free_y")
pb4
pb5<-pb4+theme_classic()+ggtitle("Cantidad de préstamos otorgados por categoría")
pb5
pb6<-pb5+theme(legend.position="none")
pb6
pb7<-pb6+labs(y= "", x = "Monto del préstamo ($)") 
pb7


#2. GRÁFICO ORIGINAL ELECTRICIDAD Y PBI 
#Exercise - Using color to group points by variable
dfs <- subset(df,Country %in% c("Germany","India","China","United States"))
var1<-"Electricity_consumption_per_capita"
var2<-"gdp_per_capita"
name1<- "Electricity/capita"
name2<- "GDP/capita"
# Change color and shape of points
p1<- ggplot(dfs,aes_string(x=var1,y=var2))+
  geom_point(color=2,shape=2)+xlim(0,10000)+xlab(name1)+ylab(name2)
p1
#Grouping points by a variable mapped to colour and shape
p2 <- ggplot(dfs,aes_string(x=var1,y=var2))+
  geom_point(aes(color=Country,shape=Country))+xlim(0,10000)+xlab(name1)+ylab(name2)
p2

#GRÁFICO CORREGIDO ELECTRICIDAD Y PBI 
dfs <- subset(df,Country %in% c("Germany","India","China","United States"))
var1<-"Electricity_consumption_per_capita"
var2<-"gdp_per_capita"
name1<- "Electricity/capita"
name2<- "GDP/capita"
# Change color and shape of points
p1<- ggplot(dfs,aes_string(x=var1,y=var2))+
  geom_point(color=2,shape=2)+xlim(0,10000)+xlab(name1)+ylab(name2)
p1
#Grouping points by a variable mapped to colour and shape
p2 <- ggplot(dfs,aes_string(x=var1,y=var2))+
  geom_point(aes(color=Country))+xlim(0,10000)+xlab(name1)+ylab(name2)
p2
p3<-p2+theme_classic()+ggtitle("Relación entre electricidad y gdp per cápita")
p3
p4<-p3+theme(legend.position="top")
p4
p5<-p4+labs(y= "GDP", x = "Electricidad") 
p5
p6<-p5+ theme(legend.title = element_blank())
p6

#3. GRÁFICO ORIGINAL BMI FEMALE VS MALE
# Objetivo: Trazar el IMC de hombres contra mujeres en diferentes países.
pd1 <- ggplot(df,aes(x=BMI_male,y=BMI_female))
pd2 <- pd1+geom_point()
pd2
pd3 <- pd1+geom_point(aes(color=Country),size=2)+
  scale_colour_brewer(palette="Dark2")
pd3
pd4 <- pd3+theme(axis.title=element_text(size=15,color="cadetblue4",
                                         face="bold"),
                 plot.title=element_text(color="cadetblue4",size=18,
                                         face="bold.italic"),
                 panel.background = element_rect(fill="azure",color="black"),
                 panel.grid=element_blank(),
                 legend.position="bottom",
                 legend.justification="left",
                 legend.title = element_blank(),
                 legend.key = element_rect(color=3,fill="gray97")
)+
  xlab("BMI Male")+
  ylab("BMI female")+
  ggtitle("BMI female vs BMI Male")
pd4

#GRÁFICO BMI CORREGIDO
pd1 <- ggplot(df,aes(x=BMI_male,y=BMI_female))
pd2 <- pd1+geom_point()
pd2
pd3 <- pd1+geom_point(aes(color=Country),size=1)+
  scale_colour_brewer(palette="Dark2")
pd4<-pd3+theme_classic()+ggtitle("Body Mass Index")
pd4
pd5<-pd4+theme(legend.position="top")
pd6<-pd5+labs(y= "female", x = "male") 
pd7<-pd6+ theme(legend.title = element_blank())
pd7
