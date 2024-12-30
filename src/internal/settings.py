from pathlib import Path

CONFIG_FILE_NAME = 'composer-config.yml'
WORKDIR = Path.cwd()
CURRENT_CFG = WORKDIR.joinpath(CONFIG_FILE_NAME)
