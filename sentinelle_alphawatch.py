import os
import ccxt
import time
import csv
import requests

# 1. CONFIGURATION
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SEUIL_ALERTE = 0.1
INTERVALLE = 3600

# Configuration exchange avec plusieurs tentatives
exchange = ccxt.bybit({
    'options': {
        'defaultType': 'swap',
        'adjustForTimeDifference': True
    },
    'enableRateLimit': True,  # Important pour éviter les bans
    'timeout': 30000,  # 30 secondes de timeout
})

symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'ADA/USDT:USDT', 'XRP/USDT:USDT']

# 2. FONCTIONS
def envoyer_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        params = {
            'chat_id': CHAT_ID,
            'text': message
        }
        response = requests.post(url, params=params, timeout=10)
        if response.status_code == 200:
            print(f"✅ Message Telegram envoyé")
        else:
            print(f"⚠️ Erreur Telegram: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur envoi Telegram: {e}")

def enregistrer_simulation(crypto, apr, gain_50):
    fichier = 'simulation_gains.csv'
    existe = os.path.isfile(fichier)
    with open(fichier, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Date', 'Crypto', 'APR %', 'Gain estime 24h (50 CHF)'])
        
        date_heure = time.strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([date_heure, crypto, f"{apr:.2f}%", f"{gain_50:.4f} CHF"])

# 3. TEST DE CONNEXION TELEGRAM AU DÉMARRAGE
print("🔍 Test de connexion Telegram...")
envoyer_telegram("🚀 Bot AlphaWatch démarré depuis GitHub Actions")

# 4. SCAN DES CRYPTOS
print(f"🚀 Scan AlphaWatch en cours à {time.strftime('%H:%M:%S')}...")

erreurs_consecutives = 0

for s in symbols:
    try:
        # Attendre un peu entre chaque requête
        time.sleep(2)
        
        funding = exchange.fetch_funding_rate(s)
        rate = funding['fundingRate']
        apr_final = rate * 3 * 365 * 3 * 100
        
        gain_24h = (50 * (apr_final/100)) / 365
        gain_une_heure = gain_24h / 24 
        
        if apr_final >= 0.1: 
            nom_crypto = s.split('/')[0]
            msg = f"✅ {nom_crypto} | APR: {apr_final:.2f}% | Gain/h: {gain_une_heure:.4f} CHF"
            
            envoyer_telegram(msg)
            enregistrer_simulation(nom_crypto, apr_final, gain_une_heure)
            print(f"💰 Log enregistré pour {nom_crypto}")
        
        # Réinitialiser le compteur d'erreurs si succès
        erreurs_consecutives = 0
            
    except ccxt.NetworkError as e:
        erreurs_consecutives += 1
        print(f"⚠️ Erreur réseau sur {s}: {e}")
        if erreurs_consecutives >= 3:
            envoyer_telegram("❌ Problème de connexion à Bybit depuis GitHub Actions")
            break
    except Exception as e:
        print(f"⚠️ Erreur sur {s}: {e}")

print("✅ Scan terminé.")






