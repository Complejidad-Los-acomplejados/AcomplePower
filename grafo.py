import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import folium
import tkinter as tk
from tkinter import filedialog


# Crear la ventana principal de tkinter
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal

# Abrir el cuadro de diálogo para seleccionar el archivo
print("Por favor, selecciona el archivo CSV.")
file_path = filedialog.askopenfilename(
    title="Seleccionar archivo CSV",
    filetypes=[("CSV files", "*.csv"), ("Todos los archivos", "*.*")]
)

# Verificar si se seleccionó un archivo
if not file_path:
    print("No se seleccionó ningún archivo. Saliendo del programa.")
else:
    try:
        # Leer el archivo seleccionado
        data = pd.read_csv(file_path)
        print(f"Archivo cargado correctamente: {file_path}")

        # Filtrar las columnas necesarias
        data = data[['Station Name', 'Latitude', 'Longitude']].dropna()

        # Limitar a 1500 nodos para evitar sobrecarga
        data = data.iloc[:1500]

        # Crear el grafo
        G = nx.Graph()

        # Agregar nodos al grafo
        for _, row in data.iterrows():
            G.add_node(row['Station Name'], pos=(row['Latitude'], row['Longitude']))

        # Agregar aristas basadas en distancia
        for i, row1 in data.iterrows():
            for j, row2 in data.iterrows():
                if i != j:  # Evitar loops
                    coord1 = (row1['Latitude'], row1['Longitude'])
                    coord2 = (row2['Latitude'], row2['Longitude'])
                    distance = geodesic(coord1, coord2).kilometers
                    if distance <= 50:  # Umbral de 50 km
                        G.add_edge(row1['Station Name'], row2['Station Name'], weight=distance)

        # Crear un mapa interactivo
        center = (data.iloc[0]['Latitude'], data.iloc[0]['Longitude'])
        map_grafo = folium.Map(location=center, zoom_start=6)

        # Agregar nodos al mapa
        for _, row in data.iterrows():
            folium.Marker(
                location=(row['Latitude'], row['Longitude']),
                popup=row['Station Name']
            ).add_to(map_grafo)

        # Crear un grupo de capas para las líneas del grafo
        line_group = folium.FeatureGroup(name="Líneas del Grafo", show=False)

        # Agregar aristas al grupo de capas
        for edge in G.edges(data=True):
            coord1 = G.nodes[edge[0]]['pos']
            coord2 = G.nodes[edge[1]]['pos']
            folium.PolyLine([coord1, coord2], color='blue', weight=1).add_to(line_group)

        # Añadir el grupo de líneas al mapa
        line_group.add_to(map_grafo)

        # Añadir control de capas para mostrar/ocultar líneas
        folium.LayerControl().add_to(map_grafo)

        # Guardar el mapa como archivo HTML
        map_file = "grafo_interactivo.html"
        map_grafo.save(map_file)

        print(f"Grafo interactivo guardado en: {map_file}")
        print("Abre el archivo HTML en tu navegador para visualizar el grafo.")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")