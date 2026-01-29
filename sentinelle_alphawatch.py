import os
import time
import csv
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SEUIL_ALERTE = 0.1
symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT']

def envoyer_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        params = {'chat_id': CHAT_ID, 'text': message}
        requests.post(url, params=params, timeout=10)
        print(f"✅ Message envoyé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def enregistrer_simulation(crypto, apr, gain_50):
    fichier = 'simulation_gains.csv'
    existe = os.path.isfile(fichier)
    with open(fichier, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Date', 'Crypto', 'APR %', 'Gain estime 24h (50 CHF)'])
        date_heure = time.strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([date_heure, crypto, f"{apr:.2f}%", f"{gain_50:.4f} CHF"])

def get_funding_rate_binance(symbol):
    """Récupère le funding rate de Binance Futures"""
    try:
        url = "https://fapi.binance.com/fapi/v1/premiumIndex"
        params = {'symbol': symbol}
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        return float(data['lastFundingRate'])
    except Exception as e:
        print(f"❌ Erreur Binance {symbol}: {e}")
        return None

print("🚀 Bot démarré...")
envoyer_telegram("🚀 AlphaWatch actif - Scan Binance...")

opportunities = []

for symbol in symbols:
    time.sleep(0.5)
    rate = get_funding_rate_binance(symbol)
    
    if rate is not None:
        apr_final = rate * 3 * 365 * 100
        gain_24h = (50 * (apr_final/100)) / 365
        gain_une_heure = gain_24h / 24
        
        nom_crypto = symbol.replace('USDT', '')
        print(f"✅ {nom_crypto}: {apr_final:.2f}% APR")
        
        if apr_final >= SEUIL_ALERTE:
            opportunities.append({
                'crypto': nom_crypto,
                'apr': apr_final,
                'gain': gain_une_heure
            })
            enregistrer_simulation(nom_crypto, apr_final, gain_une_heure)

if opportunities:
    message = "💰 OPPORTUNITÉS\n\n"
    for opp in opportunities:
        message += f"• {opp['crypto']}: {opp['apr']:.2f}% APR ({opp['gain']:.4f} CHF/h)\n"
    envoyer_telegram(message)
else:
    envoyer_telegram("📊 Aucune opportunité > 0.1% APR")

print("✅ Terminé")







