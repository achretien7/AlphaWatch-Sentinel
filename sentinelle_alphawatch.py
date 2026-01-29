import os
import time
import csv
import ccxt
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# On baisse le seuil à 0 pour GitHub pour être sûr d'avoir des points sur le graphique
SEUIL_DASHBOARD = 0  

# Configuration Binance (Accepte les connexions GitHub)
exchange = ccxt.binance({'enableRateLimit': True})

# Votre liste complète de cryptos (adaptée au format Binance)
symbols = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 
    'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'MATIC/USDT',
    'DOT/USDT', 'LINK/USDT', 'UNI/USDT', 'ATOM/USDT',
    'LTC/USDT', 'BCH/USDT', 'NEAR/USDT', 'APT/USDT',
    'ARB/USDT', 'OP/USDT', 'SUI/USDT', 'SEI/USDT'
]

def enregistrer_simulation(crypto, apr, gain_50):
    fichier = 'simulation_gains.csv'
    existe = os.path.isfile(fichier)
    with open(fichier, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not existe or os.stat(fichier).st_size == 0:
            writer.writerow(['Date', 'Crypto', 'APR %', 'Gain estime 24h (50 CHF)'])
        date_heure = time.strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([date_heure, crypto, f"{apr:.2f}%", f"{gain_50:.4f} CHF"])

def scanner_pour_dashboard():
    print(f"🔍 Scan Dashboard (Binance) à {time.strftime('%H:%M:%S')}...")
    
    for symbol in symbols:
        try:
            # Sur Binance on récupère le funding via fetch_funding_rate ou fetch_premium_index
            funding = exchange.fetch_funding_rate(symbol)
            rate = funding['fundingRate']
            apr_final = rate * 3 * 365 * 100
            
            nom_crypto = symbol.split('/')[0]
            gain_24h = (50 * (apr_final/100)) / 365
            
            # On enregistre tout pour avoir un beau graphique complet
            enregistrer_simulation(nom_crypto, apr_final, gain_24h)
            print(f"📊 {nom_crypto}: {apr_final:.2f}% enregistré")
            
            time.sleep(0.1) 
        except Exception as e:
            print(f"⚠️ Skip {symbol}: {e}")

# --- EXECUTION UNIQUE POUR GITHUB ACTIONS ---
if __name__ == "__main__":
    try:
        scanner_pour_dashboard()
        print("✅ Dashboard mis à jour. GitHub va maintenant sauvegarder le CSV.")
    except Exception as e:
        print(f"❌ Erreur: {e}")











