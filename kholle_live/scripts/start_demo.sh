#!/usr/bin/env bash
# Démo : proxy de patience (8001), puis serveur de la khôlle (8000) qui passe par lui.
# Si le proxy ne répond pas en 10 s : serveur en direct sur OpenAI, le khôlleur n'est jamais muet.
# Ctrl-C arrête les deux. kholle_live/.env n'est pas modifié.
#
#   bash scripts/start_demo.sh                 depuis kholle_live (Git Bash sous Windows)
#   PROXY_HOLD=0 bash scripts/start_demo.sh    proxy en simple relais
#   PORT=8011 bash scripts/start_demo.sh       serveur sur un autre port (tests)
set -u
cd "$(dirname "$0")/.."

PORT=${PORT:-8000}
PROXY_PORT=${PROXY_PORT:-8001}
PROXY_URL="http://127.0.0.1:$PROXY_PORT"
DIRECT_URL=${PROXY_UPSTREAM_URL:-https://api.openai.com/v1}
JOURNAL_PROXY=${JOURNAL_PROXY:-${TMPDIR:-/tmp}/kholle_proxy.log}
UV=$(command -v uv || echo "$HOME/.local/bin/uv")
PROXY_PID=""

proxy_repond() {
  curl -s --max-time 1 "$PROXY_URL/openapi.json" 2>/dev/null | grep -q "Proxy de patience"
}

tuer() {  # un processus et ses descendants (uv lance python)
  local pid=$1 enfants
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null || return 0
  if [ -r "/proc/$pid/winpid" ] && command -v taskkill >/dev/null 2>&1; then
    taskkill //F //T //PID "$(cat "/proc/$pid/winpid")" >/dev/null 2>&1
  else
    enfants=$(pgrep -P "$pid" 2>/dev/null)
    kill "$pid" 2>/dev/null
    [ -n "$enfants" ] && kill $enfants 2>/dev/null
  fi
  return 0
}

arreter() {
  trap - INT TERM EXIT
  echo
  echo "Arrêt de la démo."
  tuer "$PROXY_PID"
}
trap arreter EXIT
trap 'exit 130' INT TERM

SCRIPT=$$
garder_proxy() {  # relancé s'il s'arrête en pleine démo, tant que ce script vit
  while kill -0 "$SCRIPT" 2>/dev/null; do
    PYTHONIOENCODING=utf-8 "$UV" run uvicorn kholle.llm_proxy:app --host 127.0.0.1 --port "$PROXY_PORT" >>"$JOURNAL_PROXY" 2>&1
    echo "$(date +%T) proxy arrêté, relance dans 1 s" >>"$JOURNAL_PROXY"
    sleep 1
  done
}

if proxy_repond; then
  echo "Proxy de patience déjà lancé sur $PROXY_PORT : réutilisé (il ne sera pas arrêté avec la démo)."
else
  echo "Proxy de patience : démarrage sur $PROXY_PORT (journal : $JOURNAL_PROXY)"
  garder_proxy &
  PROXY_PID=$!
  debut=$SECONDS
  until proxy_repond || (( SECONDS - debut >= 10 )); do sleep 0.5; done
fi

if proxy_repond; then
  echo "Proxy de patience prêt : le serveur passe par $PROXY_URL/v1"
  LLM="$PROXY_URL/v1"
else
  tuer "$PROXY_PID"
  PROXY_PID=""
  cat >&2 <<EOF

##########################################################################
##
##   ATTENTION : LE PROXY DE PATIENCE NE RÉPOND PAS (port $PROXY_PORT).
##
##   Démo lancée SANS proxy : le khôlleur parle directement à OpenAI
##   et peut couper l'étudiant au milieu d'une phrase.
##   Journal du proxy : $JOURNAL_PROXY
##
##########################################################################

EOF
  # Adresse directe explicite plutôt qu'une variable vide : elle l'emporte sur un
  # LLM_BASE_URL resté dans .env, et gradbot prendrait une chaîne vide pour une adresse.
  LLM="$DIRECT_URL"
fi

# Au premier plan : Ctrl-C lui parvient directement ; à sa sortie, le trap EXIT arrête le proxy.
LLM_BASE_URL="$LLM" "$UV" run uvicorn main:app --host 0.0.0.0 --port "$PORT"
