import pandas as pd
import networkx as nx
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, OptionMenu, Entry
import folium
from folium.plugins import MarkerCluster
import webbrowser
from geopy.distance import geodesic
import googlemaps
import polyline

# Reemplaza 'YOUR_API_KEY' con tu clave de API de Google Maps
gmaps = googlemaps.Client(key='AIzaSyA8nGVVg5uAs2RACNJ7m7CjPT9ycV9-1eg')

# Función para calcular la distancia en km entre dos estaciones a partir de sus coordenadas geográficas
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

def load_data():
    try:
        file_path = filedialog.askopenfilename(title="Selecciona tu archivo de dataset", filetypes=[("Archivos CSV", "*.csv")])
        if not file_path:
            messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo.")
            return
        df = pd.read_csv(file_path)
        print(f"Archivo cargado: {file_path}")
        print(df.head())  # Mostrar las primeras filas del DataFrame para depuración
        process_data(df)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar el archivo: {e}")
        print(f"Error al cargar el archivo: {e}")

def process_data(df):
    global G, stations
    try:
        # Verificar que el DataFrame tenga las columnas necesarias
        required_columns = ['Station Name', 'Latitude', 'Longitude']
        if not all(column in df.columns for column in required_columns):
            raise ValueError(f"El archivo CSV debe contener las columnas: {', '.join(required_columns)}")

        # Crear el grafo
        G = nx.Graph()

        # Agregar nodos al grafo
        for idx, row in df.iterrows():
            G.add_node(row['Station Name'], pos=(row['Latitude'], row['Longitude']))

        # Agregar aristas con la distancia como peso
        for i, row1 in df.iterrows():
            for j, row2 in df.iterrows():
                if i != j:
                    distance = calculate_distance(row1['Latitude'], row1['Longitude'], row2['Latitude'], row2['Longitude'])
                    G.add_edge(row1['Station Name'], row2['Station Name'], weight=distance)

        # Actualizar las opciones de las estaciones en los menús desplegables
        stations = df['Station Name'].tolist()
        start_station_var.set(stations[0])
        end_station_var.set(stations[0])
        start_station_menu['menu'].delete(0, 'end')
        end_station_menu['menu'].delete(0, 'end')
        for name in stations:
            start_station_menu['menu'].add_command(label=name, command=tk._setit(start_station_var, name))
            end_station_menu['menu'].add_command(label=name, command=tk._setit(end_station_var, name))

        # Visualizar el grafo en un mapa interactivo
        show_map()
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar los datos: {e}")
        print(f"Error al procesar los datos: {e}")

def show_map():
    try:
        # Crear un mapa centrado en el promedio de las coordenadas
        avg_lat = sum([G.nodes[node]['pos'][0] for node in G.nodes]) / len(G.nodes)
        avg_lon = sum([G.nodes[node]['pos'][1] for node in G.nodes]) / len(G.nodes)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)

        # Crear un clúster de marcadores
        marker_cluster = MarkerCluster().add_to(m)

        # Agregar marcadores al mapa
        for node in G.nodes:
            folium.Marker(
                location=[G.nodes[node]['pos'][0], G.nodes[node]['pos'][1]],
                popup=node,
            ).add_to(marker_cluster)

        # Guardar el mapa en un archivo HTML y abrirlo en el navegador
        m.save('map.html')
        webbrowser.open('map.html')
    except Exception as e:
        messagebox.showerror("Error", f"Error al mostrar el mapa: {e}")
        print(f"Error al mostrar el mapa: {e}")

