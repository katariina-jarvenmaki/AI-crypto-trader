# KÄYTÄ KOMENNOT:
# python3 scripts/pick_from_history_analysis.py AEROUSDT 2025-07-23T13:00:00 2025-07-23T18:00:00

import sys
import json
from datetime import datetime, timezone, timedelta
import os

def main():
    if len(sys.argv) < 4:
        print("Käyttö: python poimi_symboli.py <symboli> <alkuaika> <loppuaika>")
        print("Esim:   python poimi_symboli.py AEROUSDT 2025-07-24T09:00:00 2025-07-24T10:00:00")
        sys.exit(1)

    tiedosto = "../AI-crypto-trader-logs/analysis-data/history_analysis_log.jsonl"
    haluttu_symboli = sys.argv[1]

    # Käytetään +03:00 aikavyöhykettä
    tz = timezone(timedelta(hours=3))
    alku = datetime.fromisoformat(sys.argv[2]).replace(tzinfo=tz)
    loppu = datetime.fromisoformat(sys.argv[3]).replace(tzinfo=tz)

    try:
        with open(tiedosto, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        print(f"Virhe tiedostoa luettaessa: {e}")
        sys.exit(1)

    osumat = []
    for r in records:
        # Tarkista että timestamp on olemassa
        timestamp_str = r.get("timestamp")
        if not timestamp_str:
            continue

        try:
            ts = datetime.fromisoformat(timestamp_str)
        except:
            continue

        # Lisää symboli, jos puuttuu
        if "symbol" not in r:
            r["symbol"] = haluttu_symboli

        if r["symbol"] == haluttu_symboli and alku <= ts <= loppu:
            osumat.append(r)

    if not osumat:
        print("Ei osumia annetulle symbolille ja aikavälille.")
    else:
        print(f"{len(osumat)} osumaa löytyi.")
        for r in osumat:
            print(json.dumps(r, indent=2))

        # Tallenna tulokset tiedostoon
        tulostiedosto = f"temp_log_poimi_symboli.jsonl"
        try:
            with open(tulostiedosto, "w", encoding="utf-8") as out:
                for r in osumat:
                    out.write(json.dumps(r) + "\n")
            print(f"Tulokset tallennettu tiedostoon: {tulostiedosto}")
        except Exception as e:
            print(f"Virhe tallennettaessa tiedostoon: {e}")

if __name__ == "__main__":
    main()
