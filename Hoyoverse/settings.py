# settings
import logging
import json
import requests
import os
from dotenv import load_dotenv
from requests.exceptions import HTTPError

load_dotenv()

__all__ = ['log', 'CONFIG', 'req']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S')

log = logger = logging

class _Config:
    GIH_VERSION = '4.0'
    LOG_LEVEL = logging.INFO
    # LOG_LEVEL = logging.DEBUG

    # HoYoLAB
    LANG = 'en-us'
    
    # Genshin
    GI_OS_ACT_ID = 'e202102251931481'
    GI_GAME_BIZ = 'hk4e_global'
    GI_OS_REFERER_URL = 'https://webstatic-sea.mihoyo.com/ys/event/signin-sea/index.html?act_id={}'.format(GI_OS_ACT_ID)
    GI_OS_REWARD_URL = 'https://sg-hk4e-api.mihoyo.com/event/sol/home?lang={}&act_id={}'.format(LANG, GI_OS_ACT_ID)
    GI_OS_ROLE_URL = 'https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format(GI_GAME_BIZ)
    GI_OS_INFO_URL = 'https://sg-hk4e-api.mihoyo.com/event/sol/info?lang={}&act_id={}'.format(LANG, GI_OS_ACT_ID)
    GI_OS_SIGN_URL = 'https://sg-hk4e-api.mihoyo.com/event/sol/sign?lang={}'.format(LANG)
    GI_WB_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E150'
    
    # ZZZ
    ZZZ_OS_ACT_ID = 'e202406031448091'
    ZZZ_GAME_BIZ = 'nap_global'
    ZZZ_OS_REFERER_URL = 'https://act.hoyolab.com/bbs/event/signin/zzz/{}.html?act_id={}'.format(ZZZ_OS_ACT_ID, ZZZ_OS_ACT_ID) 
    ZZZ_OS_REWARD_URL = 'https://sg-public-api.hoyolab.com/event/luna/zzz/os/home?lang={}&act_id={}'.format(LANG, ZZZ_OS_ACT_ID) 
    ZZZ_OS_ROLE_URL = 'https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format(ZZZ_GAME_BIZ) 
    ZZZ_OS_INFO_URL = 'https://sg-public-api.hoyolab.com/event/luna/zzz/os/info?lang={}&act_id={}'.format(LANG, ZZZ_OS_ACT_ID) 
    ZZZ_OS_SIGN_URL = 'https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/sign?lang={}'.format(LANG) 
    ZZZ_WB_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E150'
    
    # HSR
    HSR_OS_ACT_ID = 'e202303301540311'
    HSR_OS_REFERER_URL = 'https://act.hoyolab.com/bbs/event/signin/hkrpg/{}.html?act_id={}'.format(HSR_OS_ACT_ID,HSR_OS_ACT_ID)
    HSR_OS_REWARD_URL = 'https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/home?lang={}&act_id={}'.format(LANG, HSR_OS_ACT_ID)
    HSR_OS_ROLE_URL = 'https://bbs-api-os.hoyolab.com/community/painter/wapi/user/full'
    HSR_OS_INFO_URL = 'https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/info?lang={}&act_id={}'.format(LANG, HSR_OS_ACT_ID) 
    HSR_OS_SIGN_URL = 'https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/sign'
    HSR_WB_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E150'
    
    # HI3
    HI3_OS_ACT_ID = 'e202110291205111'
    HI3_GAME_BIZ = 'bh3_global'
    HI3_OS_REFERER_URL = 'https://webstatic-sea.mihoyo.com/bbs/event/signin-bh3/index.html?act_id={}'.format(HI3_OS_ACT_ID)
    HI3_OS_REWARD_URL = 'https://sg-public-api.hoyolab.com/event/mani/home?lang={}&act_id={}'.format(LANG, HI3_OS_ACT_ID) #May-05-2024 - Changed from api-os-takumi.mihoyo.com
    HI3_OS_ROLE_URL = 'https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format(HI3_GAME_BIZ)
    HI3_OS_INFO_URL = 'https://sg-public-api.hoyolab.com/event/mani/info?lang={}&act_id={}'.format(LANG, HI3_OS_ACT_ID) #May-05-2024 - Changed from api-os-takumi.mihoyo.com
    HI3_OS_SIGN_URL = 'https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/info?lang=en-us&act_id=e202303301540311={}'.format(LANG) #May-09-2024 - Changed from api-os-takumi.mihoyo.com
    HI3_WB_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E150'

class HttpRequest(object):
    @staticmethod
    def to_python(json_str: str):
        return json.loads(json_str)

    @staticmethod
    def to_json(obj):
        return json.dumps(obj, indent=4, ensure_ascii=False)

    def request(self, method, url, max_retry: int = 2,
            params=None, data=None, json=None, headers=None, **kwargs):
        for i in range(max_retry + 1):
            try:
                s = requests.Session()
                response = s.request(method, url, params=params,
                    data=data, json=json, headers=headers, **kwargs)
            except HTTPError as e:
                log.error(f'HTTP error:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            except KeyError as e:
                log.error(f'Wrong response:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            except Exception as e:
                log.error(f'Unknown error:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            else:
                return response

        raise Exception(f'All {max_retry + 1} HTTP requests failed, die.')


req = HttpRequest()
CONFIG = _Config()
log.basicConfig(level=CONFIG.LOG_LEVEL)
if os.getenv('ZZZ_USER_AGENT'):
    CONFIG.WB_USER_AGENT = os.getenv('ZZZ_USER_AGENT')

MESSAGE_TEMPLATE = '''
    {today:#^28}
    
    {nick_name} — Lv. {level}
    [{region_name}] {uid}
    Today's rewards: {award_name} × {award_cnt}
    Monthly Check-In count: {total_sign_day} days
    Check-in result: {status}
    
    {end:#^28}'''

CONFIG.MESSAGE_TEMPLATE = MESSAGE_TEMPLATE