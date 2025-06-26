import plotly.express as px
import pandas as pd
import textwrap # Importa a biblioteca textwrap

def plot_ranking_problemas(df):
    """Gera um gráfico de barras vertical com o ranking de problemas."""
    problemas_counts = df['problema_consolidado'].dropna().value_counts().nlargest(15).sort_values(ascending=True)

    wrapped_labels = [
        '<br>'.join(textwrap.wrap(label, width=35)) for label in problemas_counts.index
    ]

    fig = px.bar(
        x=problemas_counts.values,
        y=wrapped_labels,
        orientation='h',
        labels={'x': 'Nº de Ocorrências', 'y': 'Tipo de Problema'},
        text=problemas_counts.values,
        color_discrete_sequence=['#0083B8']
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis={'categoryorder':'total ascending'},
        # --- AJUSTE PRINCIPAL: Aumenta a margem esquerda e a altura ---
        margin=dict(t=20, b=20, l=250, r=20), # Aumenta a margem esquerda para dar espaço aos rótulos
        height=500 # Aumenta a altura para evitar sobreposição vertical
    )
    return fig

def plot_distribuicao_tipo_ocorrencia(df):
    """Gera um gráfico de donut interativo da distribuição por tipo de ocorrência."""
    ocorrencias_por_tipo = df['Tipo da ocorrência'].value_counts()

    fig = px.pie(
        values=ocorrencias_por_tipo.values, names=ocorrencias_por_tipo.index,
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig.update_traces(
        textposition='outside', textinfo='percent+label',
        hovertemplate='<b>%{label}</b>: %{value} (%{percent})<extra></extra>'
    )
    fig.update_layout(
        height=400, showlegend=False,
        margin=dict(t=100, b=100, l=10, r=10)
    )
    return fig

def plot_ocorrencias_por_hora_e_tipo(df):
    """NOVA FUNÇÃO: Gera um gráfico de linhas de ocorrências por hora, com uma linha para cada tipo de ocorrência."""
    # Agrupa por hora e tipo de ocorrência para a legenda
    df_grouped = df.groupby([df['data_hora_ocorrencia'].dt.hour, 'Tipo da ocorrência']).size().reset_index(name='contagem')
    df_grouped.rename(columns={'data_hora_ocorrencia': 'Hora'}, inplace=True)

    fig = px.line(
        df_grouped,
        x='Hora',
        y='contagem',
        color='Tipo da ocorrência', # Cria uma linha para cada tipo e gera a legenda
        labels={'Hora': 'Hora do Dia', 'contagem': 'Nº de Ocorrências'},
        markers=True # Adiciona marcadores nos pontos de dados
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, dtick=1),
        yaxis=dict(showgrid=False),
        legend_title_text='Tipo de Ocorrência'
    )
    return fig