def find_shortest_path():
    try:
        start_station = start_station_var.get()
        end_station = end_station_var.get()
        num_intermediate_stations = int(num_intermediate_stations_var.get())

        if start_station not in G.nodes or end_station not in G.nodes:
            messagebox.showerror("Error", "Una o ambas estaciones no existen en el grafo.")
            return

        # Calcular el camino más corto entre inicio y fin
        base_path = nx.dijkstra_path(G, source=start_station, target=end_station, weight='weight')
        base_distance = nx.dijkstra_path_length(G, source=start_station, target=end_station, weight='weight')

        # Si no se requieren estaciones intermedias, usamos directamente el camino más corto
        if num_intermediate_stations == 0:
            path = base_path
        else:
            # Dividir el trayecto base en segmentos proporcionales al número de paradas
            segment_length = base_distance / (num_intermediate_stations + 1)

            # Lista para las estaciones intermedias
            intermediate_stations = []

            accumulated_distance = 0
            for i in range(len(base_path) - 1):
                current_node = base_path[i]
                next_node = base_path[i + 1]
                edge_distance = nx.dijkstra_path_length(G, source=current_node, target=next_node, weight='weight')

                while len(intermediate_stations) < num_intermediate_stations and accumulated_distance + edge_distance >= len(intermediate_stations) * segment_length:
                    target_distance = len(intermediate_stations) * segment_length
                    overshoot_distance = target_distance - accumulated_distance
                    # Buscar un nodo cercano a la posición ideal dentro del segmento
                    intermediate_node = min(
                        G.nodes,
                        key=lambda node: abs(
                            nx.dijkstra_path_length(G, source=current_node, target=node, weight='weight') - overshoot_distance
                        )
                    )
                    intermediate_stations.append(intermediate_node)

                accumulated_distance += edge_distance

            # Crear el camino final con estaciones intermedias
            path = [start_station] + intermediate_stations + [end_station]

        # Calcular la distancia total del nuevo camino
        total_distance = sum(
            nx.dijkstra_path_length(G, source=path[i], target=path[i + 1], weight='weight')
            for i in range(len(path) - 1)
        )

        # Validar que la nueva distancia no sea excesiva
        if total_distance > base_distance * 1.1:
            messagebox.showwarning(
                "Advertencia",
                f"El camino con escalas es significativamente más largo ({total_distance:.2f} km vs {base_distance:.2f} km)."
            )

        # Obtener la ruta real usando Google Maps API
        directions_result = gmaps.directions(
            (G.nodes[start_station]['pos'][0], G.nodes[start_station]['pos'][1]),
            (G.nodes[end_station]['pos'][0], G.nodes[end_station]['pos'][1]),
            waypoints=[(G.nodes[node]['pos'][0], G.nodes[node]['pos'][1]) for node in path[1:-1]],
            mode="driving"
        )

        # Extraer los puntos de la ruta
        route_points = []
        for leg in directions_result[0]['legs']:
            for step in leg['steps']:
                points = polyline.decode(step['polyline']['points'])
                route_points.extend(points)

        # Crear un mapa centrado en el promedio de las coordenadas
        avg_lat = sum([G.nodes[node]['pos'][0] for node in G.nodes]) / len(G.nodes)
        avg_lon = sum([G.nodes[node]['pos'][1] for node in G.nodes]) / len(G.nodes)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)

        # Crear un clúster de marcadores
        marker_cluster = MarkerCluster().add_to(m)

        # Agregar marcadores al mapa
        for node in G.nodes:
            folium.Marker(
                location=[G.nodes[node]['pos'][0], G.nodes[node]['pos'][1]],
                popup=node,
            ).add_to(marker_cluster)

        # Resaltar las estaciones de inicio y fin
        folium.Marker(
            location=[G.nodes[start_station]['pos'][0], G.nodes[start_station]['pos'][1]],
            popup=start_station,
            icon=folium.Icon(color='green')
        ).add_to(m)
        folium.Marker(
            location=[G.nodes[end_station]['pos'][0], G.nodes[end_station]['pos'][1]],
            popup=end_station,
            icon=folium.Icon(color='red')
        ).add_to(m)

        # Dibujar el camino más corto
        folium.PolyLine(route_points, color="blue", weight=5, opacity=0.7).add_to(m)

        # Guardar el mapa en un archivo HTML y abrirlo en el navegador
        m.save('shortest_path_map.html')
        webbrowser.open('shortest_path_map.html')

    except Exception as e:
        messagebox.showerror("Error", f"Error al encontrar el camino más corto: {e}")
        print(f"Error al encontrar el camino más corto: {e}")



        
# Crear la ventana principal
root = tk.Tk()
root.title("Cargar Base de Datos")

# Crear el botón para cargar el archivo
load_button = tk.Button(root, text="Cargar Base de Datos", command=load_data)
load_button.pack(pady=20)

# Variables para las estaciones de inicio y fin
start_station_var = StringVar(root)
end_station_var = StringVar(root)
num_intermediate_stations_var = StringVar(root)

# Menús desplegables para seleccionar las estaciones
start_station_menu = OptionMenu(root, start_station_var, "")
start_station_menu.pack(pady=10)
end_station_menu = OptionMenu(root, end_station_var, "")
end_station_menu.pack(pady=10)

# Entrada para el número de estaciones intermedias
num_intermediate_stations_label = tk.Label(root, text="Número de Estaciones Intermedias:")
num_intermediate_stations_label.pack(pady=10)
num_intermediate_stations_entry = Entry(root, textvariable=num_intermediate_stations_var)
num_intermediate_stations_entry.pack(pady=10)

# Botón para encontrar el camino más corto
find_path_button = tk.Button(root, text="Encontrar Camino Más Corto", command=find_shortest_path)
find_path_button.pack(pady=20)

# Ejecutar la aplicación
root.mainloop()