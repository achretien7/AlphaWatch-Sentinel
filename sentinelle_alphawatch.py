import os
import time
import csv
import ccxt

# Configuration Gate.io forcée sur les Swaps (Perpétuels)
exchange = ccxt.gateio({
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'} # C'est cette ligne qui corrige l'erreur !
})

# Liste complète avec le format Gate.io (ex: BTC_USDT:USDT)
symbols = [
    'BTC_USDT:USDT', 'ETH_USDT:USDT', 'SOL_USDT:USDT', 'XRP_USDT:USDT', 
    'ADA_USDT:USDT', 'DOGE_USDT:USDT', 'AVAX_USDT:USDT', 'DOT_USDT:USDT', 
    'LINK_USDT:USDT', 'UNI_USDT:USDT', 'ATOM_USDT:USDT', 'LTC_USDT:USDT', 
    'BCH_USDT:USDT', 'NEAR_USDT:USDT', 'APT_USDT:USDT', 'ARB_USDT:USDT', 
    'OP_USDT:USDT', 'SUI_USDT:USDT', 'SEI_USDT:USDT'
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
    print(f"🔍 Scan Dashboard (Gate.io Swaps) à {time.strftime('%H:%M:%S')}...")
    
    for symbol in symbols:
        try:
            funding = exchange.fetch_funding_rate(symbol)
            rate = funding['fundingRate']
            apr_final = rate * 3 * 365 * 100
            
            nom_crypto = symbol.split('_')[0]
            gain_24h = (50 * (apr_final/100)) / 365
            
            enregistrer_simulation(nom_crypto, apr_final, gain_24h)
            print(f"📊 {nom_crypto}: {apr_final:.2f}% enregistré")
            
            time.sleep(0.2)
        except Exception as e:
            print(f"⚠️ Skip {symbol}: {e}")

if __name__ == "__main__":
    try:
        scanner_pour_dashboard()
        print("✅ Dashboard mis à jour avec succès.")
    except Exception as e:
        print(f"❌ Erreur critique: {e}")













