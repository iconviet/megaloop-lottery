cd "$(dirname "$0")"
../venv/bin/tbears deploy -c "./tbears_cli_config_mainnet.json" "$(dirname $(dirname "$0"))/megaloop"
