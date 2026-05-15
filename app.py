# RODAR ARQUIVO
# python -m streamlit run app.py

# Importar bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title = "Dashboard TMDB",
    page_icon= "🎬",
    layout="wide"
)

# Carregar dataframe
df = pd.read_csv('data/tmdb_5000_movies.csv')

#========================================
# FUNÇÕES

# Tradução das colunas para interface
colunas_ui = {
    "title": "Título",
    "budget": "Orçamento (USD)",
    "revenue": "Receita (USD)",
    "vote_average": "Nota Média",
    "vote_count": "Quantidade de Votos",
    "popularity": "Popularidade",
    "release_date": "Data de Lançamento"
}

def traduzir_colunas(df):
    return df.rename(columns = colunas_ui)


# Função para formatar números grandes
def formatar_numero(valor):

    # Se o número for maior ou igual a 1 bilhão
    if valor >= 1_000_000_000:
        return f'{round(valor / 1_000_000_000, 1)}Bilhões'
    
    # Se o número for maior ou igual a 1 milhão
    elif valor >= 1_000_000:
        return f'{round(valor / 1_000_000, 1)}Milhões'
    
    # Se o número for maior ou igual a 1 mil
    elif valor >= 1_000:
        return f'{round(valor / 1_000, 1)}Mil'
    
    # Caso seja menor que mil
    else:
        return valor
    
# Função para formatar moeda
def formatar_moeda(valor):
    if valor >= 1_000_000_000:
        return f"$ {valor/1_000_000_000:.2f}B"
    elif valor >= 1_000_000:
        return f"$ {valor/1_000_000:.2f}M"
    else:
        return f"$ {valor:,.0f}"

#========================================
# FILTROS
st.sidebar.title("Filtros")

# Filtro Idioma
idiomas = df["original_language"].unique()
idiomas = ["Todos"] + list(idiomas)
idioma_escolhido = st.sidebar.selectbox("Escolha o idioma", idiomas)

# Filtro Nota
notas = df["vote_average"].unique()
notas = sorted(notas)
notas = ["Todos"] + list(notas)
notas_escolhidas = st.sidebar.multiselect("Escolha as notas", notas, default="Todos")

# Filtro Período - Ano
df["release_year"] = pd.to_datetime(df["release_date"]).dt.year
ano_escolhido = st.sidebar.slider("Escolha o período de anos",
                                  min_value = int(df["release_year"].min()),
                                  max_value = int(df["release_year"].max()),
                                  value = (
                                      int(df["release_year"].min()),
                                      int(df["release_year"].max())
                                  )
                                  )

# Dataframe filtrado
df_filtrado = df

if idioma_escolhido != "Todos":
    df_filtrado = df_filtrado[df_filtrado["original_language"] == idioma_escolhido]

if "Todos" not in notas_escolhidas:
    df_filtrado = df_filtrado[df_filtrado["vote_average"].isin(notas_escolhidas)]

df_filtrado = df_filtrado[
    (df_filtrado["release_year"] >= ano_escolhido[0]) &
    (df_filtrado["release_year"] <= ano_escolhido[1]) 
]


#============================================
# EXPLORAÇÃO DE DADOS

# Mostrar dataframe bruto
# st.subheader(" 📌 Visualização Dados Brutos")
# st.dataframe(df)

# st.subheader("📌 Visão Geral da Base")
# st.write("Dimensão do dataset")
# st.write(df.shape)

# st.write("Colunas disponíveis")
# st.write(df.columns)

# st.subheader("⚠️ Valores Faltantes")
# st.dataframe(df.isnull().sum())

# st.subheader("📊 Estatisticas Gerais")
# st.dataframe(df.describe())

# ========================================

# Título da Dashboard
st.title("🎬 Dashboard de Filmes - TMDB ")
st.write("Análise interativa de filmes e avaliações")

# KPIs
    
st.divider()

