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
SEUIL_ALERTE = 0.1
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

# --- 3. DÉMARRAGE DE LA MACHINE (VERSION CLOUD OPTIMISÉE) ---
print(f"🚀 Scan AlphaWatch en cours à {time.strftime('%H:%M:%S')}...")

for s in symbols:
    try:
        funding = exchange.fetch_funding_rate(s)
        rate = funding['fundingRate']
        apr_final = rate * 3 * 365 * 3 * 100
        
        # Gain théorique sur 24h
        gain_24h = (50 * (apr_final/100)) / 365
        # Gain réel pour l'heure écoulée
        gain_une_heure = gain_24h / 24 
        
        # TEST : Seuil bas pour forcer la notification
        if apr_final >= 0.1: 
            nom_crypto = s.split('/')[0]
            msg = f"✅ TEST CLOUD : {nom_crypto} est actif ! APR: {apr_final:.2f}%"
            
            envoyer_telegram(msg)
            enregistrer_simulation(nom_crypto, apr_final, gain_une_heure)
            print(f"💰 Log enregistré pour {nom_crypto}")
            
    except Exception as e:
        print(f"⚠️ Erreur sur {s}: {e}")

print("✅ Scan terminé. GitHub va maintenant sauvegarder le CSV.")


