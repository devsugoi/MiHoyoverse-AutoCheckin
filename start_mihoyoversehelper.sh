#!/bin/sh
# Run from the repo directory no matter where cron invokes this from
cd "$(dirname "$0")"
# last_checkin_run.log is overwritten each run and catches even early crashes
# (missing modules etc.); rotating history lives in hoyohelper.log
/home/matt/.venv/bin/python Hoyoverse/Hoyo-os.py > last_checkin_run.log 2>&1
