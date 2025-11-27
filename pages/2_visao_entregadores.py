from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import streamlit as st
import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')


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

#-----------------------------------------retorna a maior idade do entregador---------------------------------------------------------------
def entregador_velho(df1):
    aux1 = df1.loc[:,'Delivery_person_Age'].max()
    col1.metric("",aux1 )
#-----------------------------------------retorna a menor idade do entregador---------------------------------------------------------------
def entregador_novo(df1):
    aux2 = df1.loc[:,'Delivery_person_Age'].min()
    col2.metric("",aux2 )
#-----------------------------------------retorna a melhor condicao do veiculo---------------------------------------------------------------
def condicao_veiculo(df1):
    aux3 = df1.loc[:,'Vehicle_condition'].max()
    col3.metric("", aux3)
#-----------------------------------------retorna a pior condicao do veiculo---------------------------------------------------------------
def condicao_veiculo_min(df1):
    aux4 = df1.loc[:,'Vehicle_condition'].min()
    col4.metric("", aux4)
#-----------------------------------------retorna a avaliacao media por entregador em forma de dataframe---------------------------------------------------------------
def avaliacao_media(df1):
    aux5 = df1.loc[:,['Delivery_person_Ratings', 'Delivery_person_ID']].groupby(['Delivery_person_ID']).mean().reset_index()
    st.dataframe(aux5)
#------------------------------------------retorna a avaliacao media por transito--------------------------------------------------------------
def avg_transito(df1):
    aux6 = df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings' : ['mean', 'std']})
    aux6 = aux6.loc[aux6.index != 'NaN', :]
    aux6.columns = ['Média','Desvio padrão']
    st.dataframe(aux6)
#------------------------------------------retorna avaliacao media por clima--------------------------------------------------------------
def avg_clima(df1):
    aux7 = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings' : ['mean' , 'std']})
    aux7 = aux7.loc[aux7.index != 'conditions NaN', :]
    aux7.columns = ['Média','Desvio padrão']
    st.dataframe(aux7)
#--------------------------------------------retorna os 10 entregadores mais rapidos por cidade------------------------------------------------------------
def entregadores_rapido(df1):
    aux8 = df1.loc[:,['Time_taken(min)','Delivery_person_ID', 'City']].groupby(['Delivery_person_ID', 'City']).mean().sort_values( ['City', 'Time_taken(min)'], ascending=True).reset_index()
            
    me = aux8.loc[aux8['City']== 'Metropolitian', :].head(10)
    mi = aux8.loc[aux8['City']== 'Urban', :].head(10)
    mo = aux8.loc[aux8['City']== 'Semi-Urban', :].head(10)

    df2 = pd.concat([me, mi, mo]).reset_index(drop=True)
    st.dataframe(df2)
#-------------------------------------------retorna os 10 entregadores mais lentos por cidade-------------------------------------------------------------
def entregadores_lentos(df1):
    aux9 = df1.loc[:,['Time_taken(min)','Delivery_person_ID', 'City']].groupby(['Delivery_person_ID', 'City']).mean().sort_values( ['City', 'Time_taken(min)'], ascending=False).reset_index()

    me = aux9.loc[aux9['City']== 'Metropolitian', :].head(10)
    mi = aux9.loc[aux9['City']== 'Urban', :].head(10)
    mo = aux9.loc[aux9['City']== 'Semi-Urban', :].head(10)

    df3 = pd.concat([me, mi, mo]).reset_index(drop=True)
    st.dataframe(df3)

#visao_empresa

#===============================
#Barra lateral
#===============================

st.header('Marketplace - Visão Entregadores' )

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

#=================
#layout
#=================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Métricas gerais' )
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            st.markdown("##### Idade do entregador mais velho")
            entregador_velho(df1)

        with col2:
            st.markdown("##### Idade do entregador mais novo")
            entregador_novo(df1)

        with col3:
            st.markdown("##### Melhor condição dos veículos em estrelas")
            condicao_veiculo(df1)

        with col4:
            st.markdown("##### Pior condição dos veículos em estrelas")
            condicao_veiculo_min(df1)

    with st.container():
        st.markdown("""---""")
        st.title("Avaliações")

        col1,col2 = st.columns(2)
        with col1:
            st.markdown('Avaliação média por entregadores')
            avaliacao_media(df1)

        with col2:
            st.markdown("Avaliação média por trânsito")
            avg_transito(df1)

            st.markdown("Avaliação média por clima")
            avg_clima(df1)

    with st.container():
        st.markdown("""---""")
        st.title("Velocidade de entrega")

        col1,col2 = st.columns(2)
        with col1:
            st.subheader("Entregadores mais rápidos")
            entregadores_rapido(df1)

        with col2:
            st.subheader("Entregadores mais lentos")
            entregadores_lentos(df1)
