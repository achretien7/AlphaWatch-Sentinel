import os
import time
import csv
import ccxt

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SEUIL_ALERTE = 30  # Seuil réaliste pour vraies opportunités
INTERVALLE = 600   # 10 minutes entre chaque scan

# Configuration Bybit
exchange = ccxt.bybit({
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}
})

# Liste étendue de cryptos
symbols = [
    'BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'XRP/USDT:USDT', 
    'ADA/USDT:USDT', 'DOGE/USDT:USDT', 'AVAX/USDT:USDT', 'MATIC/USDT:USDT',
    'DOT/USDT:USDT', 'LINK/USDT:USDT', 'UNI/USDT:USDT', 'ATOM/USDT:USDT',
    'LTC/USDT:USDT', 'BCH/USDT:USDT', 'NEAR/USDT:USDT', 'APT/USDT:USDT',
    'ARB/USDT:USDT', 'OP/USDT:USDT', 'SUI/USDT:USDT', 'SEI/USDT:USDT'
]

def envoyer_telegram(message):
    try:
        import requests
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        params = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
        requests.post(url, params=params, timeout=10)
        print(f"✅ Message envoyé")
    except Exception as e:
        print(f"❌ Erreur Telegram: {e}")

def enregistrer_simulation(crypto, apr, gain_50):
    fichier = 'simulation_gains.csv'
    existe = os.path.isfile(fichier)
    with open(fichier, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Date', 'Crypto', 'APR %', 'Gain estime 24h (50 CHF)'])
        date_heure = time.strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([date_heure, crypto, f"{apr:.2f}%", f"{gain_50:.4f} CHF"])

def scanner_opportunites():
    print(f"\n🔍 Scan à {time.strftime('%H:%M:%S')}...")
    opportunities = []
    
    for symbol in symbols:
        try:
            funding = exchange.fetch_funding_rate(symbol)
            rate = funding['fundingRate']
            apr_final = rate * 3 * 365 * 100
            
            nom_crypto = symbol.split('/')[0]
            
            if apr_final >= SEUIL_ALERTE:
                gain_24h = (50 * (apr_final/100)) / 365
                gain_une_heure = gain_24h / 24
                
                opportunities.append({
                    'crypto': nom_crypto,
                    'apr': apr_final,
                    'gain': gain_une_heure
                })
                
                enregistrer_simulation(nom_crypto, apr_final, gain_une_heure)
                print(f"💰 {nom_crypto}: {apr_final:.2f}% APR")
            
            time.sleep(0.5)  # Éviter rate limit
            
        except Exception as e:
            print(f"⚠️ Erreur {symbol}: {e}")
    
    return opportunities

def envoyer_rapport(opportunities):
    if opportunities:
        message = "💰 <b>OPPORTUNITÉS DÉTECTÉES</b>\n\n"
        for opp in sorted(opportunities, key=lambda x: x['apr'], reverse=True):
            message += f"• <b>{opp['crypto']}</b>: {opp['apr']:.2f}% APR\n"
            message += f"  Gain/h: {opp['gain']:.4f} CHF\n\n"
        envoyer_telegram(message)
    else:
        print(f"📊 Aucune opportunité > {SEUIL_ALERTE}% APR")

# Boucle principale
print("🚀 AlphaWatch démarré sur VPS Oracle")
envoyer_telegram("🚀 <b>AlphaWatch actif</b>\nScan Bybit toutes les 10 min")

while True:
    try:
        opportunities = scanner_opportunites()
        envoyer_rapport(opportunities)
        print(f"⏰ Prochain scan dans {INTERVALLE//60} minutes...")
        time.sleep(INTERVALLE)
    except KeyboardInterrupt:
        print("\n👋 Arrêt du bot")
        break
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        time.sleep(60)  # Attendre 1 min avant de réessayer











