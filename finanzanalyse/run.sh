#!/usr/bin/with-contenv bashio
set -e

export LLM_PROVIDER="$(bashio::config 'llm_provider')"
export AZURE_OPENAI_ENDPOINT="$(bashio::config 'azure_openai_endpoint')"
export AZURE_OPENAI_API_KEY="$(bashio::config 'azure_openai_api_key')"
export AZURE_OPENAI_DEPLOYMENT="$(bashio::config 'azure_openai_deployment')"
export AZURE_OPENAI_API_VERSION="$(bashio::config 'azure_openai_api_version')"
export HOUSEHOLD_ADULTS="$(bashio::config 'household_adults')"
export HOUSEHOLD_CHILDREN="$(bashio::config 'household_children')"
export HOUSEHOLD_NET_INCOME_RANGE="$(bashio::config 'household_net_income_range')"
export LOG_LEVEL="$(bashio::config 'log_level')"

export DATABASE_URL="sqlite:////data/finanzanalyse.db"
export CORS_ORIGINS="*"
export SECRET_KEY="${SECRET_KEY:-ha-addon-default-please-rotate}"
export STATIC_DIR="/app/static"

mkdir -p /data

bashio::log.info "Starte Finanzanalyse (Provider: ${LLM_PROVIDER})"

cd /app
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
