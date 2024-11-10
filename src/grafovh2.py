import heapq
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename


# Función para construir el grafo basado en las regiones y cultivos
def build_graph(data):
    G = nx.Graph()
    for index, row in data.iterrows():
        region = row['Region']
        crop = row['Crop_Type']

        # En este caso, nos guiamos en las condiciones como temperatura y precipitación
        weight = abs(row['Average_Temperature_C']) + abs(row['Total_Precipitation_mm'] / 1000)

        # Añadir nodos y aristas
        G.add_edge(region, crop, weight=weight)

    return G


# Función para dibujar el grafo usando networkx y matplotlib
def draw_graph(G):
    pos = nx.spring_layout(G)  # Posiciones de los nodos para la visualización
    plt.figure(figsize=(12, 12))

    # Dibujar los nodos
    nx.draw_networkx_nodes(G, pos, node_size=50, node_color='skyblue')

    # Dibujar las aristas
    nx.draw_networkx_edges(G, pos, alpha=0.5)

    # Dibujar etiquetas de los nodos
    nx.draw_networkx_labels(G, pos, font_size=8, font_family="sans-serif")

    plt.title("Grafo Completo de Regiones y Cultivos (1500 nodos)")
    plt.show()


# Algoritmo de Dijkstra para encontrar el camino más corto
def dijkstra(G, start, target):
    queue = [(0, start)]
    distances = {node: float('infinity') for node in G.nodes}
    distances[start] = 0
    previous_nodes = {node: None for node in G.nodes}

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor in G.neighbors(current_node):
            weight = G[current_node][neighbor]['weight']
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    # Reconstruir el camino desde el nodo objetivo hasta el nodo de inicio
    path, current_node = [], target
    while previous_nodes[current_node] is not None:
        path.insert(0, current_node)
        current_node = previous_nodes[current_node]
    if path:
        path.insert(0, start)

    return path, distances[target]


# Ocultar la ventana principal de Tkinter
Tk().withdraw()

# Abrir el explorador de archivos para seleccionar el archivo
file_path = askopenfilename(title="Selecciona tu archivo de dataset", filetypes=[("Archivos CSV", "*.csv")])

# Cargar el dataset
if file_path:
    try:
        data = pd.read_csv(file_path)
        print(f"Archivo cargado exitosamente: {file_path}")
    except FileNotFoundError:
        print("Error: No se encontró el archivo en la ruta especificada.")
        exit()
else:
    print("No se seleccionó ningún archivo.")
    exit()

# Limitar el dataset para cumplir con los 1500 nodos (750 regiones y 750 cultivos)
data_filtered = data.head(1500)

# Construir el grafo con los primeros 1500 nodos
G = build_graph(data_filtered)

# Dibujar el grafo completo (grafo padre)
draw_graph(G)

# Aplicar el algoritmo de Dijkstra para encontrar el camino más corto
start_region = 'Victoria'  # Cambia por la región que te interese
target_crop = 'Sugarcane'  # Cambia por el cultivo que te interese
path, total_weight = dijkstra(G, start_region, target_crop)

# Mostrar el resultado del algoritmo de Dijkstra
print("Camino más corto:", path)
print("Peso total del camino:", total_weight)