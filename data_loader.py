import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def carregar_dados():
    """
    Carrega os dados de ocorrências, realiza o pré-processamento, a limpeza
    e enriquece com informações de um cadastro de câmeras.
    """
    # --- 1. Carrega e processa os dados de OCORRÊNCIAS ---
    try:
        df_ocorrencias = pd.read_csv('planilha_ocorrencias_tratadas_as_csv.csv', sep=';', encoding='utf-8')
    except FileNotFoundError:
        st.error("Arquivo 'planilha_ocorrencias_tratadas_as_csv.csv' não encontrado.")
        return pd.DataFrame()

    # Conversão de data/hora
    df_ocorrencias['data_hora_ocorrencia'] = pd.to_datetime(
        df_ocorrencias['Data da Ocorrência'] + ' ' + df_ocorrencias['Hora da ocorrência'], 
        format='%d/%m/%Y %H:%M:%S',
        errors='coerce'
    )
    df_ocorrencias.dropna(subset=['data_hora_ocorrencia'], inplace=True)

    # Consolidação das colunas de problema
    cols_problema = ["Definição do problema", "Tipo do descarte", "tipo_do_problema_Mesclado"]
    for col in cols_problema:
        if col not in df_ocorrencias.columns:
            df_ocorrencias[col] = np.nan
    df_ocorrencias['problema_consolidado'] = df_ocorrencias[cols_problema[0]].fillna(df_ocorrencias[cols_problema[1]]).fillna(df_ocorrencias[cols_problema[2]])
    
    # Limpeza e criação de colunas derivadas
    id_camera_str = df_ocorrencias['Identificador_da_camera_mesclado'].astype(str)
    df_ocorrencias['id_camera_limpo'] = id_camera_str.str.replace(' ', '').str.split(':').str[-1]
    conditions = [
        df_ocorrencias['id_camera_limpo'].str.startswith('SG', na=False),
        df_ocorrencias['id_camera_limpo'].str.startswith('SCSP', na=False)
    ]
    choices = ['SG', 'SCSP']
    df_ocorrencias['secretaria'] = np.select(conditions, choices, default='Outros')

    # --- 2. Carrega e processa os dados das CÂMERAS ---
    try:
        df_cameras = pd.read_csv('Levantamento_Cameras_PMF - GERAL.csv', sep=',')
        colunas_interesse = ['Código', 'Qtd FIXA', 'Qtd PTZ', 'Regional', 'Bairro', 'Nome Câmera']
        df_cameras_info = df_cameras[colunas_interesse].copy()
        df_cameras_info.drop_duplicates(subset=['Código'], inplace=True)

        # --- 3. Junta (Merge) os dois DataFrames ---
        df_final = pd.merge(
            left=df_ocorrencias,
            right=df_cameras_info,
            left_on='id_camera_limpo',
            right_on='Código',
            how='left'
        )
        df_final.drop(columns=['Código'], inplace=True)

        # --- 4. Cria a coluna de Tipo de Câmera (PTZ/FIXA) ---
        # Define as condições com base nas colunas Qtd PTZ e Qtd FIXA. O valor 1 indica o tipo.
        conditions_camera_type = [
            df_final['Qtd PTZ'] == 1,
            df_final['Qtd FIXA'] == 1
        ]
        choices_camera_type = ['PTZ', 'FIXA']
        # Usa np.select para criar a nova coluna. Onde nenhuma condição é atendida, o valor é 'Indefinido'.
        df_final['tipo_camera'] = np.select(conditions_camera_type, choices_camera_type, default='Indefinido')

        return df_final

    except FileNotFoundError:
        st.warning("Arquivo 'Levantamento_Cameras_PMF - GERAL.csv' não encontrado. Os dados não serão enriquecidos.")
        # Se o arquivo de câmeras não for encontrado, cria a coluna 'tipo_camera' com valor padrão
        df_ocorrencias['tipo_camera'] = 'Indefinido'
        return df_ocorrencias