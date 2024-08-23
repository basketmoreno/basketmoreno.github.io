import time
import folium
from folium import plugins
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from tqdm import tqdm

# Ruta al archivo Excel
file_path = 'Proyecto vlak/lista_destinos.xlsx'

# Cargar el archivo Excel que contiene los destinos en la hoja "destinos"
data = pd.read_excel(file_path, sheet_name='destinos')

# Extraer las estaciones de origen de las columnas en la hoja 'destinos'
estaciones_origen = data.columns.tolist()

# Inicializar el geolocalizador con un user agent único
geolocator = Nominatim(user_agent="mi_aplicacion_geolocalizacion")

# Crear una lista para almacenar los resultados
resultados = []

# Asignacion de colores para las 6 estaciones de origen principales
colores_estaciones = {
    "MADRID-ATOCHA": "lightblue",      
    "MADRID-PRINCIPE PIO": "lightgreen", 
    "BARCELONA-SANTS": "darkred",    
    "SANTIAGO DE COMPOSTELA": "purple", 
    "VALENCIA-NORD": "orange",    
    "SEVILLA-SANTA JUSTA": "beige"  
}

# Coordenadas fijas para estaciones que no se encontraron previamente
destinos_con_error = {
    "ALMURADIEL-VISO DEL MARQU": (38.5846, -3.5217),
    "MADRID-CHAMARTÍN-CLARA CA": (40.4723, -3.6883),
    "MADRID-NUEVOS MINISTERIOS": (40.4475, -3.6939),
    "MENGÍBAR-ARTICHUELA (APD-": (37.9725, -3.8001),
    "FAIÓ-LA POBLA DE MASSALUC": (41.2241, 0.5448),
    "CAUDIEL (APT)": (39.8733, -0.5746),
    "JÉRICA-VIVER (APT)": (39.9062, -0.6203),
    "CÁDIZ-ESTADIO": (36.5086, -6.2789),
    "MADRID - ATOCHA CERCANÍAS": (40.4067, -3.6904),
    "SEVILLA-VIRGEN DEL ROCÍO": (37.3591, -5.9735)
    "EL CHORRO": (36.9047, -4.7576),
    "GENOVÉS": (38.9796, -0.4478)
}

# Función para obtener coordenadas
def obtener_coordenadas(destino):
    try:
        location = geolocator.geocode(destino + ", Spain", timeout=10)
        time.sleep(1)  # Esperar 1 segundo entre solicitudes
        if location:
            return (location.latitude, location.longitude)
        else:
            print(f"Coordenadas no encontradas para {destino}")
            return (None, None)
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Error obteniendo coordenadas para {destino}: {e}")
        return (None, None)

# Crear un mapa centrado en España
mapa = folium.Map(location=[40.416775, -3.703790], zoom_start=6)

# Procesar estaciones de origen con barra de progreso externa
for estacion in estaciones_origen:
    destinos = data[estacion].dropna().tolist()  # Obtener la lista de destinos sin NaN
    
    # Crear una barra de progreso para los destinos dentro de la estación
    with tqdm(total=len(destinos), desc=f"Procesando {estacion}", ncols=100) as pbar:
        for destino in destinos:
            if destino in destinos_con_error:
                # Usar las coordenadas fijas del diccionario
                lat, lon = destinos_con_error[destino]
            else:
                # Obtener las coordenadas del destino usando la función
                lat, lon = obtener_coordenadas(destino)
            
            # Agregar el resultado a la lista de resultados
            resultados.append({"Estación de Origen": estacion, "Destino": destino, "Latitud": lat, "Longitud": lon})
            
            # Actualizar la barra de progreso para cada destino procesado
            pbar.update(1)

# Añadir marcadores para cada destino (sin barra de progreso interna)
for resultado in resultados:
    if resultado['Latitud'] is not None and resultado['Longitud'] is not None:
        # Determinar el color del marcador basado en la estación de origen
        estacion_origen = resultado['Estación de Origen']
        color = colores_estaciones.get(estacion_origen)
        folium.Marker(
            location=[resultado['Latitud'], resultado['Longitud']],
            popup=resultado['Destino'],
            icon=folium.Icon(color=color),
        ).add_to(mapa)

# Crear el contenido HTML de la leyenda (colores con HEX de Folium)
# https://www.kaggle.com/code/aungdev/colors-available-for-marker-icons-in-folium

legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 300px; height: 230px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white; opacity: 0.85;
                padding: 10px;">
        <b>Estaciones de Origen</b><br>
        <i class="fa fa-map-marker fa-2x" style="color:#ADD8E6"></i> MADRID-ATOCHA<br> <!-- lightblue -->
        <i class="fa fa-map-marker fa-2x" style="color:#90EE90"></i> MADRID-PRINCIPE PIO<br> <!-- lightgreen -->
        <i class="fa fa-map-marker fa-2x" style="color:#8B0000"></i> BARCELONA-SANTS<br> <!-- darkred -->
        <i class="fa fa-map-marker fa-2x" style="color:#800080"></i> SANTIAGO DE COMPOSTELA<br> <!-- purple -->
        <i class="fa fa-map-marker fa-2x" style="color:#FFA500"></i> VALENCIA-NORD<br> <!-- orange -->
        <i class="fa fa-map-marker fa-2x" style="color:#F5F5DC"></i> SEVILLA-SANTA JUSTA<br> <!-- beige -->
    </div>
'''

# Añadir la leyenda al mapa
mapa.get_root().html.add_child(folium.Element(legend_html))

# Guardar el mapa en un archivo HTML
mapa.save("Proyecto vlak/mapa-renfe.html")