st.subheader("📊 KPIs")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    qtd_filmes = df_filtrado.shape[0]
    st.metric("🎬 Total de Filmes", qtd_filmes)

with col2:
    media_ava = round(df_filtrado["vote_average"].mean(), 1)
    st.metric("⭐ Avaliação Média", media_ava)

with col3:
    total_ava = df_filtrado["vote_count"].sum()
    st.metric("🗳️ Volume de Votos", formatar_numero(total_ava))

with col4:
    receita_total = df_filtrado["revenue"].sum()
    st.metric("💰 Receita Total (USD)", formatar_numero(receita_total))

with col5:
    orc_medio = round(df_filtrado["budget"].mean(), 2)
    st.metric("🎬 Orçamento Médio (USD)", formatar_numero(orc_medio))

st.divider()

# ========================================
# # INSIGHTS
st.subheader("🧠 Insights")

st.markdown("### 🎬 Receita vs Avaliação")
st.info("Filmes com maior faturamento não apresentam, em média, as maiores notas de avaliação, indicando que sucesso comercial e qualidade percebida pelo público não seguem a mesma tendência.")

st.markdown("### ⭐ Popularidade vs Avaliação")
st.info("A popularidade dos filmes não acompanha necessariamente suas avaliações médias, sugerindo que filmes mais assistidos não são sempre os mais bem avaliados pelos usuários.")

st.markdown("### 🔥 Receita vs Popularidade")
st.info("Apenas uma pequena parcela dos filmes aparece simultaneamente entre os mais populares e os de maior receita, indicando que alcance de público e desempenho financeiro nem sempre estão diretamente correlacionados.")

st.markdown("### 🗳️ Votos vs Avaliação")
st.info("Existe uma diferença entre filmes mais bem avaliados e filmes mais votados, o que sugere que volume de votos não é um fator determinante direto para maior nota média.")
st.divider()

# ========================================
# # RANKINGS

# Criação de novo dataframe apenas com filmes que possuem mais de 8000 votos
df_votos_validos = df_filtrado[df_filtrado["vote_count"] > 8000]

st.subheader("🔝 Rankings")
col1, col2 = st.columns(2)

# Ranking Filmes por Receita
top_receita = df_filtrado.sort_values(
        by=["revenue"],
        ascending=False
).head(10)[["title", "budget", "revenue"]]
top_receita = top_receita.reset_index(drop=True)
top_receita.index = top_receita.index + 1

top_receita_visual = top_receita.copy()
top_receita_visual["budget"] = top_receita_visual["budget"].apply(formatar_moeda)
top_receita_visual["revenue"] = top_receita_visual["revenue"].apply(formatar_moeda)

with col1:
    st.markdown("### 💰 Top 10 Filmes por Receita (USD)")
    st.caption("Filmes com maior desempenho financeiro no conjunto filtrado")

    top1 = top_receita_visual.iloc[0]
    st.success(f"🥇 Maior receita: {top1['title']} — {top1['revenue']}")
    st.dataframe(traduzir_colunas(top_receita_visual))


# Ranking Filmes por Avaliação
top_avaliacao = df_votos_validos.sort_values(
    by=["vote_average"],
    ascending=False
).head(10)[["title", "vote_average"]]
top_avaliacao = top_avaliacao.reset_index(drop=True)
top_avaliacao.index = top_avaliacao.index + 1

with col2:
    st.markdown("### ⭐ Top 10 Filmes por Avaliação")
    st.caption("Filmes com maior nota média entre usuários (filtrados por volume de votos)")

    # Proteção contra Dataframe vazio
    if not top_avaliacao.empty:
        top1 = top_avaliacao.iloc[0]
        st.success(f"🥇 Maior avaliação: {top1['title']} — {top1['vote_average']}")
        st.dataframe(traduzir_colunas(top_avaliacao))
    else:
        st.warning("Nenhum filme encontrado após os filtros aplicados.")


