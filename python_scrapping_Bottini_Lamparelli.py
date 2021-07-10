

import os
os.chdir("C:/Users/Cristel/Desktop/Carolina/Herramientas computacionales/Clase 3/Stata")

from wwo_hist import retrieve_hist_data

# Elegimos la frecuencia de los datos
# Elegimos las fechas
# Api: en el website (https://www.worldweatheronline.com/developer/premium-api-explorer.aspx)
# Location: de donde queremos sacar los datos
frequency=12
frequency=24
start_date = '1-JAN-2015'
end_date = '31-DEC-2015'
api_key = '26098d8245194cc7842233300211206'

# Obtenemos estos zipcodes de stata:
location_list = ['20625','20650','20688','20742','20876','21040','21043','21158','21214','21220','21411','21502','21536','21638','21639','21643','21650','21653','21703','21748','21802','21811','21853','21914']

hist_weather_data = retrieve_hist_data(api_key,
                                location_list,
                                start_date,
                                end_date,
                                frequency,
                                location_label = False,
                                export_csv = True,
                                store_df = True)


