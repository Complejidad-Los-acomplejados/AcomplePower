import pandas as pd
import networkx as nx
import pygame
import pygame_gui
import folium
from folium.plugins import MarkerCluster
import webbrowser
from geopy.distance import geodesic
import googlemaps
import polyline

from config.config import *

gmaps = googlemaps.Client(key='AIzaSyA8nGVVg5uAs2RACNJ7m7CjPT9ycV9-1eg')

# Variables globales
start_station_var = None
end_station_var = None
num_intermediate_stations_var = 0

def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

def load_data(manager):
    try:
        loading_message = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((350, 250), (200, 100)),
                                                             html_message='Cargando base de datos...',
                                                             manager=manager)
        pygame.display.update()
        file_path = 'dataset/estaciones_reducido.csv'
        df = pd.read_csv(file_path)
        print(f"Archivo cargado: {file_path}")
        print(df.head())  
        process_data(df)
        loading_message.kill()
        success_message = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((350, 250), (200, 100)),
                                                             html_message='Base de datos cargada con éxito.',
                                                             manager=manager)
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        error_message = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((350, 250), (200, 100)),
                                                           html_message=f'Error al cargar el archivo: {e}',
                                                           manager=manager)

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
        start_station_var = stations[0]
        end_station_var = stations[0]

        # Actualizar los menús de selección de estaciones
        start_station_menu.set_item_list(stations)
        end_station_menu.set_item_list(stations)

        show_map()
    except Exception as e:
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
        print(f"Error al mostrar el mapa: {e}")

distance_label = None

def find_shortest_path():
    try:
        start_station = start_station_var
        end_station = end_station_var
        num_intermediate_stations = int(num_intermediate_stations_var) + 1

        if start_station not in G.nodes or end_station not in G.nodes:
            print("Una o ambas estaciones no existen en el grafo.")
            return

        base_path = nx.dijkstra_path(G, source=start_station, target=end_station, weight='weight')
        base_distance = nx.dijkstra_path_length(G, source=start_station, target=end_station, weight='weight')

        if num_intermediate_stations == 0:
            path = base_path
        else:
            segment_length = base_distance / (num_intermediate_stations + 1)

            intermediate_stations = []

            accumulated_distance = 0
            for i in range(len(base_path) - 1):
                current_node = base_path[i]
                next_node = base_path[i + 1]
                edge_distance = nx.dijkstra_path_length(G, source=current_node, target=next_node, weight='weight')

                while len(intermediate_stations) < num_intermediate_stations and accumulated_distance + edge_distance >= len(intermediate_stations) * segment_length:
                    target_distance = len(intermediate_stations) * segment_length
                    overshoot_distance = target_distance - accumulated_distance
                    intermediate_node = min(
                        G.nodes,
                        key=lambda node: abs(
                            nx.dijkstra_path_length(G, source=current_node, target=node, weight='weight') - overshoot_distance
                        )
                    )
                    intermediate_stations.append(intermediate_node)

                accumulated_distance += edge_distance

            path = [start_station] + intermediate_stations + [end_station]

        total_distance = sum(
            nx.dijkstra_path_length(G, source=path[i], target=path[i + 1], weight='weight')
            for i in range(len(path) - 1)
        )

        if total_distance > base_distance * 1.1:
            print(f"El camino con escalas es significativamente más largo ({total_distance:.2f} km vs {base_distance:.2f} km).")

        directions_result = gmaps.directions(
            (G.nodes[start_station]['pos'][0], G.nodes[start_station]['pos'][1]),
            (G.nodes[end_station]['pos'][0], G.nodes[end_station]['pos'][1]),
            waypoints=[(G.nodes[node]['pos'][0], G.nodes[node]['pos'][1]) for node in path[1:-1]],
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

        m.save('shortest_path_map.html')
        webbrowser.open('shortest_path_map.html')

        if distance_label:
            distance_label.set_text(f"Distancia total: {total_distance:.2f} km")

    except Exception as e:
        print(f"Error al encontrar el camino más corto: {e}")

def set_start_station(option):
    global start_station_var
    start_station_var = option

def set_end_station(option):
    global end_station_var
    end_station_var = option

def set_num_intermediate_stations(text):
    global num_intermediate_stations_var
    num_intermediate_stations_var = text

def setup_pygame_ui(manager):
    global start_station_menu, end_station_menu, num_intermediate_stations_input, distance_label

    find_path_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 500), (200, 50)),
                                                    text='Encontrar Camino Más Corto',
                                                    manager=manager,
                                                    object_id='#find_path_button')

    start_station_menu = pygame_gui.elements.UIDropDownMenu(options_list=[],
                                                            starting_option='Seleccionar Estación de Inicio',
                                                            relative_rect=pygame.Rect((350, 250), (200, 50)),
                                                            manager=manager,
                                                            object_id='#start_station_menu')

    end_station_menu = pygame_gui.elements.UIDropDownMenu(options_list=[],
                                                          starting_option='Seleccionar Estación de Fin',
                                                          relative_rect=pygame.Rect((350, 350), (200, 50)),
                                                          manager=manager,
                                                          object_id='#end_station_menu')

    num_intermediate_stations_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 450), (200, 50)),
                                                                          manager=manager,
                                                                          object_id='#num_intermediate_stations_input')

    distance_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, 600), (200, 50)),
                                                 text='Distancia total: 0 km',
                                                 manager=manager,
                                                 object_id='#distance_label')

def main():
    pygame.init()
    pygame.display.set_caption('AcomplePower')
    window_surface = pygame.display.set_mode((900, 600))

    background = pygame.Surface((900, 600))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((900, 600))

    setup_pygame_ui(manager)

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_object_id == '#find_path_button':
                        find_shortest_path()

                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_object_id == '#start_station_menu':
                        set_start_station(event.text)
                    if event.ui_object_id == '#end_station_menu':
                        set_end_station(event.text)

                if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_object_id == '#num_intermediate_stations_input':
                        set_num_intermediate_stations(event.text)

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()

if __name__ == '__main__':
    main()