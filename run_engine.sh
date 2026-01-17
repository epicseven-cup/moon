#!/usr/bin/env bash
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus
export GTK_CSS_PATH=~/.config/gtk-3.0

source /home/tomato/moon/.venv/bin/activate
exec python3 /home/tomato/moon/main.py
