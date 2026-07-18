import os
from dotenv import load_dotenv
from settings import log, CONFIG
from sign import Sign, CookieExpired
from notify import Notify

load_dotenv()

# Display names used in the summary notification
GAME_NAMES = {
    'GI': 'Genshin Impact',
    'ZZZ': 'Zenless Zone Zero',
    'HI3': 'Honkai Impact 3',
    'HSR': 'Honkai Star Rail',
}

if __name__ == '__main__':
    log.info(f'Hoyo Check-In Helper v{CONFIG.GIH_VERSION}')
    log.info('If you fail to check in, please try to update!')
    
    notify = Notify()
    msg_list = []
    ret = success_num = fail_num = 0
    
    """
    HoYoLAB Community's COOKIE
    :param OS_COOKIE: HoYoLAB cookie(s) for one or more accounts.
        Separate cookies for multiple accounts with the hash symbol #
        e.g. cookie1text#cookie2text
        Do not surround cookies with quotes "" if using Github Secrets.
    """
    # Github Actions -> Settings -> Secrets
    # Ensure that the Name is exactly: OS_COOKIE
    # Value should look like: login_ticket=xxx; account_id=696969; cookie_token=xxxxx; ltoken=xxxx; ltuid=696969; mi18nLang=en-us; _MHYUUID=xxx
    #         Separate cookies for multiple accounts with the hash symbol #
    #         e.g. cookie1text#cookie2text
    
    # A game is only checked in when its cookie env var exists and is non-empty
    GAMES = [game for game in ('GI', 'ZZZ', 'HI3', 'HSR')
             if os.getenv(f'{game}_OS_COOKIE')]

    # os.getenv returns None when the var is missing, so bool() covers both
    # an unset and an empty DISCORD_WEBHOOK_SUMMARY
    allow_summary = bool(os.getenv('DISCORD_WEBHOOK_SUMMARY'))


    total_success_num: int = 0
    total_fail_num: int = 0
    msg_summary = ''
    expired_accounts = []
    try:
        for game in GAMES:
            OS_COOKIE = os.getenv(f'{game}_OS_COOKIE')
            if not OS_COOKIE:
                log.error("Cookie not set properly, please read a documentation on how to set and format your cookie.")
                raise Exception("Cookie failure")
            cookie_list = [cookie.strip() for cookie in OS_COOKIE.split('#') if cookie.strip()]
            log.info(f'Number of account cookies read: {len(cookie_list)}')
            log.info(f'Game: {game}')
            msg=f'**Game: {game}**'
            msg_list.append(msg)
            success_num = fail_num = 0
            
            for i, cookie in enumerate(cookie_list, 1):
                try:
                    log.info(f'Preparing NO.{i} Account Check-In...')
                    msg = f'	NO.{i} Account:{Sign(cookie).run(game=game)}'
                    msg_list.append(msg)
                    success_num = success_num + 1
                except CookieExpired as e:
                    log.error(f'Cookie expired for {game} account NO.{i}: {e}')
                    msg_list.append(f'Cookie expired for this account ({e}).')
                    expired_accounts.append(f'{game} NO.{i}')
                    fail_num = fail_num + 1
                except Exception as e:
                    log.debug('Error occurred during sign-in process:')
                    log.debug(e)
                    msg_list.append('Failed to check in this account.')
                    fail_num = fail_num + 1
                
            msg=f'**  -Number of successful sign-ins: {success_num} \n  -Number of failed sign-ins: {fail_num}**'
            msg_list.append(msg)
            if allow_summary:
                msg_summary += f'\n  {GAME_NAMES[game]}: **{success_num}** Success and **{fail_num}** Fails'
            
            total_success_num += success_num
            total_fail_num += fail_num
        
        # Color coding to easily determine in discord embed if there is an error
        if total_fail_num == 0:
            color = '2ecc71' #green
        else:
            color = 'f1c40f' #yellow
        
        notify.send(status=f'\n  -Total number of successful sign-ins: {total_success_num} \n  -Total number of failed sign-ins: {total_fail_num}', msg=msg_list)
        
        if allow_summary:
            notify.send(msg=msg_summary, isSummary=allow_summary, embed_color=color)
        
        if total_fail_num > 0:
            notify.send(msg="Error occured @everyone", isSummary=allow_summary, embed=False)

        # expired cookies need action from the user, so they get a distinct,
        # actionable alert instead of just a generic failure count
        if expired_accounts:
            notify.send(
                msg=f'@everyone Cookie expired for: {", ".join(expired_accounts)}. '
                    'Log in to hoyolab.com again and update the cookie in .env.',
                isSummary=allow_summary, embed=False)
    except Exception as e:
        log.error('An error occurred during the check-in process:')
        log.error(e)
        ret = 1
        # still try to tell Discord - a silent crash on a headless Pi would
        # otherwise go unnoticed until rewards stop arriving
        try:
            notify.send(status='CRASHED', msg=f'@everyone Check-in run crashed: {e}', embed=False)
        except Exception as notify_error:
            log.error(f'Failed to send crash notification: {notify_error}')

    if ret != 0:
        log.error('program terminated with errors')
        exit(ret)
    log.info('exit success')