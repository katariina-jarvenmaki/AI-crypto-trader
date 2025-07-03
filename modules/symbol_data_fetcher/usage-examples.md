## Ajaminen komentoriviltä

Kukin tehtävä voidaan ajaa näin:
python symbol_data_fetcher.py main_symbols_data_fetcher
python symbol_data_fetcher.py supported_symbols_data_fetcher
python symbol_data_fetcher.py potential_traders_checker

# Mahdollinen parannus (yhdistetty ajaminen)
Voit lisätä pääkomentoon argumentin kuten --all, jolla ajetaan kaikki kolme:
parser_all = subparsers.add_parser("run_all", help="Aja kaikki tehtävät peräkkäin")
parser_all.set_defaults(func=run_all_tasks)

def run_all_tasks():
    run_main_symbols_data_fetcher()
    run_supported_symbols_data_fetcher()
    run_potential_traders_checker()

# Bonus: Cron-ajastus (esim. Linuxissa)

# joka 5 minuutti
*/5 * * * * /usr/bin/python3 /path/to/symbol_data_fetcher.py main_symbols_data_fetcher

# joka 30 minuutti
*/30 * * * * /usr/bin/python3 /path/to/symbol_data_fetcher.py supported_symbols_data_fetcher

# joka toinen päivä klo 01:00
0 1 */2 * * /usr/bin/python3 /path/to/symbol_data_fetcher.py potential_traders_checker
