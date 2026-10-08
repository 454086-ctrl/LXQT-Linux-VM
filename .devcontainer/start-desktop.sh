#!/usr/bin/env bash
set -Eeuo pipefail

export DISPLAY=:0

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
panel_config="${XDG_CONFIG_HOME:-$HOME/.config}/lxqt/panel.conf"
if [[ -f /usr/share/lxqt/lxqt-panel/fancymenu.desktop && -f "$panel_config" ]]; then
  sed -i '/^\[mainmenu\]$/,/^\[/ s/^type=mainmenu$/type=fancymenu/' "$panel_config"
fi
python3 "$script_dir/configure-lxqt-menu.py" \
  "$panel_config" \
  /usr/share/lxqt/panel.conf \
  /etc/xdg/menus/kf5-applications.menu \
  "${XDG_CONFIG_HOME:-$HOME/.config}/menus/panel-applications.menu"

pids=()
cleanup() {
  for pid in "${pids[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

Xvfb "$DISPLAY" -screen 0 1440x900x24 -nolisten tcp -ac &
pids+=("$!")

display_ready=false
for _ in {1..30}; do
  if xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
    display_ready=true
    break
  fi
  if ! kill -0 "${pids[0]}" 2>/dev/null; then
    echo "Xvfb exited before the display became ready." >&2
    exit 1
  fi
  sleep 1
done
if [[ "$display_ready" != true ]]; then
  echo "Timed out waiting for the Xvfb display." >&2
  exit 1
fi

dbus-run-session -- startlxqt &
pids+=("$!")
x11vnc -display "$DISPLAY" -localhost -nopw -forever -shared -rfbport 5900 &
pids+=("$!")
websockify --web=/usr/share/novnc 6080 127.0.0.1:5900 &
pids+=("$!")

wait -n "${pids[@]}"
