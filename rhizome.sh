#!/usr/bin/env bash

set -euo pipefail

HISTORY_DIR=".rhizome"
HISTORY_FILE="${HISTORY_DIR}/history.log"
MODEL_NAME="${RHIZOME_MODEL:-deepseek-r1:8b}"
MAX_HISTORY_LINES=400
DEFAULT_WARM_PROMPT="Please reply READY so I know you are initialized."
ONCE_REQUEST=""

print_help() {
  cat <<'EOF'
Usage: ./rhizome.sh [--once "request"] [request...]

Without options, starts an interactive AI shell assistant.
Use --once "request" (or provide a request directly) to run a single non-interactive request.
EOF
}

parse_args() {
  local pending=""
  while (($#)); do
    case "$1" in
      --once)
        shift
        if (($# == 0)); then
          echo "Error: --once requires a request argument." >&2
          exit 1
        fi
        ONCE_REQUEST="$1"
        shift
        ;;
      --help|-h)
        print_help
        exit 0
        ;;
      --*)
        echo "Unknown option: $1" >&2
        exit 1
        ;;
      *)
        if [[ -n "${pending}" ]]; then
          pending+=" $1"
        else
          pending="$1"
        fi
        shift
        ;;
    esac
  done

  if [[ -n "${pending}" ]]; then
    if [[ -n "${ONCE_REQUEST}" ]]; then
      ONCE_REQUEST+=" ${pending}"
    else
      ONCE_REQUEST="${pending}"
    fi
  fi
}

log() {
  printf '[%s] %s\n' "$(date +"%Y-%m-%d %H:%M:%S")" "$*" >&2
}

ensure_history_file() {
  mkdir -p "${HISTORY_DIR}"
  if [[ ! -f "${HISTORY_FILE}" ]]; then
    cat <<'EOF' > "${HISTORY_FILE}"
# Rhizome command history
# Format:
#   [timestamp] TYPE: content
EOF
  fi
}

warm_model() {
  if ! command -v ollama >/dev/null 2>&1; then
    log "ollama is not installed; aborting."
    exit 1
  fi

  if ! ollama ps 2>/dev/null | grep -q "${MODEL_NAME}"; then
    log "Warming ${MODEL_NAME} model (30 token spin-up)…"
    if ! printf '%s\n' "${DEFAULT_WARM_PROMPT}" | ollama run "${MODEL_NAME}" >/dev/null 2>&1; then
      log "Failed to warm ${MODEL_NAME}; continuing, but responses may be slow."
    fi
  else
    log "${MODEL_NAME} already appears warm."
  fi
}

append_history() {
  local type="$1"
  local content="$2"
  printf '[%s] %s: %s\n' "$(date +"%Y-%m-%d %H:%M:%S")" "${type}" "${content}" >> "${HISTORY_FILE}"
}

build_prompt() {
  local request="$1"
  local history
  history=$(tail -n "${MAX_HISTORY_LINES}" "${HISTORY_FILE}" 2>/dev/null || true)
  cat <<EOF
You are an assistant that produces safe bash commands based on a user request.
Return only one line containing the command to run. Do not add explanations,
markdown, quotes, or leading text. Use shell builtins when simple.

Available helper tools:
- ./rhizome_mem.py "Title" --content "text" --link NoteA --link NoteB : create/update associative notes under .rhizome/notes.

Command history transcript:
${history}

User request:
${request}
EOF
}

generate_command() {
  local prompt="$1"
  local response
  if ! response=$(printf '%s\n' "${prompt}" | ollama run "${MODEL_NAME}"); then
    log "ollama call failed."
    return 1
  fi

  # Take the last non-empty line as the command suggestion.
  printf '%s\n' "${response}" | awk 'NF{last=$0} END{print last}'
}

run_once() {
  local request="$1"
  append_history "REQUEST" "${request}"
  local prompt suggestion
  prompt=$(build_prompt "${request}")
  suggestion=$(generate_command "${prompt}") || exit 1

  printf 'Suggested command:\n\n  %s\n\n' "${suggestion}"
  execute_command "${suggestion}"
}

execute_command() {
  local command="$1"
  log "Executing: ${command}"
  append_history "COMMAND" "${command}"
  if bash -lc "${command}"; then
    append_history "RESULT" "success"
    log "Command completed successfully."
  else
    local status=$?
    append_history "RESULT" "failure (exit ${status})"
    log "Command failed with exit code ${status}."
    return "${status}"
  fi
}

main() {
  parse_args "$@"
  ensure_history_file
  warm_model

  if [[ -n "${ONCE_REQUEST}" ]]; then
    run_once "${ONCE_REQUEST}"
    return
  fi

  log "Rhizome AI executor ready. Type 'exit' or 'quit' to stop."

  while true; do
    read -r -p $'\n🌱 Request> ' user_request || break
    user_request="${user_request//[$'\t\r\n']/ }"

    case "${user_request}" in
      "" ) continue ;;
      exit|quit ) log "Goodbye!"; break ;;
    esac

    append_history "REQUEST" "${user_request}"
    prompt=$(build_prompt "${user_request}")
    suggestion=$(generate_command "${prompt}") || continue

    printf 'Suggested command:\n\n  %s\n\n' "${suggestion}"
    read -r -p "Run this command? [y/N]: " confirm
    case "${confirm}" in
      y|Y|yes|YES)
        execute_command "${suggestion}" || true
        ;;
      * )
        append_history "SKIP" "${suggestion}"
        log "Command skipped."
        ;;
    esac
  done
}

main "$@"
