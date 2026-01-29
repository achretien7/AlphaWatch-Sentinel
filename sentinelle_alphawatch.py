import os
import time
import csv
import ccxt

# Configuration Gate.io Swaps
exchange = ccxt.gateio({
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}
})

# Format exact pour Gate.io Perpétuels (ex: BTC_USDT)
symbols = [
    'BTC_USDT', 'ETH_USDT', 'SOL_USDT', 'XRP_USDT', 
    'ADA_USDT', 'DOGE_USDT', 'AVAX_USDT', 'DOT_USDT', 
    'LINK_USDT', 'UNI_USDT', 'ATOM_USDT', 'LTC_USDT', 
    'BCH_USDT', 'NEAR_USDT', 'APT_USDT', 'ARB_USDT', 
    'OP_USDT', 'SUI_USDT', 'SEI_USDT'
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
    print(f"🔍 Scan Final (Gate.io) à {time.strftime('%H:%M:%S')}...")
    
    for symbol in symbols:
        try:
            # On utilise fetch_funding_rate qui est le plus fiable sur Gate.io
            funding = exchange.fetch_funding_rate(symbol)
            rate = funding['fundingRate']
            apr_final = rate * 3 * 365 * 100
            
            nom_crypto = symbol.split('_')[0]
            gain_24h = (50 * (apr_final/100)) / 365
            
            enregistrer_simulation(nom_crypto, apr_final, gain_24h)
            print(f"✅ {nom_crypto}: {apr_final:.2f}% enregistré")
            
            time.sleep(0.2)
        except Exception as e:
            # Si le format simple échoue, on tente avec l'ID complet de Gate.io
            try:
                funding = exchange.fetch_funding_rate(symbol + "_USDT")
                # ... même logique ...
            except:
                print(f"⚠️ Erreur {symbol}: {e}")

if __name__ == "__main__":
    scanner_pour_dashboard()













