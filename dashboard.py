import streamlit as st
import pandas as pd
from data_loader import carregar_dados
from plotting import plot_ranking_problemas ,plot_ocorrencias_por_hora_e_tipo, plot_distribuicao_tipo_ocorrencia

# --- CONFIGURAÇÃO DA PÁGINA E TÍTULO ---
st.set_page_config(layout="wide")
st.title('Painel de Análise de Ocorrências')

# --- CARREGAMENTO DE DADOS ---
# Carrega o DataFrame já processado e enriquecido
df_ocorrencias = carregar_dados()

# --- CAMADA DE AUTENTICAÇÃO POR SENHA ---
def check_password():
    """Retorna True se o usuário inseriu a senha correta."""
    
    # Usa st.session_state para manter o estado de login
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    # Se já estiver logado, não mostra o formulário de senha
    if st.session_state.password_correct:
        return True

    # Mostra o formulário de senha
    st.header("🔒 Acesso Restrito")
    password = st.text_input("Digite a senha para acessar o painel:", type="password")

    # Use uma senha mais segura no seu projeto real!
    # Idealmente, use st.secrets para armazenar a senha.
    if password == "eurico123":
        st.session_state.password_correct = True
        st.rerun() # Recarrega a página para mostrar o painel
    elif password != "":
        st.error("Senha incorreta.")
    
    return False

# Se a senha não for validada, interrompe a execução do restante do app
if not check_password():
    st.stop()

# --- BARRA LATERAL COM FILTROS ---
st.sidebar.header("Filtros")

# Começa com o DataFrame completo para a lógica de filtragem sequencial
df_filtrado = df_ocorrencias.copy()

# --- LÓGICA DE FILTROS DINÂMICOS ---

# 1. Filtro de Data (O primeiro da hierarquia)
min_date = df_ocorrencias['data_hora_ocorrencia'].min().date()
max_date = df_ocorrencias['data_hora_ocorrencia'].max().date()
data_inicio = st.sidebar.date_input("Data de Início", min_date, min_value=min_date, max_value=max_date)
data_fim = st.sidebar.date_input("Data de Fim", max_date, min_value=min_date, max_value=max_date)

if data_inicio > data_fim:
    st.sidebar.error("A data de início não pode ser posterior à data de fim.")
    st.stop()
else:
    data_inicio_dt = pd.to_datetime(data_inicio)
    data_fim_dt = pd.to_datetime(data_fim) + pd.Timedelta(days=1)
    df_filtrado = df_filtrado[
        (df_filtrado['data_hora_ocorrencia'] >= data_inicio_dt) & 
        (df_filtrado['data_hora_ocorrencia'] < data_fim_dt)
    ]

# 2. Filtro por Secretaria
# As opções são geradas a partir do df_filtrado (que já passou pelo filtro de data)
opcoes_secretaria = ['Todas'] + sorted(df_filtrado['secretaria'].dropna().unique().tolist())
secretaria_selecionada = st.sidebar.selectbox("Filtrar por Secretaria", options=opcoes_secretaria)
if secretaria_selecionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['secretaria'] == secretaria_selecionada]

# 3. Filtro por Regional
opcoes_regional = sorted(df_filtrado['Regional'].dropna().unique().tolist())
regional_selecionada = st.sidebar.multiselect("Filtrar por Regional", options=opcoes_regional, placeholder="Escolha uma Opção")
if regional_selecionada:
    df_filtrado = df_filtrado[df_filtrado['Regional'].isin(regional_selecionada)]

# 4. Filtro por Bairro
opcoes_bairro = sorted(df_filtrado['Bairro'].dropna().unique().tolist())
bairro_selecionado = st.sidebar.multiselect("Filtrar por Bairro", options=opcoes_bairro, placeholder="Escolha uma Opção")
if bairro_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Bairro'].isin(bairro_selecionado)]

# 5. Filtro por Código da Câmera
opcoes_camera = sorted(df_filtrado['id_camera_limpo'].dropna().unique().tolist())
camera_selecionada = st.sidebar.multiselect("Filtrar por Código da Câmera", options=opcoes_camera, placeholder="Escolha uma Opção")
if camera_selecionada:
    df_filtrado = df_filtrado[df_filtrado['id_camera_limpo'].isin(camera_selecionada)]

# 6. Filtro por Tipo de Ocorrência
opcoes_tipo_ocorrencia = sorted(df_filtrado['Tipo da ocorrência'].dropna().unique().tolist())
tipo_ocorrencia_selecionado = st.sidebar.multiselect("Filtrar por Tipo de Ocorrência", options=opcoes_tipo_ocorrencia, placeholder="Escolha uma Opção")
if tipo_ocorrencia_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Tipo da ocorrência'].isin(tipo_ocorrencia_selecionado)]

# 7. Filtro por Tipo de Problema
opcoes_problema = sorted(df_filtrado['problema_consolidado'].dropna().unique().tolist())
problema_selecionado = st.sidebar.multiselect("Filtrar por Tipo de Problema", options=opcoes_problema, placeholder="Escolha uma Opção")
if problema_selecionado:
    df_filtrado = df_filtrado[df_filtrado['problema_consolidado'].isin(problema_selecionado)]


# --- PAINEL PRINCIPAL ---
st.subheader("Resumo do Período Filtrado")
col1, col2 = st.columns(2)
col1.metric("Total de Ocorrências", len(df_filtrado))
col2.metric("Total de Câmeras Únicas", df_filtrado['id_camera_limpo'].nunique())

st.divider()

st.subheader("Análises Gráficas")
if not df_filtrado.empty:
    # --- LINHA SUPERIOR DE GRÁFICOS (LARGURA TOTAL) ---
    st.markdown("##### Ocorrências por Hora (detalhado por Tipo)")
    fig_line = plot_ocorrencias_por_hora_e_tipo(df_filtrado)
    st.plotly_chart(fig_line, use_container_width=True)

    # --- LINHA INFERIOR DE GRÁFICOS ---
    col1_graf, col2_graf = st.columns(2)
    with col1_graf:
        st.markdown("##### Distribuição por Tipo de Ocorrência")
        fig_donut = plot_distribuicao_tipo_ocorrencia(df_filtrado)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col2_graf:
        st.markdown("##### Ranking por Tipo de Problema")
        fig_ranking = plot_ranking_problemas(df_filtrado)
        st.plotly_chart(fig_ranking, use_container_width=True)

    st.divider()

    # --- TABELA: RESUMO POR CÂMERA ---
    st.subheader("Resumo por Câmera (Período Filtrado)")

    # Agrupa os dados filtrados para obter informações únicas por câmera
    df_resumo_camera = df_filtrado.groupby(
        ['id_camera_limpo', 'Nome Câmera', 'Regional', 'Bairro']
    ).agg(
        total_ocorrencias=('data_hora_ocorrencia', 'count')
    ).reset_index()

    # Renomeia as colunas para uma apresentação mais clara
    df_resumo_camera.rename(columns={
        'id_camera_limpo': 'Código da Câmera',
        'total_ocorrencias': 'Total de Ocorrências'
    }, inplace=True)

    # Ordena a tabela para mostrar as câmeras com mais ocorrências no topo
    df_resumo_camera = df_resumo_camera.sort_values(by='Total de Ocorrências', ascending=False)

    # Exibe a tabela interativa
    st.dataframe(
        df_resumo_camera,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Não há dados para exibir para os filtros selecionados.")

with st.expander("Visualizar dados brutos filtrados"):
    st.dataframe(df_filtrado)