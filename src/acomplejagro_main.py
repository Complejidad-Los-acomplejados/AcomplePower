import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import networkx as nx

# Variable global para el dataframe
df = pd.DataFrame()

# Función para cargar el archivo CSV
def cargar_datos():
    global df
    filepath = filedialog.askopenfilename(
        title="climate_change_impact_on_agriculture_2024.csv",
        filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*"))
    )
    if filepath:
        df = pd.read_csv(filepath)
        messagebox.showinfo("Éxito", f"Archivo {filepath} cargado correctamente.")
        print(df.head())  # Para verificar los datos cargados

# Función de Programación Dinámica para optimización de cultivos
def optimizar_cultivos(temperatura, precipitacion, region):
    global df
    # Filtrar el dataset para la región y extraer las variables necesarias
    df_region = df[df['Region'] == region]
    
    cultivos = df_region['Crop_Type'].unique()
    rendimiento = {}
    
    # Calcular el rendimiento estimado para cada tipo de cultivo
    for cultivo in cultivos:
        cultivo_data = df_region[df_region['Crop_Type'] == cultivo]
        avg_temp = cultivo_data['Average_Temperature_C'].mean()
        total_precip = cultivo_data['Total_Precipitation_mm'].mean()
        
        # Formula simple para estimar rendimiento (puedes ajustar según los datos)
        rendimiento[cultivo] = (0.5 * temperatura / avg_temp) + (0.5 * precipitacion / total_precip)
    
    cultivo_optimo = max(rendimiento, key=rendimiento.get)
    return cultivo_optimo, rendimiento[cultivo_optimo]

# Algoritmo de Bellman-Ford para calcular la distribución óptima de recursos
def calcular_recursos_optimos(grafo, nodo_inicio):
    distancias = nx.single_source_bellman_ford_path_length(grafo, nodo_inicio)
    return distancias

# Función para mostrar recomendaciones de cultivos
def mostrar_recomendaciones():
    if df.empty:
        messagebox.showerror("Error", "Primero cargue los datos desde el archivo CSV.")
        return
    
    try:
        temp = float(entry_temperatura.get())
        precip = float(entry_precipitacion.get())
        region = entry_region.get()
        
        cultivo, rendimiento = optimizar_cultivos(temp, precip, region)
        lbl_resultado_cultivo['text'] = f"Cultivo óptimo: {cultivo} (Rendimiento: {rendimiento:.2f})"
        
        # Crear el grafo de recursos
        G = nx.DiGraph()
        G.add_weighted_edges_from([
            ('Región A', 'Región B', 5),
            ('Región B', 'Región C', 3),
            ('Región A', 'Región C', 7),
            ('Región C', 'Región D', 2),
        ])
        
        recursos_optimos = calcular_recursos_optimos(G, 'Región A')
        lbl_resultado_recursos['text'] = f"Distribución óptima: {recursos_optimos}"
    except ValueError:
        messagebox.showerror("Error", "Ingrese valores válidos.")

# Diseño de la GUI
root = tk.Tk()
root.title("Sistema de Recomendación de Cultivos")
root.geometry("700x500")

# Etiqueta y botón para cargar el archivo CSV
ttk.Button(root, text="Cargar Datos CSV", command=cargar_datos).grid(row=0, column=0, columnspan=2, pady=10)

# Etiquetas y campos de entrada
ttk.Label(root, text="Temperatura (°C):").grid(row=1, column=0, padx=10, pady=10)
entry_temperatura = ttk.Entry(root)
entry_temperatura.grid(row=1, column=1, padx=10, pady=10)

ttk.Label(root, text="Precipitación (mm):").grid(row=2, column=0, padx=10, pady=10)
entry_precipitacion = ttk.Entry(root)
entry_precipitacion.grid(row=2, column=1, padx=10, pady=10)

ttk.Label(root, text="Región:").grid(row=3, column=0, padx=10, pady=10)
entry_region = ttk.Entry(root)
entry_region.grid(row=3, column=1, padx=10, pady=10)

# Botón para obtener recomendaciones
btn_recomendar = ttk.Button(root, text="Obtener Recomendación", command=mostrar_recomendaciones)
btn_recomendar.grid(row=4, column=0, columnspan=2, pady=20)

# Etiquetas de resultado
lbl_resultado_cultivo = ttk.Label(root, text="Cultivo óptimo:")
lbl_resultado_cultivo.grid(row=5, column=0, columnspan=2, pady=10)

lbl_resultado_recursos = ttk.Label(root, text="Distribución óptima:")
lbl_resultado_recursos.grid(row=6, column=0, columnspan=2, pady=10)

root.mainloop()
