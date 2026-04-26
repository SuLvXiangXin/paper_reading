#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="${PAPER_READER_TMUX_SESSION:-paper-reader-web-codex-7860}"
PORT="${PAPER_READER_WEB_PORT:-7860}"
HOST="${PAPER_READER_WEB_HOST:-0.0.0.0}"
CONDA_ENV="${PAPER_READER_CONDA_ENV:-paper_reader}"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$REPO_DIR/logs/web_server"
LOG_FILE="$LOG_DIR/paper_reader_web_${PORT}.log"

mkdir -p "$LOG_DIR"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "缺少命令: $1" >&2
    exit 1
  fi
}

proxy_url() {
  if [[ -n "${PAPER_READER_PUBLIC_URL:-}" ]]; then
    echo "${PAPER_READER_PUBLIC_URL}"
    return
  fi
  if [[ -n "${VSCODE_PROXY_URI:-}" ]]; then
    local url="$VSCODE_PROXY_URI"
    url="${url//'{{port}}'/$PORT}"
    url="${url//'{port}'/$PORT}"
    echo "$url"
    return
  fi
  if [[ -n "${NB_PREFIX:-}" ]]; then
    echo "${NB_PREFIX%/}/proxy/${PORT}/"
    return
  fi
  echo "http://127.0.0.1:${PORT}/"
}

kill_tmux_session() {
  if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "停止旧 tmux session: $SESSION_NAME"
    tmux kill-session -t "$SESSION_NAME"
  fi
}

kill_existing_app_processes() {
  local current_pid="$$"
  local pid args
  while read -r pid args; do
    [[ -z "${pid:-}" ]] && continue
    [[ "$pid" == "$current_pid" ]] && continue
    if [[ "$args" == *"paper_reader_web"* ]]; then
      echo "停止遗留 paper_reader_web 进程: pid=$pid"
      kill "$pid" 2>/dev/null || true
    fi
  done < <(ps -eo pid=,args=)

  sleep 0.6
}

kill_old_app_on_port() {
  local pids
  pids="$(ss -ltnp "sport = :${PORT}" 2>/dev/null | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | sort -u || true)"
  [[ -z "$pids" ]] && return

  local pid args
  for pid in $pids; do
    args="$(ps -p "$pid" -o args= 2>/dev/null || true)"
    if [[ "$args" == *"paper_reader_web"* ]]; then
      echo "停止旧 paper_reader_web 进程: pid=$pid"
      kill "$pid" 2>/dev/null || true
    else
      echo "端口 ${PORT} 被其他进程占用，未强杀: pid=$pid $args" >&2
      echo "请先释放端口，或设置 PAPER_READER_WEB_PORT 使用其他端口。" >&2
      exit 1
    fi
  done

  for _ in {1..20}; do
    if ! ss -ltn "sport = :${PORT}" 2>/dev/null | grep -q LISTEN; then
      return
    fi
    sleep 0.2
  done
}

wait_until_ready() {
  local health_url="http://127.0.0.1:${PORT}/api/health"
  for _ in {1..60}; do
    if curl -fsS "$health_url" >/dev/null 2>&1; then
      return
    fi
    sleep 0.5
  done
  echo "服务启动超时，最近日志:" >&2
  tail -80 "$LOG_FILE" >&2 || true
  exit 1
}

need_cmd tmux
need_cmd ss
need_cmd curl
need_cmd conda

cd "$REPO_DIR"

kill_tmux_session
kill_existing_app_processes
kill_old_app_on_port

: > "$LOG_FILE"

CMD="cd '$REPO_DIR' && conda run -n '$CONDA_ENV' python -m paper_reader_web --host '$HOST' --port '$PORT' 2>&1 | tee -a '$LOG_FILE'"
tmux new-session -d -s "$SESSION_NAME" -c "$REPO_DIR" "$CMD"

wait_until_ready

ENTRY_URL="$(proxy_url)"

cat <<EOF
Paper Reader Web 已启动

入口地址:
$ENTRY_URL

本地地址:
http://127.0.0.1:${PORT}/

tmux session:
$SESSION_NAME

查看日志:
tmux attach -t $SESSION_NAME
tail -f $LOG_FILE

停止服务:
tmux kill-session -t $SESSION_NAME
EOF
