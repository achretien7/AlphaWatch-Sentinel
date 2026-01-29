import os
import time
import csv
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SEUIL_ALERTE = 5
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
        
        # 🔍 DEBUG : Afficher la réponse complète
        print(f"🔍 Réponse API pour {symbol}: {data}")
        
        # ✅ CORRECTION : Binance utilise 'fundingRate' pas 'lastFundingRate'
        if 'lastFundingRate' in data:
            rate = float(data['lastFundingRate'])
        elif 'fundingRate' in data:
            rate = float(data['fundingRate'])
        else:
            print(f"⚠️ Aucun funding rate trouvé dans: {data.keys()}")
            return None
        
        print(f"🔍 {symbol} - Rate brut: {rate} ({rate*100:.4f}%)")
        
        return rate
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
        
        # 🔍 LOGS COMPLETS POUR DEBUG
        print(f"📊 {nom_crypto}:")
        print(f"   Rate: {rate} ({rate*100:.4f}%)")
        print(f"   APR: {apr_final:.2f}%")
        print(f"   Gain/h: {gain_une_heure:.4f} CHF")
        print(f"   Seuil: {SEUIL_ALERTE}%")
        print(f"   Passe le test? {apr_final >= SEUIL_ALERTE}")
        
        if apr_final >= SEUIL_ALERTE:
            opportunities.append({
                'crypto': nom_crypto,
                'apr': apr_final,
                'gain': gain_une_heure
            })
            enregistrer_simulation(nom_crypto, apr_final, gain_une_heure)
    else:
        print(f"⚠️ {symbol} - Aucune donnée reçue")

if opportunities:
    message = "💰 OPPORTUNITÉS\n\n"
    for opp in opportunities:
        message += f"• {opp['crypto']}: {opp['apr']:.2f}% APR ({opp['gain']:.4f} CHF/h)\n"
    envoyer_telegram(message)
else:
    envoyer_telegram(f"📊 Aucune opportunité > {SEUIL_ALERTE}% APR")

print("✅ Terminé")











