#!/bin/sh
# Run from the repo directory no matter where cron invokes this from
cd "$(dirname "$0")"
# last_birthday_run.log is overwritten each run and catches even early crashes
# (missing modules etc.); rotating history lives in hoyohelper.log
/home/matt/.venv/bin/python Hoyoverse/birthday.py > last_birthday_run.log 2>&1
