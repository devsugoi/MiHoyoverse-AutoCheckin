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
    
    # Check first if an environment variable belonging for the birthday script exists
    BIRTHDAYS = os.getenv('BIRTHDAYS')
    if not BIRTHDAYS:
        log.error("Birthday not set properly, please read the documentation on how to set up the birthdays.")
        raise Exception("Birthday set-up failure")

    # os.getenv returns None when the var is missing, so bool() covers both
    # an unset and an empty DISCORD_WEBHOOK_SUMMARY
    allow_summary = bool(os.getenv('DISCORD_WEBHOOK_SUMMARY'))
    
    # Divide the birthday list in the environment folder
    bday_list = BIRTHDAYS.split('#')
    log.info(f'Number of birthdays read: {len(bday_list)}')
    
    # Each entry in BIRTHDAYS is one of:
    #   <discord_user_id>;<YYYY/MM/DD>  -> birthday greeting (year is ignored, only MM/DD is compared)
    #   !;<date>;<message>              -> custom announcement; date is YYYY/MM/DD for a one-off,
    #                                      or XXXX/MM/DD to repeat it every year
    for bday in bday_list:
        bday_info = bday.split(';')
        # Check if the item is not for ordinary birthday but for a custom announcement
        if bday_info[0] == '!' and (today.strftime("%Y/%m/%d") == bday_info[1].strip()
                                    or (bday_info[1].strip()[:4] == "XXXX" and today.strftime("%m/%d") == bday_info[1].strip()[-5:])):
            notify.send(app='Birthday Greeting Helper', status='', msg=bday_info[2].strip(),embed=False, isSummary=allow_summary)

        elif today.strftime("%m/%d") == bday_info[1].strip()[-5:]:
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
                f'mga lode @everyone batiin nyo naman ng Happy Birthday si <@{bday_info[0]}>',
                f'Uy lods <@{bday_info[0]}>, isa ka na namang taong gulang. Happy Birthday!',
                f'Petmalu lods <@{bday_info[0]}>, Happy Birthday!',
                f'Happy Birthday idol <@{bday_info[0]}>, sana all may birthday ngayon',
                f'Lods <@{bday_info[0]}> saan ang handaan? Happy Birthday!',
                f'Libre mo naman kami lods <@{bday_info[0]}>, birthday mo daw eh',
                f'Wish ko lang masaya ka lods <@{bday_info[0]}>, Happy Birthday!',
                f'Isang taon na naman ang nadagdag sa pagka-lodi mo <@{bday_info[0]}>, HBD!',
                f'Attention mga lods @everyone, birthday ngayon ni idol <@{bday_info[0]}>!',
                f'Sabi ng kalendaryo ko bday mo raw ngayon lods <@{bday_info[0]}>, Happy Birthday!',
                f'Happy Birthday lods <@{bday_info[0]}>! Sana marami kang matanggap na regalo',
                f'Walang tatalo sa lodi kong si <@{bday_info[0]}>, Happy Birthday boss!',
                f'Level up na naman si lods <@{bday_info[0]}>! Happy Birthday!',
                f'Kain tayo lods <@{bday_info[0]}>! Birthday mo naman diba? HBD!'
            ]
            notify.send(app='Birthday Greeting Helper', status='', msg=random.choice(greeting_list),embed=False, isSummary=allow_summary)
    