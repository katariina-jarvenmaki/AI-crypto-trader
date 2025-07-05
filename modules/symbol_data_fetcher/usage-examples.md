# Running from the Command Line

Each task can be run like this:
```bash
cd /opt/kjc/int/AI-crypto-trader
/usr/bin/python3 -m modules.symbol_data_fetcher.tasks.potential_trades_checker
/usr/bin/python3 -m modules.symbol_data_fetcher.tasks.main_symbols_data_fetcher
/usr/bin/python3 -m modules.symbol_data_fetcher.tasks.top_symbols_data_fetcher
```

## Possible Improvement (combined execution)

You can add an argument like --all to the main command to run all three:
```bash
parser_all = subparsers.add_parser("run_all", help="Run all tasks sequentially")  
parser_all.set_defaults(func=run_all_tasks)  

def run_all_tasks():  
    run_main_symbols_data_fetcher()  
    run_top_symbols_data_fetcher()  
    run_potential_traders_checker()  
```

## Cron Scheduling (e.g., on Linux)

**Main symbol data fetching (Potential trades checker is supposted to run first at least once before this)**

Every 5 minutes:
```bash
*/5 * * * * cd /opt/kjc/int/AI-crypto-trader && /usr/bin/python3 -m modules.symbol_data_fetcher.tasks.main_symbols_data_fetcher >> logs/cron.log 2>&1
```

**Supported symbol data fetching (Potential trades checker is supposted to run first at least once before this)**

Every 30 minutes:
```bash
*/30 * * * * cd /opt/kjc/int/AI-crypto-trader && /usr/bin/python3 -m modules.symbol_data_fetcher.tasks.top_symbols_data_fetcher >> logs/cron.log 2>&1
```

**Potential trades checker**

Twice a day at 9:00 (AM and PM):
```bash
0 9,21 * * * cd /opt/kjc/int/AI-crypto-trader && /usr/bin/python3 -m modules.symbol_data_fetcher.tasks.potential_trades_checker >> logs/cron.log 2>&1
```

Four times a day at 3:00, 9:00, 15:00, 21:00:
```bash
0 3,9,15,21 * * * cd /opt/kjc/int/AI-crypto-trader && /usr/bin/python3 -m modules.symbol_data_fetcher.tasks.potential_trades_checker >> logs/cron.log 2>&1
```

**Check and update crons**
```bash
crontab -e
```

**Check cron log**
```bash
tail -n 100 /opt/kjc/int/AI-crypto-trader/logs/cron.log
```