import pandas as pd
import networkx as nx
import tkinter as tk
from tkinter import messagebox, StringVar, OptionMenu, Entry, Label
import folium
from folium.plugins import MarkerCluster
import webbrowser
from geopy.distance import geodesic
import googlemaps
import polyline
import heapq as hq
import math

gmaps = googlemaps.Client(key='AIzaSyA8nGVVg5uAs2RACNJ7m7CjPT9ycV9-1eg')

def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

def dijkstra(G, source):
    n = len(G.nodes)
    visited = {node: False for node in G.nodes}
    path = {node: None for node in G.nodes}
    cost = {node: math.inf for node in G.nodes}

    cost[source] = 0
    pqueue = [(0, source)]
    while pqueue:
        g, u = hq.heappop(pqueue)
        if not visited[u]:
            visited[u] = True
            for v in G.neighbors(u):
                if not visited[v]:
                    f = g + G[u][v]['weight']
                    if f < cost[v]:
                        cost[v] = f
                        path[v] = u
                        hq.heappush(pqueue, (f, v))

    return path, cost

def load_data():
    try:
        file_path = 'dataset/estaciones_reducido.csv'
        df = pd.read_csv(file_path)
        print(f"Archivo cargado: {file_path}")
        print(df.head())  
        process_data(df)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar el archivo: {e}")
        print(f"Error al cargar el archivo: {e}")

def process_data(df):
    global G, stations, start_station_var, end_station_var, start_station_menu, end_station_menu
    try:
        required_columns = ['Station Name', 'Latitude', 'Longitude']
        if not all(column in df.columns for column in required_columns):
            raise ValueError(f"El archivo CSV debe contener las columnas: {', '.join(required_columns)}")

        G = nx.Graph()

        for idx, row in df.iterrows():
            G.add_node(row['Station Name'], pos=(row['Latitude'], row['Longitude']))

        for i, row1 in df.iterrows():
            for j, row2 in df.iterrows():
                if i != j:
                    distance = calculate_distance(row1['Latitude'], row1['Longitude'], row2['Latitude'], row2['Longitude'])
                    G.add_edge(row1['Station Name'], row2['Station Name'], weight=distance)

        stations = df['Station Name'].tolist()
        start_station_var.set(stations[0])
        end_station_var.set(stations[0])
        start_station_menu['menu'].delete(0, 'end')
        end_station_menu['menu'].delete(0, 'end')
        for name in stations:
            start_station_menu['menu'].add_command(label=name, command=tk._setit(start_station_var, name))
            end_station_menu['menu'].add_command(label=name, command=tk._setit(end_station_var, name))

        show_map()
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar los datos: {e}")
        print(f"Error al procesar los datos: {e}")

def show_map():
    try:
        avg_lat = sum([G.nodes[node]['pos'][0] for node in G.nodes]) / len(G.nodes)
        avg_lon = sum([G.nodes[node]['pos'][1] for node in G.nodes]) / len(G.nodes)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)

        marker_cluster = MarkerCluster().add_to(m)

        for node in G.nodes:
            folium.Marker(
                location=[G.nodes[node]['pos'][0], G.nodes[node]['pos'][1]],
                popup=node,
            ).add_to(marker_cluster)

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

        path, cost = dijkstra(G, start_station)
        base_path = []
        current_node = end_station
        while current_node is not None:
            base_path.insert(0, current_node)
            current_node = path[current_node]
        base_distance = cost[end_station]

        intermediate_stations = []
        if num_intermediate_stations > 0:
            segment_length = base_distance / (num_intermediate_stations + 1)
            accumulated_distance = 0
            for i in range(len(base_path) - 1):
                current_node = base_path[i]
                next_node = base_path[i + 1]
                edge_distance = cost[next_node] - cost[current_node]

                while len(intermediate_stations) < num_intermediate_stations and accumulated_distance + edge_distance >= (len(intermediate_stations) + 1) * segment_length:
                    target_distance = (len(intermediate_stations) + 1) * segment_length
                    overshoot_distance = target_distance - accumulated_distance
                    intermediate_node = min(
                        G.nodes,
                        key=lambda node: abs(cost[node] - (cost[current_node] + overshoot_distance))
                    )
                    intermediate_stations.append(intermediate_node)

                accumulated_distance += edge_distance

        final_path = [start_station] + intermediate_stations + [end_station]

        total_distance = sum(
            cost[final_path[i + 1]] - cost[final_path[i]]
            for i in range(len(final_path) - 1)
        )

        if total_distance > base_distance * 1.1:
            messagebox.showwarning(
                "Advertencia",
                f"El camino con escalas es significativamente más largo ({total_distance:.2f} km vs {base_distance:.2f} km)."
            )

        directions_result = gmaps.directions(
            (G.nodes[start_station]['pos'][0], G.nodes[start_station]['pos'][1]),
            (G.nodes[end_station]['pos'][0], G.nodes[end_station]['pos'][1]),
            waypoints=[(G.nodes[node]['pos'][0], G.nodes[node]['pos'][1]) for node in final_path[1:-1]],
            mode="driving"
        )

        route_points = []
        for leg in directions_result[0]['legs']:
            for step in leg['steps']:
                points = polyline.decode(step['polyline']['points'])
                route_points.extend(points)

        avg_lat = sum([G.nodes[node]['pos'][0] for node in G.nodes]) / len(G.nodes)
        avg_lon = sum([G.nodes[node]['pos'][1] for node in G.nodes]) / len(G.nodes)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)

        marker_cluster = MarkerCluster().add_to(m)

        for node in G.nodes:
            folium.Marker(
                location=[G.nodes[node]['pos'][0], G.nodes[node]['pos'][1]],
                popup=node,
            ).add_to(marker_cluster)

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

        for node in intermediate_stations:
            folium.Marker(
                location=[G.nodes[node]['pos'][0], G.nodes[node]['pos'][1]],
                popup=node,
                icon=folium.Icon(color='orange')
            ).add_to(m)

        folium.PolyLine(route_points, color="blue", weight=5, opacity=0.7).add_to(m)

        # Agregar un marcador con la distancia total
        distance_popup = folium.Popup(f"Distancia total: {total_distance:.2f} km", max_width=300)
        folium.Marker(
            location=[avg_lat, avg_lon],
            popup=distance_popup,
            icon=folium.DivIcon(html=f"""
                <div style="background-color: white; color: black; padding: 5px; border-radius: 5px;">
                    Distancia total: {total_distance:.2f} km
                </div>
            """)
        ).add_to(m)

        m.save('shortest_path_map.html')
        webbrowser.open('shortest_path_map.html')

        # Actualizar la etiqueta de distancia
        distance_label.config(text=f"Distancia total: {total_distance:.2f} km")

    except Exception as e:
        messagebox.showerror("Error", f"Error al encontrar el camino más corto: {e}")
        print(f"Error al encontrar el camino más corto: {e}")

