import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AlphaWatch Sentinel", page_icon="💰", layout="wide")
st.title("🛡️ AlphaWatch Sentinel Dashboard")

CSV_URL = "https://raw.githubusercontent.com/achretien7/AlphaWatch-Sentinel/main/simulation_gains.csv"

try:
    # Lecture forcée de tout en texte pour éviter les erreurs
    df = pd.read_csv(CSV_URL, dtype=str)
    
    if not df.empty:
        # Nettoyage sécurisé des données
        df['Date'] = pd.to_datetime(df['Date'])
        df['APR %'] = df['APR %'].str.replace('%', '', regex=False).astype(float)
        df['Gain'] = df['Gain estime 24h (50 CHF)'].str.replace(' CHF', '', regex=False).astype(float)

        # KPI
        col1, col2, col3 = st.columns(3)
        col1.metric("Gain Cumulé (Est.)", f"{df['Gain'].sum():.4f} CHF")
        col2.metric("Dernier APR Max", f"{df['APR %'].iloc[-1]:.2f}%")
        col3.metric("Nb de Scans", len(df))

        # Graphique
        fig = px.line(df, x='Date', y='APR %', color='Crypto', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
    else:
        st.info("👋 Bienvenue ! Le dashboard s'affichera dès que le CSV contiendra des données.")

except Exception as e:
    st.warning("🔄 Synchronisation du CSV en cours...")
    # Affiche l'erreur simplifiée pour le debug si besoin
    st.write("Détail : Ajoutez une ligne au CSV sur GitHub pour débloquer l'affichage.")
