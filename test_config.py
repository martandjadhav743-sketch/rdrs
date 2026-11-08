from app.core.config import load_config

config = load_config()

print(config.watched_folders)
print(config.thresholds.modified_files_per_minute)
print(config.response.simulation_mode)