# Ranking Filmes por Popularidade
top_popularidade = df_filtrado.sort_values(
    by=["popularity"],
    ascending=False
).head(10)[["title", "popularity"]]
top_popularidade = top_popularidade.reset_index(drop=True)
top_popularidade.index = top_popularidade.index + 1

with col1:
    st.markdown("### 🔥 Top 10 Filmes por Popularidade")
    st.caption("Filmes com maior engajamento e interesse do público")

    top1 = top_popularidade.iloc[0]
    st.success(f"🥇 Mais popular: {top1['title']} — {top1['popularity']:.2f}")
    st.dataframe(traduzir_colunas(top_popularidade))


# Rankings Filmes por Quantidade de Votos
top_qtd_votos = df_filtrado.sort_values(
    by=["vote_count"],
    ascending=False
).head(10)[["title", "vote_count"]]
top_qtd_votos = top_qtd_votos.reset_index(drop=True)
top_qtd_votos.index = top_qtd_votos.index + 1

with col2:
    st.markdown("### 🗳️ Top 10 Filmes por Quantidade de Votos")
    st.caption("Filmes com maior participação do público nas avaliações")

    top1 = top_qtd_votos.iloc[0]
    st.success(f"🥇 Mais votado: {top1['title']} — {formatar_numero(top1["vote_count"])}")
    st.dataframe(traduzir_colunas(top_qtd_votos))

st.divider()

# ========================================
# GRÁFICOS

st.subheader("Gráficos")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💰 Top 10 Filmes por Receita (USD)")
    grafico_receita = px.bar(
        df_filtrado.sort_values(by=["revenue"], ascending=False).head(10), x="title", y="revenue",
        labels={
            "title": colunas_ui["title"],
            "revenue": colunas_ui["revenue"]
        })
    
    grafico_receita.update_layout(
        xaxis_tickangle=-45
    )

    st.plotly_chart(grafico_receita, use_container_width=True)

with col2:
    st.markdown("### ⭐ Distribuição das Avaliações")
    grafico_avaliacoes = px.histogram(
        df_filtrado, x="vote_average", 
        labels={
            "vote_average": colunas_ui["vote_average"]
        })
    st.plotly_chart(grafico_avaliacoes)

with col1:
    st.markdown("### 🔥 Popularidade vs Avaliação")
    grafico_popularidade_avaliacao = px.scatter(
        df_filtrado, x="popularity", y="vote_average", 
        labels={
            "popularity": colunas_ui["popularity"],
            "vote_average": colunas_ui["vote_average"]
        })
    st.plotly_chart(grafico_popularidade_avaliacao)

with col2:
    st.markdown("### 💰 Orçamento vs Receita")
    grafico_orcamento_receita = px.scatter(
        df_filtrado, x="budget", y="revenue", 
        labels={
            "budget": colunas_ui["budget"],
            "revenue": colunas_ui["revenue"]
        })
    st.plotly_chart(grafico_orcamento_receita)

st.divider()

# ========================================
# CONCLUSÃO DO PROJETO

st.subheader("🎬 Conclusão da Análise")

st.markdown("""
A análise dos dados do TMDB revela que o sucesso de um filme não depende de um único fator, mas sim de uma combinação de elementos como receita, avaliação, popularidade e engajamento do público.

De forma geral, observa-se que:

- 🎬 Filmes com maior receita não são necessariamente os mais bem avaliados, indicando que sucesso comercial e qualidade percebida não caminham sempre juntos.

- ⭐ A avaliação média dos filmes se mantém relativamente estável dentro dos filtros aplicados, sugerindo consistência na percepção do público.

- 🔥 Popularidade e receita apresentam alguma relação, mas não são diretamente proporcionais, mostrando que visibilidade não garante desempenho financeiro.

- 🗳️ O volume de votos não necessariamente influencia a nota média, indicando que quantidade de avaliações não é sinônimo de qualidade.

Em resumo, o dataset mostra que o desempenho de um filme é multifatorial, e nenhuma métrica isolada é suficiente para definir seu sucesso.
""")