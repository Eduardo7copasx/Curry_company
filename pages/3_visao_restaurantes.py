from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import streamlit as st
import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np

st.set_page_config(page_title='Visão Restaurantes', page_icon='🧑‍🍳', layout='wide')


def clean_code(df1):

    # Remover “NaN” que são strings
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].str.strip()
    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
    df1['City'] = df1['City'].str.strip()
    df1['Festival'] = df1['Festival'].str.strip()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].str.strip()

    # Filtros corretos 1D
    df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN', :]
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN', :]
    df1 = df1.loc[df1['City'] != 'NaN', :]
    df1 = df1.loc[df1['Festival'] != 'NaN', :]
    df1 = df1.loc[df1['multiple_deliveries'] != 'NaN', :]

    # Conversões
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Limpeza tempo
    df1['Time_taken(min)'] = (
        df1['Time_taken(min)']
        .astype(str)
        .str.replace('(min) ', '', regex=False)
        .astype(int)
    )

    # Strip final
    df1['ID'] = df1['ID'].str.strip()
    df1['Delivery_person_ID'] = df1['Delivery_person_ID'].str.strip()
    df1['Type_of_order'] = df1['Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()

    # Semana
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    return df1

df = pd.read_csv( 'dataset/train.csv')
df1 = clean_code (df)

#----------------------------------retorna a Distância média do restaurante para os pontos de entrega-----------------------------------------------------------------------
def distancia_media_entrega(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1 ['Distance'] = df1.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1)
    distancia_media = np.round(df1.loc[:,'Distance'].mean(),2)
    col2.metric("",distancia_media)
#----------------------------------retorna o Tempo médio de entrega com festival-----------------------------------------------------------------------
def avg_entrega_festival(df1):
    aux8 = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg( {'Time_taken(min)' : ['mean', 'std']}).reset_index() 
    aux8.columns = ['Festival', 'Media', 'Desvio_padrao']           
    aux8 = np.round(aux8.loc[aux8['Festival'] == 'Yes', 'Media'].iloc[0],2)
    col3.metric("", aux8) 
#---------------------------------retorna o Desvio padrão de entrega com festival------------------------------------------------------------------------
def std_entrega_festival(df1):
    aux8 = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg( {'Time_taken(min)' : ['mean', 'std']}).reset_index() 
    aux8.columns = ['Festival', 'Media', 'Desvio_padrao']           
    aux8 = np.round(aux8.loc[aux8['Festival'] == 'Yes', 'Desvio_padrao'].iloc[0],2)
    col4.metric("", aux8)
#---------------------------------retorna o Tempo médio de entrega sem festival------------------------------------------------------------------------
def avg_entrega_semfestival(df1):
    aux8 = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg( {'Time_taken(min)' : ['mean', 'std']}).reset_index() 
    aux8.columns = ['Festival', 'Media', 'Desvio_padrao']           
    aux8 = np.round(aux8.loc[aux8['Festival'] == 'No', 'Media'].iloc[0],2)
    col5.metric("", aux8)
#---------------------------------retorna o Desvio padrão de entrega sem festival------------------------------------------------------------------------
def std_entrega_semfestival(df1):
    aux8 = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg( {'Time_taken(min)' : ['mean', 'std']}).reset_index() 
    aux8.columns = ['Festival', 'Media', 'Desvio_padrao']           
    aux8 = np.round(aux8.loc[aux8['Festival'] == 'No', 'Desvio_padrao'].iloc[0],2)
    col6.metric("", aux8)
#--------------------------------retorna o grafico de barras com Tempo médio e o desvio padrão por cidade-------------------------------------------------------------------------
def avg_std_cidade(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby( 'City').agg({'Time_taken(min)': ['mean', 'std']})            
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
                         
    fig.update_layout (barmode='group')
    return fig
#--------------------------------retorna o grafico de pizza com o tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego-------------------------------------------------------------------------
def avg_std_cidade_trafego(df1):   
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density'] ).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    return fig
#---------------------------------retorna o grafico de pizza com o Tempo médio de entrega por cidade------------------------------------------------------------------------
def avg_entrega_cidade(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1 ['Distance'] = df1.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1)
    distancia_media = df1.loc[:,['City', 'Distance']].groupby('City').mean().reset_index()
    fig = go.Figure( data= [go.Pie(labels=distancia_media['City'], values=distancia_media['Distance'], pull=[0,0.1,0])])
    return fig
#---------------------------------retorna um dataframe com os tipos de pedidos, tempo medio e desvio padrao de entrega e cidade------------------------------------------------------------------------
def distribuicao_distancia(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']].groupby ( ['City', 'Type_of_order'] ).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['Média', 'Desvio Padrão']
    df_aux = df_aux.reset_index()
    st.dataframe(df_aux)
#---------------------------------------------------------------------------------------------------------

#visao_empresa

#===============================
#Barra lateral
#===============================

st.header('Marketplace - Visão Restaurantes' )

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

#===================
#layout
#===================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("metricas")

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown('###### Quantidade de entregadores únicos')
            aux1 = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric("", aux1)

        with col2:
            st.markdown('###### Distância média do restaurante para os pontos de entrega')
            distancia_media_entrega(df1)

        with col3:
            st.markdown('###### Tempo médio de entrega com festival')
            avg_entrega_festival(df1)           
            
        with col4:
            st.markdown('###### Desvio padrão de entrega com festival')
            std_entrega_festival(df1)
            
        with col5:
            st.markdown('###### Tempo médio de entrega sem festival')
            avg_entrega_semfestival(df1)

        with col6:
            st.markdown('###### Desvio padrão de entrega sem festival')
            std_entrega_semfestival(df1)

    
    with st.container():
            st.markdown('##### Tempo médio e o desvio padrão por cidade')
            fig = avg_std_cidade(df1)
            st.plotly_chart(fig)         

    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do tempo')

        col1, col2= st.columns(2)

        with col1:
            st.markdown('##### O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego')
            fig = avg_std_cidade_trafego(df1)
            st.plotly_chart(fig)    

        with col2:
            st.markdown('##### Tempo médio de entrega por cidade')
            fig = avg_entrega_cidade(df1)
            st.plotly_chart(fig)

    with st.container(): 
        st.markdown("""---""")  
        st.title('Distribuição da distância') 
        distribuicao_distancia(df1)



