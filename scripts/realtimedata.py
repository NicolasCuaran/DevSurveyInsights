import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Función para obtener datos de la API
def fetch_data():
    try:
        response = requests.get("http://localhost:8000/data")
        response.raise_for_status()
        data = response.json()
        logging.info(f"Datos obtenidos de la API: {len(data)} registros")
        return data
    except requests.RequestException as e:
        logging.error(f"Error al obtener datos de la API: {e}")
        return []

# Layout de la aplicación Dash
app.layout = html.Div([
    html.H1("Visualización de Datos de Encuesta Kafka", style={'textAlign': 'center'}),
    html.H3("Promedio de Calificaciones (Excluyendo valores 99)", style={'textAlign': 'center'}),
    dcc.Graph(id='average-ratings-bar'),
    html.H3("Distribución de Salarios (Excluyendo 0.0)", style={'textAlign': 'center'}),
    dcc.Graph(id='salary-histogram'),
    html.H3("Distribución de Calificaciones (Box Plot)", style={'textAlign': 'center'}),
    dcc.Graph(id='ratings-box'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Actualizar cada 5 segundos
        n_intervals=0
    )
])

# Callback para actualizar los gráficos
@app.callback(
    [
        Output('average-ratings-bar', 'figure'),
        Output('salary-histogram', 'figure'),
        Output('ratings-box', 'figure')
    ],
    Input('interval-component', 'n_intervals')
)
def update_graphs(n_intervals):
    # Obtener datos
    data = fetch_data()
    
    if not data:
        logging.warning("No hay datos disponibles para graficar")
        empty_fig = {
            'data': [],
            'layout': {'title': 'No hay datos disponibles'}
        }
        return empty_fig, empty_fig, empty_fig

    # Convertir a DataFrame
    df = pd.DataFrame(data)
    
    if df.empty:
        logging.warning("DataFrame vacío después de convertir los datos")
        empty_fig = {
            'data': [],
            'layout': {'title': 'No hay datos disponibles'}
        }
        return empty_fig, empty_fig, empty_fig

    # Filtrar valores 99 para las columnas de calificaciones
    rating_columns = [
        'Benefit_SalaryBonuses', 'Benefit_RetirementPlan',
        'Importance_Industry', 'Importance_RemoteWork', 'Importance_Technologies'
    ]
    df_filtered = df[rating_columns].replace(99, pd.NA)
    
    # 1. Bar Chart: Promedio de calificaciones
    averages = df_filtered.mean().reset_index()
    averages.columns = ['Metric', 'Average']
    bar_fig = px.bar(
        averages,
        x='Metric',
        y='Average',
        title='Promedio de Calificaciones',
        labels={'Metric': 'Métrica', 'Average': 'Promedio'},
        color='Metric',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    bar_fig.update_layout(
        xaxis_title="Métrica",
        yaxis_title="Promedio",
        template="plotly_white",
        showlegend=False
    )

    # 2. Histogram: Distribución de salarios (excluyendo 0.0)
    salary_df = df[df['StandardizedMonthlySalaryCOP'] > 0][['StandardizedMonthlySalaryCOP']]
    if not salary_df.empty:
        hist_fig = px.histogram(
            salary_df,
            x='StandardizedMonthlySalaryCOP',
            title='Distribución de Salarios Mensuales (COP)',
            labels={'StandardizedMonthlySalaryCOP': 'Salario Mensual (COP)'},
            nbins=10,
            color_discrete_sequence=['#636EFA']
        )
        hist_fig.update_layout(
            xaxis_title="Salario Mensual (COP)",
            yaxis_title="Frecuencia",
            template="plotly_white"
        )
    else:
        hist_fig = {
            'data': [],
            'layout': {'title': 'No hay datos de salario válidos (todos son 0.0)'}
        }

    # 3. Box Plot: Distribución de calificaciones
    box_fig = go.Figure()
    for col in rating_columns:
        box_fig.add_trace(
            go.Box(
                y=df_filtered[col].dropna(),
                name=col,
                boxpoints='outliers',
                jitter=0.3,
                marker_color=px.colors.qualitative.Plotly[rating_columns.index(col) % len(px.colors.qualitative.Plotly)]
            )
        )
    box_fig.update_layout(
        title='Distribución de Calificaciones',
        yaxis_title='Valor',
        xaxis_title='Métrica',
        template="plotly_white",
        showlegend=True
    )

    return bar_fig, hist_fig, box_fig

# Punto de entrada principal
if __name__ == '__main__':
    logging.info("Iniciando la aplicación Dash...")
    app.run(debug=True, host='0.0.0.0', port=8050)