import pandas as pd
import networkx as nx
import tkinter as tk
from tkinter import messagebox, StringVar, ttk
import folium
from folium.plugins import MarkerCluster
import webbrowser
from geopy.distance import geodesic
import googlemaps
import polyline
import heapq as hq
import math
from PIL import Image, ImageTk

# Inicializa el cliente de Google Maps con una clave API válida
gmaps = googlemaps.Client(key='TU_CLAVE_API')

# Calcula la distancia en kilómetros entre dos coordenadas geográficas
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

# Implementa el algoritmo de Dijkstra para encontrar las rutas más cortas en un grafo
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

# Carga los datos desde un archivo CSV
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

# Procesa los datos del DataFrame y crea el grafo
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
        start_station_menu['values'] = stations
        end_station_menu['values'] = stations

        show_map()
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar los datos: {e}")
        print(f"Error al procesar los datos: {e}")

# Genera un mapa interactivo usando folium
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

# Encuentra la ruta más corta utilizando Dijkstra y la API de Google Maps
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

        total_distance = 0
        for i in range(len(final_path) - 1):
            segment_path, segment_cost = dijkstra(G, final_path[i])
            total_distance += segment_cost[final_path[i + 1]]

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

        distance_label.config(text=f"Distancia total: {total_distance:.2f} km")

    except Exception as e:
        messagebox.showerror("Error", f"Error al encontrar el camino más corto: {e}")
        print(f"Error al encontrar el camino más corto: {e}")

# Configura la interfaz gráfica con Tkinter
def setup_tkinter(root):
    global start_station_var, end_station_var, num_intermediate_stations_var, start_station_menu, end_station_menu, distance_label

    root.title("AcomplePower - Camino Más Corto")
    window_width, window_height = 900, 600
    root.geometry(f"{window_width}x{window_height}")

    background_image = Image.open("img/fondoaurora.jpg")
    background_photo = ImageTk.PhotoImage(background_image.resize((window_width, window_height)))
    background_label = tk.Label(root, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

    header = tk.Frame(root, bg="black", bd=0)
    header.place(relwidth=1, relheight=0.1)
    title_label = tk.Label(
        header,
        text="AcomplePower - Camino Más Corto",
        font=("Helvetica", 24, "bold"),
        bg="black",
        fg="white",
    )
    title_label.pack(pady=10)

    footer = tk.Frame(root, bg="black", bd=0)
    footer.place(relwidth=1, relx=0, rely=0.9)
    footer_label = tk.Label(
        footer,
        text="© 2024 AcomplePower",
        font=("Helvetica", 12),
        bg="black",
        fg="white",
    )
    footer_label.pack(pady=10)

    main_frame = tk.Frame(root, bg="black", bd=5)      
    main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.7)

    logo_image = Image.open("img/logoupcc.png")
    logo_photo = ImageTk.PhotoImage(logo_image.resize((50, 50)))
    logo_label = tk.Label(root, image=logo_photo, bg="black")
    logo_label.place(x=20, y=20)

    load_button = tk.Button(
        main_frame,
        text="Iniciar Dataset",
        font=("Helvetica", 14, "bold"),
        bg="#4CAF50",
        fg="white",
        activebackground="#45a049",
        command=load_data,
    )
    load_button.pack(pady=10)

    start_station_var = tk.StringVar(root)
    end_station_var = tk.StringVar(root)
    num_intermediate_stations_var = tk.StringVar(root)

    start_label = tk.Label(main_frame, text="Estación inicial:", font=("Helvetica", 14), bg="black", fg="white")
    start_label.pack(pady=5)
    start_station_menu = ttk.Combobox(main_frame, textvariable=start_station_var, state="readonly")
    start_station_menu.pack(pady=5)

    end_label = tk.Label(main_frame, text="Estación final:", font=("Helvetica", 14), bg="black", fg="white")
    end_label.pack(pady=5)
    end_station_menu = ttk.Combobox(main_frame, textvariable=end_station_var, state="readonly")
    end_station_menu.pack(pady=5)

    num_intermediate_stations_label = tk.Label(
        main_frame, text="Número de Estaciones Intermedias:", font=("Helvetica", 14), bg="black", fg="white"
    )
    num_intermediate_stations_label.pack(pady=5)
    num_intermediate_stations_entry = tk.Entry(main_frame, textvariable=num_intermediate_stations_var, font=("Helvetica", 14))
    num_intermediate_stations_entry.pack(pady=5)

    find_path_button = tk.Button(
        main_frame,
        text="Encontrar Camino Más Corto",
        font=("Helvetica", 14, "bold"),
        bg="#2196F3",
        fg="white",
        activebackground="#1e88e5",
        command=find_shortest_path,
    )
    find_path_button.pack(pady=10)

    distance_label = tk.Label(
        main_frame, text="Distancia total: 0 km", font=("Helvetica", 14), bg="black", fg="white"
    )
    distance_label.pack(pady=10)

    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (window_width // 2)
    y = (root.winfo_screenheight() // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.background_photo = background_photo
    root.logo_photo = logo_photo

if __name__ == "__main__":
    root = tk.Tk()
    setup_tkinter(root)
    root.mainloop()