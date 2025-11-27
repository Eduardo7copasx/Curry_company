
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import streamlit as st
import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

def clean_code (df1):

    """Esta funcao tem a responsabilidade de limpar o dataframe

Tipos de limpeza:
1. Removação dos dados NaN
2. Mudança do tipo da coluna de dados
3. Remoção dos espaços das variáveis de texto
4. Formatação da coluna de datas
5. Limpeza da coluna de tempo (remoção do texto da variável numérica )
    
    """

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(str).str.strip()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(str).str.strip()


    linhas_selecionadas = df1.loc[:, 'Delivery_person_Age'] != 'NaN'
    linhas_selecionadas2 = df1.loc[:, 'multiple_deliveries'] != 'NaN'
    linhas_selecionadas3 = df1.loc[:, 'City'] != 'NaN'

    df1 = df1.loc[linhas_selecionadas, :]
    df1 = df1.loc[linhas_selecionadas2, :]
    df1 = df1.loc[linhas_selecionadas3, :]

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).str.replace('(min) ', '', regex=False)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    return df1

df = pd.read_csv( 'dataset/train.csv')
df1 = clean_code (df)

#------------------------------------------cria o grafico de barras dos pedidos por dia--------------------------------------------------------------
def order_metric(df1):
    cols = ['ID', 'Order_Date']
    aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()   
    fig = px.bar(aux, x='Order_Date', y='ID')
    return fig
#------------------------------------------cria o grafico de pizza dos pedidos por tipo de trafego---------------------------------------------------------------
def pedidos(df1):
    cols = ['ID', 'Road_traffic_density']
    aux3 = df1.loc[:, cols].groupby('Road_traffic_density').count().reset_index()
    aux3 = aux3.loc[aux3['Road_traffic_density'] != 'NaN', :]
    aux3['percent'] = aux3['ID'] / aux3['ID'].sum()
    import plotly.express as px
    fig = px.pie(aux3, values = 'percent', names = 'Road_traffic_density')
    return fig
#------------------------------------------cria o grafico espalhado dos pedidos por cidade e tipo de trafego---------------------------------------------------------------
def pedidos_cidades(df1):
    cols = ['ID', 'City', 'Road_traffic_density']
    aux4 = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
    aux4 = aux4.loc[aux4['City'] != 'NaN', :]
    aux4 = aux4.loc[aux4['Road_traffic_density'] != 'NaN', :]
    fig = px.scatter(aux4, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig
#------------------------------------------cria o grafico de linha dos pedidos por semana---------------------------------------------------------------
def pedidos_semana(df1):
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    cols = ['ID', 'Week_of_year']
    aux2 = df1.loc[:, cols].groupby('Week_of_year').count().reset_index()
    fig = px.line(aux2, x='Week_of_year', y='ID')
    return fig
#------------------------------------------cria o grafico de linha dos pedidos por entregador e por semana---------------------------------------------------------------
def pedidos_entregador(df1):
    aux5 = df1.loc[:, ['ID', 'Week_of_year']].groupby('Week_of_year').count().reset_index()
    aux6 = df1.loc[:, ['Delivery_person_ID', 'Week_of_year']].groupby('Week_of_year').nunique().reset_index()
    auxpd = pd.merge(aux5, aux6, how='inner')
    auxpd ['Delivery_person_week'] = auxpd ['ID'] / auxpd ['Delivery_person_ID']
    fig = px.line(auxpd, x='Week_of_year', y='Delivery_person_week')
    return fig
#------------------------------------------cria o mapa---------------------------------------------------------------
def mapa_pais(df1):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']]).add_to(map)
    folium_static (map, width=1024, height=600)
#---------------------------------------------------------------------------------------------------------
#visao_empresa

#===============================
#Barra lateral
#===============================

st.header('Marketplace - Visão Cliente' )

#image_path = 'Logo.jpeg'
image = Image.open('Logo.jpeg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company' )
st.sidebar.markdown('## Fastest Delivery in Town' )

st.sidebar.markdown ("""---""" )

st.sidebar.markdown('## Selecione uma data limite' )

value_date = pd.to_datetime("2022-4-13").to_pydatetime()
min_date   = pd.to_datetime("2022-2-11").to_pydatetime()
max_date   = pd.to_datetime("2022-4-6").to_pydatetime()

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=value_date,
    min_value=min_date,
    max_value=max_date,
    format='DD-MM-YYYY'
)

st.sidebar.markdown ("""---""" )

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito', 
    ['Low', 'Medium', 'High', 'Jam'], 
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown ("""---""" )
st.sidebar.markdown('### Powered by Comunidade DS' )

linhas_selecionadas = df1 ['Order_Date'] < date_slider
df1 = df1.loc [linhas_selecionadas, :]

linhas_selecionadas = df1 ['Road_traffic_density'].isin ( traffic_options)
df1 = df1.loc [linhas_selecionadas, :]

#===============================
#Layout
#===============================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('# Pedidos por dia')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)        

    with st.container():
        coll, col2 = st.columns(2)
        with coll:
            st.header('Pedidos por tipo de trafego' )
            fig = pedidos(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.header('Pedidos por cidade e tipo de trafego')
            fig = pedidos_cidades(df1)
            st.plotly_chart(fig, use_container_width=True)            

#============================
#tatica 
#============================
with tab2:
    with st.container():
        st.header('Pedidos por semana')
        fig = pedidos_semana(df1)
        st.plotly_chart(fig, use_container_width=True)

        
    with st.container():
        st.header('Pedidos por entregador  e por semana')
        fig = pedidos_entregador(df1)
        st.plotly_chart(fig, use_container_width=True)     

#============================
#geografica 
#============================

with tab3:
    st.markdown('Mapa do país')
    mapa_pais(df1)


