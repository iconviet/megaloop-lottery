cd "$(dirname "$0")"
../venv/bin/tbears deploy -c "./tbears_cli_config_local.json" "$(dirname $(dirname "$0"))/megaloop"
