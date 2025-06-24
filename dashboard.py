import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# Configuração da página para usar o layout largo
st.set_page_config(layout="wide")

# Título do painel
st.title('Painel de Análise de Ocorrências - SCSP')

# Usamos cache para carregar os dados apenas uma vez, melhorando a performance
@st.cache_data
def carregar_dados():
    # Carrega o CSV usando ';' como separador
    df = pd.read_csv('planilha_ocorrencias_tratadas_as_csv.csv', sep=';', encoding='utf-8')
    
    # Converte as colunas de data e hora para o formato datetime
    # Juntamos a data e a hora em uma única coluna para facilitar a análise temporal
    df['data_hora_ocorrencia'] = pd.to_datetime(
        df['Data da Ocorrência'] + ' ' + df['Hora da ocorrência'], 
        format='%d/%m/%Y %H:%M:%S',
        errors='coerce' # Se houver erro na conversão, o valor se torna NaT (Not a Time)
    )
    
    # Remove linhas onde a conversão de data/hora falhou
    df.dropna(subset=['data_hora_ocorrencia'], inplace=True)
    
    return df

# Carrega os dados
df_ocorrencias = carregar_dados()

# --- BARRA LATERAL COM FILTROS ---
st.sidebar.header("Filtros")

# Obter data mínima e máxima do conjunto de dados
min_date = df_ocorrencias['data_hora_ocorrencia'].min().date()
max_date = df_ocorrencias['data_hora_ocorrencia'].max().date()

# Filtro de data na barra lateral
data_inicio = st.sidebar.date_input("Data de Início", min_date, min_value=min_date, max_value=max_date)
data_fim = st.sidebar.date_input("Data de Fim", max_date, min_value=min_date, max_value=max_date)

# Converter datas para datetime para comparação
data_inicio_dt = pd.to_datetime(data_inicio)
data_fim_dt = pd.to_datetime(data_fim) + pd.Timedelta(days=1) # Adiciona 1 dia para incluir o dia final

# Validação das datas
if data_inicio > data_fim:
    st.sidebar.error("A data de início não pode ser posterior à data de fim.")
    st.stop()

# Filtrar o dataframe com base no período selecionado
df_filtrado = df_ocorrencias[
    (df_ocorrencias['data_hora_ocorrencia'] >= data_inicio_dt) & 
    (df_ocorrencias['data_hora_ocorrencia'] < data_fim_dt)
]

# Adiciona o resumo com as métricas (usando o df_filtrado)
st.subheader("Resumo do Período")
col1, col2 = st.columns(2)

total_ocorrencias_filtrado = len(df_filtrado)
col1.metric("Total de Ocorrências no Período", total_ocorrencias_filtrado)

total_cameras_filtrado = df_filtrado['Identificador_da_camera_mesclado'].nunique()
col2.metric("Total de Câmeras no Período", total_cameras_filtrado)

st.divider() # Adiciona uma linha divisória para separar o resumo dos gráficos

# --- GRÁFICOS ---
st.subheader("Análises Gráficas do Período")

# Verifica se há dados para exibir nos gráficos
if not df_filtrado.empty:
    col1_graf, col2_graf = st.columns(2)

    with col1_graf:
        # Gráfico 1: Ocorrências por Hora do Dia (Visual Melhorado)
        st.markdown("##### Ocorrências por Hora do Dia")
        df_filtrado['hora'] = df_filtrado['data_hora_ocorrencia'].dt.hour
        ocorrencias_por_hora = df_filtrado['hora'].value_counts().sort_index()
        ocorrencias_por_hora = ocorrencias_por_hora.reindex(range(24), fill_value=0)

        fig_bar = px.bar(
            x=ocorrencias_por_hora.index,
            y=ocorrencias_por_hora.values,
            labels={'x': 'Hora do Dia', 'y': 'Nº de Ocorrências'},
            text=ocorrencias_por_hora.values,
            color_discrete_sequence=['#0083B8'] # Define uma cor azul padrão
        )
        fig_bar.update_traces(
            texttemplate='%{text}', 
            textposition='outside',
            hovertemplate='<b>Hora %{x}h</b>: %{y} ocorrências<extra></extra>'
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', # Fundo transparente
            xaxis=dict(showgrid=False, dtick=1), # Garante que todos os ticks do eixo X sejam mostrados
            yaxis=dict(showgrid=False, visible=False), # Esconde o eixo Y
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2_graf:
        # Gráfico 2: Distribuição por Tipo de Ocorrência (Visual Melhorado)
        st.markdown("##### Distribuição por Tipo de Ocorrência")
        ocorrencias_por_tipo = df_filtrado['Tipo da ocorrência'].value_counts()

        fig_donut = px.pie(
            values=ocorrencias_por_tipo.values,
            names=ocorrencias_por_tipo.index,
            hole=0.4, # Aumenta o "buraco" para um visual mais moderno
            color_discrete_sequence=px.colors.sequential.Blues_r # Paleta de cores em tons de azul
        )
        fig_donut.update_traces(
            textposition='outside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b>: %{value} (%{percent})<extra></extra>'
        )
        fig_donut.update_layout(
            height=400, # Define uma altura fixa para o gráfico
            showlegend=False,
            margin=dict(t=100, b=100, l=10, r=10) # Aumenta a margem para evitar que os rótulos cortem
        )
        st.plotly_chart(fig_donut, use_container_width=True)

else:
    st.warning("Não há dados para exibir para o período selecionado.")


# Exibe o dataframe filtrado em um bloco expansível para verificação
with st.expander("Visualizar dados brutos do período"):
    st.dataframe(df_filtrado)
