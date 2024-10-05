import plotly.graph_objs as go
import networkx as nx
import pandas as pd
import random
from dash import Dash, dcc, html, Input, Output

# Cargar el dataset desde un archivo CSV
data = pd.read_csv('src/bd.csv')

# Crear un grafo vacío
G = nx.Graph()

# Añadir nodos con la combinación de Región, Tipo de Cultivo y Año
for idx, row in data.iterrows():
    node_name = f"{row['Region']} - {row['Crop_Type']} - {row['Year']}"
    G.add_node(node_name, **row.to_dict())  # Agregamos el nodo con los atributos de ese nodo

# Añadir aristas basadas en diferencias entre nodos
for i in range(len(data)):
    node_i = f"{data.iloc[i]['Region']} - {data.iloc[i]['Crop_Type']} - {data.iloc[i]['Year']}"
    connected_nodes = set()
    
    # Conectar al menos a un nodo cercano
    if i + 1 < len(data):
        node_j = f"{data.iloc[i + 1]['Region']} - {data.iloc[i + 1]['Crop_Type']} - {data.iloc[i + 1]['Year']}"
        G.add_edge(node_i, node_j, weight=1.0)  # Peso arbitrario para asegurar la conexión
        connected_nodes.add(node_j)
    
    # Añadir conexiones adicionales de manera aleatoria
    available_nodes = list(range(i + 2, len(data)))
    num_connections = min(4, len(available_nodes))
    if num_connections > 0:
        for j in random.sample(available_nodes, num_connections):  # Limitar las conexiones a nodos aleatorios cercanos
            node_j = f"{data.iloc[j]['Region']} - {data.iloc[j]['Crop_Type']} - {data.iloc[j]['Year']}"
            
            # Evitar duplicar conexiones
            if node_j in connected_nodes:
                continue
            
            # Calcular la diferencia entre los nodos
            temp_diff = abs(data.iloc[i]['Average_Temperature_C'] - data.iloc[j]['Average_Temperature_C'])
            precip_diff = abs(data.iloc[i]['Total_Precipitation_mm'] - data.iloc[j]['Total_Precipitation_mm'])
            extreme_diff = abs(data.iloc[i]['Extreme_Weather_Events'] - data.iloc[j]['Extreme_Weather_Events'])
            
            # Calcular el peso de las aristas
            irrigation_access = (data.iloc[i]['Irrigation_Access_%'] + data.iloc[j]['Irrigation_Access_%']) / 2
            pesticide_use = (data.iloc[i]['Pesticide_Use_KG_per_HA'] + data.iloc[j]['Pesticide_Use_KG_per_HA']) / 2
            fertilizer_use = (data.iloc[i]['Fertilizer_Use_KG_per_HA'] + data.iloc[j]['Fertilizer_Use_KG_per_HA']) / 2
            soil_health = (data.iloc[i]['Soil_Health_Index'] + data.iloc[j]['Soil_Health_Index']) / 2
            economic_impact = (data.iloc[i]['Economic_Impact_Million_USD'] + data.iloc[j]['Economic_Impact_Million_USD']) / 2
            
            # Peso de la arista (combinación ponderada de las variables)
            weight = (temp_diff + precip_diff + extreme_diff) - \
                     (irrigation_access * 0.1 + pesticide_use * 0.05 + fertilizer_use * 0.05 + soil_health * 10 + economic_impact * 0.001)
            
            # Añadir la arista con el peso calculado
            G.add_edge(node_i, node_j, weight=weight)
            connected_nodes.add(node_j)

# Crear la aplicación Dash
app = Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    dcc.Graph(id='graph', style={'height': '100vh'}),
    html.Button('Mostrar más nodos', id='button', n_clicks=0, style={
        'position': 'fixed',
        'top': '10px',
        'right': '10px',
        'zIndex': 1000
    })
])

# Callback para actualizar el gráfico
@app.callback(
    Output('graph', 'figure'),
    Input('button', 'n_clicks')
)
def update_graph(n_clicks):
    # Limitar la cantidad de nodos mostrados
    nodes_to_show = 500 * (n_clicks + 1)
    subgraph = G.subgraph(list(G.nodes)[:nodes_to_show])
    
    # Generar posiciones de los nodos con layout de fuerza
    pos = nx.spring_layout(subgraph, seed=42)
    
    # Extraer las coordenadas de las aristas
    edge_x = []
    edge_y = []
    for edge in subgraph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    
    # Trazar las aristas
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Extraer las coordenadas de los nodos
    node_x = []
    node_y = []
    node_color = []
    for node in subgraph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_color.append(subgraph.nodes[node]['Region'])  # Usar la región para determinar el color
    
    # Asignar colores únicos a cada región
    unique_regions = list(set(node_color))
    color_map = {region: i for i, region in enumerate(unique_regions)}
    node_color = [color_map[region] for region in node_color]
    
    # Trazar los nodos
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            color=node_color,
            size=10,
            colorbar=dict(
                thickness=15,
                title='Region',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))
    
    # Añadir información de hover a los nodos
    node_text = []
    for node in subgraph.nodes():
        info = subgraph.nodes[node]
        node_text.append(f"Region: {info['Region']}<br>Crop: {info['Crop_Type']}<br>Year: {info['Year']}")
    
    node_trace.text = node_text
    
    # Crear el gráfico final
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Grafo de Impacto Climático en la Agricultura',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=50),
                        annotations=[dict(
                            text="Grafo de nodos basados en datos climáticos y agrícolas",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False)))
    
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)