# MiHoyoverse-AutoCheckin

A small Python bot that automatically claims the **daily HoYoLAB check-in rewards** for Hoyoverse games, so you never miss a day of login rewards. It supports multiple accounts per game and reports the results to Discord through webhooks.

It also ships with a bonus **Birthday Greeting Helper** that posts a randomized birthday greeting (or a custom announcement) to a Discord channel when someone's special day comes up.

## Supported games

| Game | Env variable |
| --- | --- |
| Genshin Impact | `GI_OS_COOKIE` |
| Honkai: Star Rail | `HSR_OS_COOKIE` |
| Zenless Zone Zero | `ZZZ_OS_COOKIE` |
| Honkai Impact 3rd | `HI3_OS_COOKIE` |

A game is only checked in when its cookie variable is set — just leave out the ones you don't play.

## How it works

1. For each configured game, the script logs in to the HoYoLAB check-in endpoint using your account cookie(s).
2. It claims the daily reward and collects the result (reward name, monthly check-in count, account info).
3. It sends a Discord notification with the per-account details, a color-coded summary (green = all good, yellow = something failed), and pings `@everyone` if any sign-in failed.

## Requirements

- Python 3.11+
- Dependencies:

```
pip install requests python-dotenv discord-webhook
```

## Configuration

Create a `.env` file in the project root (or set the variables as environment variables / GitHub Actions secrets):

| Variable | Required | Description |
| --- | --- | --- |
| `GI_OS_COOKIE`, `HSR_OS_COOKIE`, `ZZZ_OS_COOKIE`, `HI3_OS_COOKIE` | at least one | HoYoLAB cookie(s) for the game. Separate multiple accounts with `#`. |
| `DISCORD_WEBHOOK` | optional | Webhook that receives the detailed check-in results. |
| `DISCORD_WEBHOOK_SUMMARY` | optional | A second webhook for a short summary, keeping the main channel clean. |
| `PUSH_CONFIG` | optional | JSON config for pushing to a custom notification API (see [notify.py](Hoyoverse/notify.py)). |
| `BIRTHDAYS` | for birthday helper | Birthday/announcement entries, separated by `#` (format below). |

### Getting your cookie

1. Log in to [hoyolab.com](https://www.hoyolab.com/) in your browser.
2. Open the developer tools (F12) → Network tab, refresh, and copy the `Cookie` header from any request.
3. It should look something like:

```
login_ticket=xxx; account_id=696969; cookie_token=xxxxx; ltoken=xxxx; ltuid=696969; mi18nLang=en-us; _MHYUUID=xxx
```

For multiple accounts, join the cookies with a `#`: `cookie1text#cookie2text`. Do not wrap the value in quotes if you're using GitHub Secrets.

### Birthday helper format

Each `#`-separated entry in `BIRTHDAYS` is one of:

- `<discord_user_id>;<YYYY/MM/DD>` — posts a random birthday greeting mentioning that user (only month/day is compared, the year is ignored).
- `!;<YYYY/MM/DD>;<message>` — posts a one-off custom announcement on that exact date.
- `!;XXXX/MM/DD;<message>` — posts the announcement every year on that month/day.

## Usage

Run everything (check-in + birthday helper):

```
python HoyoHelperStart.py
```

Or run the pieces individually:

```
python Hoyoverse/Hoyo-os.py       # daily check-in only
python Hoyoverse/Birthday-os.py   # birthday greetings only
```

Since the rewards reset daily, you'll want to schedule it — e.g. with cron on a Raspberry Pi / Linux box:

```
# crontab -e
0 16 * * * cd /path/to/MiHoyoverse-AutoCheckin && python Hoyoverse/Hoyo-os.py
0 8  * * * cd /path/to/MiHoyoverse-AutoCheckin && python Hoyoverse/Birthday-os.py
```

## Project structure

| File | Purpose |
| --- | --- |
| [HoyoHelperStart.py](HoyoHelperStart.py) | Entry point that runs the check-in and birthday scripts. |
| [Hoyoverse/Hoyo-os.py](Hoyoverse/Hoyo-os.py) | Main check-in driver: loops over games and accounts, tallies results, sends notifications. |
| [Hoyoverse/sign.py](Hoyoverse/sign.py) | The actual sign-in logic against the HoYoLAB API. |
| [Hoyoverse/settings.py](Hoyoverse/settings.py) | Per-game API endpoints, headers, logging, and a retrying HTTP client. |
| [Hoyoverse/notify.py](Hoyoverse/notify.py) | Discord webhook + custom push notification handler. |
| [Hoyoverse/Birthday-os.py](Hoyoverse/Birthday-os.py) | Birthday greeting / announcement helper. |

## Credits & disclaimer

This started from an existing open-source check-in script (source since lost) that I have heavily modified for my own use. It's a personal project shared as-is — if you're interested in a cleaned-up version for general use, let me know and I might consider recoding the whole thing.

Use at your own risk: automating check-ins involves your HoYoLAB account cookie, so keep your `.env` private and never commit it.
