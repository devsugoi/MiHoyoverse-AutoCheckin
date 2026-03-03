import os
from dotenv import load_dotenv
from settings import log, CONFIG
from sign import Sign
from notify import Notify
import threading

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
    
    if os.getenv('GI_OS_COOKIE') != '' and os.getenv('GI_OS_COOKIE') is not None:
        GAMES.append('GI')
    if os.getenv('ZZZ_OS_COOKIE') != '' and os.getenv('ZZZ_OS_COOKIE') is not None:
        GAMES.append('ZZZ')
    if os.getenv('HI3_OS_COOKIE') != '' and os.getenv('HI3_OS_COOKIE') is not None:
        GAMES.append('HI3') 
    if os.getenv('HSR_OS_COOKIE') != '' and os.getenv('HSR_OS_COOKIE') is not None:
        GAMES.append('HSR') 
        
    if os.getenv('DISCORD_WEBHOOK_SUMMARY') != '':
        allow_summary = True
        
    total_success_num: int = 0
    total_fail_num: int = 0  
    msg_summary = ''  
    try:
        for game in GAMES:
            if game == 'GI':
                OS_COOKIE = os.getenv('GI_OS_COOKIE')
            elif game == 'ZZZ':
                OS_COOKIE = os.getenv('ZZZ_OS_COOKIE')
            elif game == 'HSR':
                OS_COOKIE = os.getenv('HSR_OS_COOKIE')
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
                try:
                    log.info(f'Preparing NO.{i + 1} Account Check-In...')
                    msg = f'	NO.{i + 1} Account:{Sign(cookie_list[i]).run(game=game)}'
                    msg_list.append(msg)
                    success_num = success_num + 1
                except Exception as e:
                    log.debug('Error occurred during sign-in process:')
                    log.debug(e)
                    msg_list.append('Failed to check in this account.')
                    fail_num = fail_num + 1
                
            msg=f'**  -Number of successful sign-ins: {success_num} \n  -Number of failed sign-ins: {fail_num}**'
            msg_list.append(msg)
            if allow_summary:
                if game == 'GI':
                    msg_summary += f'\n  Genshin Impact: **{success_num}** Success and **{fail_num}** Fails'
                if game == 'ZZZ':
                    msg_summary += f'\n  Zenless Zone Zero: **{success_num}** Success and **{fail_num}** Fails'
                if game == 'HI3':
                    msg_summary += f'\n  Honkai Impact 3: **{success_num}** Success and **{fail_num}** Fails'
                if game == 'HSR':
                    msg_summary += f'\n  Honkai Star Rail: **{success_num}** Success and **{fail_num}** Fails'
            
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
            notify.send(msg="Error occured @everyone", isSummary=allow_summary, embed=False)
    except Exception as e:
        log.error('An error occurred during the check-in process:')
        log.error(e)
        ret = 1
        
    if ret != 0:
        log.error('program terminated with errors')
        exit(ret)
    log.info('exit success')