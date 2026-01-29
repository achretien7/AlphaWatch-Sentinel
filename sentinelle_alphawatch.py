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

# --- 3. DÉMARRAGE DE LA MACHINE (BOUCLE) ---
print("🚀 Sentinelle AlphaWatch activée avec Simulation...")

while True:
    print(f"🔍 Scan en cours à {time.strftime('%H:%M:%S')}...")
    
    for s in symbols:
        try:
            funding = exchange.fetch_funding_rate(s)
            rate = funding['fundingRate']
            apr_final = rate * 3 * 365 * 3 * 100
            
            # Gain si on reste 24h sur cette position
            gain_24h = (50 * (apr_final/100)) / 365
            # Gain réel pour UNE HEURE (le temps entre deux scans)
            gain_une_heure = gain_24h / 24 
            
            if apr_final >= SEUIL_ALERTE:
                nom_crypto = s.split('/')[0]
                # On enregistre le gain d'UNE HEURE dans le CSV
                enregistrer_simulation(nom_crypto, apr_final, gain_une_heure)
                
        except Exception as e:
            print(f"⚠️ Erreur sur {s}: {e}")
            
    # Le bot attend avant le prochain scan
    print(f"✅ Scan terminé. Prochain passage dans {INTERVALLE/60:.0f} minutes.")
    time.sleep(INTERVALLE)