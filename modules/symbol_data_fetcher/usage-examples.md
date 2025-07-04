# Running from the Command Line

Each task can be run like this:
```bash
python symbol_data_fetcher.py main_symbols_data_fetcher  
python symbol_data_fetcher.py supported_symbols_data_fetcher  
python symbol_data_fetcher.py potential_traders_checker  
```

## Possible Improvement (combined execution)

You can add an argument like --all to the main command to run all three:
```bash
parser_all = subparsers.add_parser("run_all", help="Run all tasks sequentially")  
parser_all.set_defaults(func=run_all_tasks)  

def run_all_tasks():  
    run_main_symbols_data_fetcher()  
    run_supported_symbols_data_fetcher()  
    run_potential_traders_checker()  
```

## Cron Scheduling (e.g., on Linux)

Every 5 minutes:
```bash
*/5 * * * * /usr/bin/python3 /path/to/symbol_data_fetcher.py main_symbols_data_fetcher
```

Every 30 minutes:
```bash
*/30 * * * * /usr/bin/python3 /path/to/symbol_data_fetcher.py supported_symbols_data_fetcher
```

Twice a day at 9:00 (AM and PM):
```bash
0 9,21 * * * cd /opt/kjc/int/AI-crypto-trader && /usr/bin/python3 -m modules.symbol_data_fetcher.tasks.potential_trades_checker >> logs/cron.log 2>&1
```
