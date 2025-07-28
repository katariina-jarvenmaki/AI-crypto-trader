# core/cron_tasks_processor.py

from modules.path_selector.path_selector import path_selector

def cron_tasks_processor():

    configs_path, logs_path = path_selector(verbose=False)
    print(f"configs_path: {configs_path}")
    print(f"logs_path: {logs_path}")

if __name__ == "__main__":
    cron_tasks_processor()