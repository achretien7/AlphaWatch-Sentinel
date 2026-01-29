import os  # Ajoutez cet import en haut
import ccxt
import time
import csv
import requests

# 1. CONFIGURATION (VERSION CLOUD)
# On demande au serveur de lire les secrets qu'on a enregistrés à l'étape 2
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Le reste de notre configuration ne change pas
SEUIL_ALERTE = 15.0
INTERVALLE = 3600
exchange = ccxt.bybit()
symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'ADA/USDT:USDT', 'XRP/USDT:USDT']

# --- 2. DÉFINITION DES OUTILS (FONCTIONS) ---
# On les place ICI pour que Python les connaisse AVANT de lancer la boucle

def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url)

def enregistrer_simulation(crypto, apr, gain_50):
    fichier = 'simulation_gains.csv'
    existe = os.path.isfile(fichier)
    with open(fichier, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not existe:
            # On écrit l'entête seulement la première fois
            writer.writerow(['Date', 'Crypto', 'APR %', 'Gain estime 24h (50 CHF)'])
        
        date_heure = time.strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([date_heure, crypto, f"{apr:.2f}%", f"{gain_50:.4f} CHF"])

# --- 3. DÉMARRAGE DE LA MACHINE (VERSION CLOUD) ---
print(f"🔍 Scan AlphaWatch en cours à {time.strftime('%H:%M:%S')}...")

for s in symbols:
    try:
        funding = exchange.fetch_funding_rate(s)
        rate = funding['fundingRate']
        apr_final = rate * 3 * 365 * 3 * 100
        
        # Gain théorique sur 24h
        gain_24h = (50 * (apr_final/100)) / 365
        # Gain réel pour l'heure qui vient de s'écouler
        gain_une_heure = gain_24h / 24 
        
        if apr_final >= SEUIL_ALERTE:
            nom_crypto = s.split('/')[0]
            msg = f"🔥 ALERTE ! {nom_crypto} | APR: {apr_final:.2f}% | Gain: {gain_24h:.2f} CHF"
            
            # Envoi et enregistrement
            envoyer_telegram(msg)
            enregistrer_simulation(nom_crypto, apr_final, gain_une_heure)
            
    except Exception as e:
        print(f"⚠️ Erreur sur {s}: {e}")

# IMPORTANT : Pas de time.sleep ni de boucle infinie ici !
print("✅ Scan terminé avec succès. GitHub relancera le bot dans 1 heure.")
