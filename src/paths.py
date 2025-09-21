import os

# Root project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Environment variables
ENV_FPATH = os.path.join(ROOT_DIR, ".env")

# Code and configs
SRC_DIR = os.path.join(ROOT_DIR, "src")          # instead of "code"
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
APP_CONFIG_FPATH = os.path.join(CONFIG_DIR, "db_config.yaml")
PROMPT_CONFIG_FPATH = os.path.join(CONFIG_DIR, "prompt_config.yaml")

# Outputs
OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")
CHAT_HISTORY_DB_FPATH = os.path.join(OUTPUTS_DIR, "chat_history.db")

# Data
DATA_DIR = os.path.join(ROOT_DIR, "data")
PUBLICATION_FPATH = os.path.join(DATA_DIR, "my_dataset.md")

# Vector DB storage
# VECTOR_DB_DIR = os.path.join(ROOT_DIR, "vector_db")
VECTOR_DB_DIR = os.path.join(ROOT_DIR, "data", "vector_db")
