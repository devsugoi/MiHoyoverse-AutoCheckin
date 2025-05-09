import random
import os
from dotenv import load_dotenv
from datetime import datetime
from settings import log, CONFIG
from notify import Notify

load_dotenv()

if __name__ == '__main__':
    log.info(f'Birthday Greeting Helper v{CONFIG.GIH_VERSION}')
    notify = Notify()
    bday_list = []
    today = datetime.now()
    
    if os.getenv('BIRTHDAYS') != '':
        BIRTHDAYS = os.getenv('BIRTHDAYS')
    else:
        log.error("Birthday not set properly, please read the documentation on how to set up the birthdays.")
        raise Exception("Birthday set-up failure")
    
    if os.getenv('DISCORD_WEBHOOK_SUMMARY') != '':
        allow_summary = True
    
    bday_list = BIRTHDAYS.split('#')
    log.info(f'Number of birthdays read: {len(bday_list)}')
    
    for bday in bday_list:
        bday_info = bday.split(';')
        if today.strftime("%m/%d") == bday_info[1][-5:]:
            greeting_list = [
                f'Happy Birthday lods <@{bday_info[0]}>!',
                f'Balita ko bday mo lode ah <@{bday_info[0]}>',
                f'Boss <@{bday_info[0]}> happy birthday boss',
                f'bday mo ba lods? <@{bday_info[0]}>',
                f'Ay bday nga pala ni lode <@{bday_info[0]}>',
                f'May nagsabi sakin bday mo ngayon lods <@{bday_info[0]}>',
                f'HBD <@{bday_info[0]}>',
                f'Ako na maunang babati sayo lods <@{bday_info[0]}> Happy Birthday',
                f'Maligayang Birthday <@{bday_info[0]}>',
                f'Happy na Birthday mo pa <@{bday_info[0]}>',
                f'Birthday na ni <@{bday_info[0]}> mga lodi @everyone',
                f'mga lode @everyone batiin nyo naman ng Happy Birthday si <@{bday_info[0]}>'
            ]
            notify.send(app='Birthday Greeting Helper', status='', msg=random.choice(greeting_list),embed=False, isSummary=allow_summary)
    