import basedosdados as bd
import pandas as pd
import plotly.express as px
from flask import Flask, render_template
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html

# Carrega os dados
df = bd.read_table(dataset_id='br_inpe_prodes',
                   table_id='desmatamento_municipio',
                   billing_project_id="<YOUR_PROJECT_ID>")

# Inicializa o Flask
server = Flask(__name__)

# Cria o layout do Dash
app = Dash(__name__, server=server)
app.layout = html.Div([
    html.H1('Análise de Dados do Desmatamento dos Municípios Brasileiros'),
    html.Div([
        html.Div([
            dcc.Graph(id='mapa', figure={})
        ], className='col-md-6'),
        html.Div([
            dcc.Graph(id='barras', figure={})
        ], className='col-md-6')
    ], className='row'),
    html.Div([
        dcc.Graph(id='pizza', figure={})
    ], className='col-md-12')
])


# Cria a rota da página inicial
@server.route('/')
def index():
    return render_template('index.html', title='Home')


# Define as atualizações dos gráficos
@app.callback(
    [dash.dependencies.Output('mapa', 'figure'),
     dash.dependencies.Output('barras', 'figure'),
     dash.dependencies.Output('pizza', 'figure')],
    [dash.dependencies.Input('mapa', 'hoverData')])
def update_graph(hoverData):
    # Cria um mapa com a área desmatada por município
    mapa = px.choropleth(df, geojson='municipio_uf_geojson',
                         locations='nome_municipio',
                         color='area_km2',
                         color_continuous_scale='reds',
                         range_color=[0, df['area_km2'].max()],
                         labels={'area_km2': 'Área Desmatada (km²)'},
                         hover_name='nome_municipio')

    # Cria um gráfico de barras com a área desmatada por bioma
    barras = px.bar(df, x='bioma', y='area_km2',
                    labels={'area_km2': 'Área Desmatada (km²)'},
                    title='Área Desmatada por Bioma')

    # Cria um gráfico de pizza com a proporção de desmatamento por bioma
    pizza = px.pie(df.groupby('bioma')['area_km2'].sum().reset_index(),
                   values='area_km2', names='bioma',
                   labels={'area_km2': 'Área Desmatada (km²)'},
                   title='Proporção de Desmatamento por Bioma')

    return mapa, barras, pizza

if __name__ == '__main__':
    app.run_server(host="0.0.0.0")