def setup_tkinter(root):
    global start_station_var, end_station_var, num_intermediate_stations_var, start_station_menu, end_station_menu, distance_label

    # Configuración de la ventana de Tkinter
    root.title("AcomplePower - Camino Más Corto")
    window_width, window_height = 900, 600
    root.geometry(f"{window_width}x{window_height}")

    # Crear un canvas para el fondo
    canvas = tk.Canvas(root, width=window_width, height=window_height)
    canvas.pack(fill="both", expand=True)

    # Crear un degradado de azul a negro
    def draw_gradient(canvas, width, height):
        for i in range(height):
            color = f'#{int(0):02x}{int(0):02x}{int(255 * (1 - i / height)):02x}'
            canvas.create_line(0, i, width, i, fill=color)

    draw_gradient(canvas, window_width, window_height)

    # Configurar estilo de fuente
    font_style = ("Helvetica", 14)
    title_font = ("Helvetica", 20, "bold")

    # Crear y posicionar elementos de la interfaz
    title_label = Label(root, text="AcomplePower", font=title_font, fg="white", bg="black")
    canvas.create_window(window_width // 2, 40, window=title_label)

    load_button = tk.Button(root, text="Iniciar dataset", font=font_style, bg="gray", fg="white", command=load_data)
    canvas.create_window(window_width // 2, 100, window=load_button)

    start_station_var = StringVar(root)
    end_station_var = StringVar(root)
    num_intermediate_stations_var = StringVar(root)

    start_station_menu = OptionMenu(root, start_station_var, "")
    start_station_menu.config(font=font_style, bg="gray", fg="white")
    canvas.create_window(window_width // 2, 160, window=start_station_menu)

    end_station_menu = OptionMenu(root, end_station_var, "")
    end_station_menu.config(font=font_style, bg="gray", fg="white")
    canvas.create_window(window_width // 2, 220, window=end_station_menu)

    num_intermediate_stations_label = tk.Label(root, text="Número de Estaciones Intermedias:", font=font_style, fg="white", bg="black")
    canvas.create_window(window_width // 2, 280, window=num_intermediate_stations_label)

    num_intermediate_stations_entry = Entry(root, textvariable=num_intermediate_stations_var, font=font_style)
    canvas.create_window(window_width // 2, 340, window=num_intermediate_stations_entry)

    find_path_button = tk.Button(root, text="Encontrar Camino Más Corto", font=font_style, bg="gray", fg="white", command=find_shortest_path)
    canvas.create_window(window_width // 2, 400, window=find_path_button)

    distance_label = Label(root, text="Distancia total: 0 km", font=font_style, fg="white", bg="black")
    canvas.create_window(window_width // 2, 460, window=distance_label)

    # Mantener la ventana centrada y consistente
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (window_width // 2) - 10  # Mover 50 píxeles a la izquierda
    y = (root.winfo_screenheight() // 2) - (window_height // 2) - 30 # Mover 50 píxeles hacia arriba
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Inicializar la interfaz de Tkinter
if __name__ == "__main__":
    root = tk.Tk()
    setup_tkinter(root)
    root.mainloop()