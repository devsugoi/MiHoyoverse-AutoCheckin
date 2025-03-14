import os
from dotenv import load_dotenv
from settings import log, CONFIG
from sign import Sign
from notify import Notify

load_dotenv()

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
    
    OS_COOKIE = ''
    token = ''

    GAMES = []
    
    if os.getenv('GI_OS_COOKIE') != '':
        GAMES.append('GI')
    if os.getenv('ZZZ_OS_COOKIE') != '':
        GAMES.append('ZZZ')
    if os.getenv('HI3_OS_COOKIE') != '':
        GAMES.append('HI3') 
        
    if os.getenv('DISCORD_WEBHOOK_SUMMARY') != '':
        allow_summary = True
        
    total_success_num: int = 0
    total_fail_num: int = 0  
    msg_summary = ''  
    
    for game in GAMES:
        if game == 'GI':
            OS_COOKIE = os.getenv('GI_OS_COOKIE')
        elif game == 'ZZZ':
            OS_COOKIE = os.getenv('ZZZ_OS_COOKIE')
        else:
            OS_COOKIE = os.getenv('HI3_OS_COOKIE')
        if OS_COOKIE == '':
            log.error("Cookie not set properly, please read a documentation on how to set and format your cookie.")
            raise Exception("Cookie failure")
        cookie_list = OS_COOKIE.split('#')
        log.info(f'Number of account cookies read: {len(cookie_list)}')
        log.info(f'Game: {game}')
        msg=f'**Game: {game}**'
        msg_list.append(msg)
        success_num = fail_num = 0
        for i in range(len(cookie_list)):
            log.info(f'Preparing NO.{i + 1} Account Check-In...')
            try:
                #ltoken = cookie_list[i].split('ltoken=')[1].split(';')[0]
                token = cookie_list[i].split('cookie_token=')[1].split(';')[0]
                msg = f'	NO.{i + 1} Account:{Sign(cookie_list[i]).run(game=game)}'
                msg_list.append(msg)
                success_num = success_num + 1
            except Exception as e:
                if not token:
                    log.error("Cookie token not found, please try to relog on the check-in page.")

                msg = f'	NO. {i + 1} Account:\n    {e}'
                msg_list.append(msg)
                fail_num = fail_num + 1
                log.error(msg)
                ret = -1
            continue
        msg=f'**  -Number of successful sign-ins: {success_num} \n  -Number of failed sign-ins: {fail_num}**'
        msg_list.append(msg)
        if allow_summary:
            if game == 'GI':
                msg_summary += f'\n  Genshin Impact: **{success_num}** Success and **{fail_num}** Fails'
            if game == 'ZZZ':
                msg_summary += f'\n  Zenless Zone Zero: **{success_num}** Success and **{fail_num}** Fails'
            if game == 'HI3':
                msg_summary += f'\n  Honkai Impact 3: **{success_num}** Success and **{fail_num}** Fails'
        
        total_success_num += success_num
        total_fail_num += fail_num
    
    # Color coding to easily determine in discord embed if there is an error
    if total_fail_num == 0:
        color = '2ecc71' #green
    elif total_fail_num > 0:
        color = 'f1c40f' #yellow
    elif ret != 0:
        color = 'eb3324' #red
    
    notify.send(status=f'\n  -Total number of successful sign-ins: {total_success_num} \n  -Total number of failed sign-ins: {total_fail_num}', msg=msg_list)
    
    if allow_summary:
        notify.send(msg=msg_summary, isSummary=allow_summary, embed_color=color)
    
    if total_fail_num > 0:
        notify.send(msg="Error occured @everyone", embed=False)
    if ret != 0:
        log.error('program terminated with errors')
        exit(ret)
    log.info('exit success')