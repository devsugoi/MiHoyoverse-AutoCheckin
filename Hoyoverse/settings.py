# settings
import logging
import json
import os
import time
import requests
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from requests.exceptions import HTTPError

load_dotenv()

__all__ = ['log', 'CONFIG', 'req']

_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
_LOG_DATEFMT = '%Y-%m-%dT%H:%M:%S'

logging.basicConfig(
    level=logging.INFO,
    format=_LOG_FORMAT,
    datefmt=_LOG_DATEFMT)

log = logger = logging.getLogger()

# Also log to a rotating file in the repo root so cron runs can be diagnosed
# after the fact (cron discards stdout/stderr unless redirected)
_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'hoyohelper.log')
_file_handler = RotatingFileHandler(_LOG_FILE, maxBytes=512_000, backupCount=2, encoding='utf-8')
_file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT))
log.addHandler(_file_handler)

class _Config:
    GIH_VERSION = '4.1'
    # set DEBUG=1 in the environment (or .env) for verbose logging
    LOG_LEVEL = logging.DEBUG if os.getenv('DEBUG') else logging.INFO

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
    HI3_OS_SIGN_URL = 'https://sg-public-api.hoyolab.com/event/mani/sign'
    HI3_WB_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E150'

class HttpRequest(object):
    def __init__(self):
        # one shared session so TLS connections are reused across requests
        self._session = requests.Session()

    @staticmethod
    def to_python(json_str: str):
        return json.loads(json_str)

    @staticmethod
    def to_json(obj):
        return json.dumps(obj, indent=4, ensure_ascii=False)

    def request(self, method, url, max_retry: int = 2,
            params=None, data=None, json=None, headers=None, **kwargs):
        kwargs.setdefault('timeout', 30)  # don't let a hung connection stall the whole run
        # retries up to max_retry extra times; the for/else returns the response
        # as soon as one attempt completes without raising
        for i in range(max_retry + 1):
            try:
                # drop cookies the server set on earlier responses so they can't
                # override the per-account Cookie header or leak across accounts
                self._session.cookies.clear()
                response = self._session.request(method, url, params=params,
                    data=data, json=json, headers=headers, **kwargs)
                response.raise_for_status()  # treat 4xx/5xx as failures so they get retried
            except HTTPError as e:
                log.error(f'HTTP error:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            except Exception as e:
                log.error(f'Unknown error:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            else:
                return response
            if i < max_retry:
                time.sleep(2 * (i + 1))  # brief backoff so transient network blips can clear

        raise Exception(f'All {max_retry + 1} HTTP requests failed, die.')


req = HttpRequest()
CONFIG = _Config()
log.setLevel(CONFIG.LOG_LEVEL)

MESSAGE_TEMPLATE = '''
    {today:#^28}
    
    {nick_name} — Lv. {level}
    [{region_name}] {uid}
    Today's rewards: {award_name} × {award_cnt}
    Monthly Check-In count: {total_sign_day} days
    Check-in result: {status}
    
    {end:#^28}'''

CONFIG.MESSAGE_TEMPLATE = MESSAGE_TEMPLATE