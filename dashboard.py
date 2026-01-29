import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="AlphaWatch Sentinel", page_icon="💰", layout="wide")

st.title("🛡️ AlphaWatch Sentinel Dashboard")

# 1. Chargement des données
CSV_URL = "https://raw.githubusercontent.com/achretien7/AlphaWatch-Sentinel/main/simulation_gains.csv"

try:
    df = pd.read_csv(CSV_URL)
    df['Date'] = pd.to_datetime(df['Date'])
    # Nettoyage des chiffres
    df['APR %'] = df['APR %'].str.replace('%', '').astype(float)
    df['Gain'] = df['Gain estime 24h (50 CHF)'].str.replace(' CHF', '').astype(float)

    # 2. Section KPI (Gros chiffres)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gain Cumulé (Est.)", f"{df['Gain'].sum():.4f} CHF")
    with col2:
        st.metric("Dernier APR Max", f"{df['APR %'].iloc[-1]:.2f}%")
    with col3:
        st.metric("Nb de Scans", len(df))

    # 3. Graphique d'évolution
    st.subheader("📈 Évolution de l'APR par Crypto")
    fig = px.line(df, x='Date', y='APR %', color='Crypto', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # 4. Historique détaillé
    st.subheader("📋 Dernières Opportunités")
    st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)

except Exception as e:
    st.info("👋 Bienvenue ! Le dashboard s'affichera dès que le fichier CSV contiendra des données.")
    st.error(f"Erreur technique (si besoin) : {e}")
