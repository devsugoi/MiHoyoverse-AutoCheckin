import time
import json
import re
from settings import log, CONFIG, req

# What each game calls the player, used in the check-in status message
JOB_TITLES = {'GI': 'Traveler', 'ZZZ': 'Proxy', 'HSR': 'Trailblazer', 'HI3': 'Captain'}

# HoYoLAB retcodes that mean the cookie can no longer authenticate:
#   -100  = cookies are not valid / expired
#   10001 = invalid cookies (variant used by some endpoints)
#   10103 = cookie is valid but has no HoYoLAB account bound to it
COOKIE_EXPIRED_RETCODES = (-100, 10001, 10103)


class CookieExpired(Exception):
    """The API rejected the account cookie - the user must log in again."""


class Base(object):
    def __init__(self, cookies: str = None):
        if not isinstance(cookies, str):
            raise TypeError('%s want a %s but got %s' %
                            (self.__class__, type(__name__), type(cookies)))
        self._cookie = cookies

    # set headers based on the game for check in
    def get_header(self, game='GI'):
        # per-game user agent / referer live in CONFIG as
        # <GAME>_WB_USER_AGENT and <GAME>_OS_REFERER_URL
        header = {
            'User-Agent': getattr(CONFIG, f'{game}_WB_USER_AGENT'),
            'Referer': getattr(CONFIG, f'{game}_OS_REFERER_URL'),
            'Accept-Encoding': 'gzip, deflate, br, zstd' if game in ('ZZZ', 'HSR') else 'gzip, deflate, br',
            'Cookie': self._cookie
        }
        if game == 'ZZZ':
            header['x-rpc-signgame'] = 'zzz' # 11/10/2024 - additional request header for successful response
        return header


class Roles(Base):
    def get_awards(self, game='GI'):
        try:
            response = req.to_python(req.request(
                'get', getattr(CONFIG, f'{game}_OS_REWARD_URL'),
                headers=self.get_header(game=game)).text)
        except json.JSONDecodeError as e:
            log.error(f'get_awards response was not valid JSON: {e}')
            return {}

        log.debug('get_awards response:')
        log.debug(response)
        return response

    def get_roles(self, game='GI'):
        # callers check retcode/data themselves, so failures just return
        # whatever we have (an empty dict when the request itself failed)
        response = {}
        try:
            response = req.to_python(req.request(
                'get', getattr(CONFIG, f'{game}_OS_ROLE_URL'),
                headers=self.get_header(game=game)).text)
        except Exception as e:
            log.error(f'get_roles request failed: {e}')
        return response


class Sign(Base):
    def __init__(self, cookies: str = None):
        super(Sign, self).__init__(cookies)
        self._region_name = ''
        self._uid = ''
        self._level = ''
        self._nick_name = ''
        #print("DEBUG: init")
    # def get_header(self): no override

    def _parse_account_id(self):
        # newer HoYoLAB cookies store the id under account_id_v2 instead of account_id
        for key in ('account_id', 'account_id_v2'):
            match = re.search(rf'{key}=([^;\s]+)', self._cookie)
            if match:
                return match.group(1)
        raise Exception('Cookie missing account_id or account_id_v2')

    def get_info(self,game='GI'):
        log.debug(f'get_info for {game}')
        index = 0
        user_game_roles = Roles(self._cookie).get_roles(game=game)
        log.debug('user_game_roles')
        log.debug(user_game_roles)
        if user_game_roles.get('retcode') in COOKIE_EXPIRED_RETCODES:
            raise CookieExpired(user_game_roles.get('message', 'Cookie expired'))
        role_list = user_game_roles.get('data', {}).get('list', [])
        if game == 'HSR': # HSR is a special case as it uses different keys for the role list
            role_list = [user_game_roles.get('data', {}).get('user_info', [])]
        # role list empty
        if not role_list:
            raise Exception(user_game_roles.get('message', 'Role list empty'))
        
        '''
            To display other server details, check through the list like this
        
            self._region_name_list = [(i.get('region_name', 'NA'))
                                  for i in role_list]
            self._uid_list = [(i.get('game_uid', 'NA')) for i in role_list]
            self._level_list = [(i.get('level', 'NA')) for i in role_list]
            self._nick_name_list = [(i.get('nickname', 'NA'))
                                for i in role_list]
        '''
        
        # If the account has characters on multiple servers, report the
        # highest-level one in the check-in message
        if len(role_list) != 1:
            highest_level = role_list[0].get('level', 'NA')
            
            for i in range(1, len(role_list)):
                if role_list[i].get('level', 'NA') > highest_level:
                    highest_level = role_list[i].get('level', 'NA')
                    index = i

        self._region_name = role_list[index].get('region_name', 'NA')
        self._uid = role_list[index].get('game_uid', 'NA')
        self._level = role_list[index].get('level', 'NA')
        self._nick_name = role_list[index].get('nickname', 'NA')            

        aid = self._parse_account_id()
        # mask the account id before logging: keep only the first and last character
        if len(aid) > 2:
            aid = str(aid).replace(str(aid)[1:len(aid)-1], ' ▓ ▓ ▓ ▓ ▓ ▓ ', 1)
        log.info(f'Checking in account id {aid}...')
        
        info_url = getattr(CONFIG, f'{game}_OS_INFO_URL')

        try:
            response = req.request(
                'get', info_url, headers=self.get_header(game=game)).text
            return req.to_python(response)
        except Exception:
            log.error('failure in get_info')
            # let the per-account handler in checkin.py log it and count the failure
            raise

    def run(self, game="GI"):
        info_list = self.get_info(game=game)
        if info_list.get('retcode') in COOKIE_EXPIRED_RETCODES:
            raise CookieExpired(info_list.get('message', 'Cookie expired'))
        message_list = []

        if info_list:
            today = info_list.get('data',{}).get('today')
            total_sign_day = info_list.get('data',{}).get('total_sign_day')
            awards = Roles(self._cookie).get_awards(game=game).get('data',{}).get('awards')
            # mask digits 2-7 of the UID before it goes into the notification
            uid = str(self._uid).replace(
                str(self._uid)[1:7], ' ▓ ▓ ▓ ▓ ▓ ▓ ▓ ', 1)

            message = {
                'today': today,
                'region_name': self._region_name,
                'uid': uid,
                'level': self._level,
                'nick_name': self._nick_name,
                'total_sign_day': total_sign_day,
                'end': '',
            }
            
            job = JOB_TITLES.get(game, 'Captain')

            # already signed today: total_sign_day includes today, so today's
            # award sits at index total_sign_day - 1
            if info_list.get('data',{}).get('is_sign') is True:
                message['award_name'] = awards[total_sign_day - 1]['name']
                message['award_cnt'] = awards[total_sign_day - 1]['cnt']
                message['status'] = f"{job}, you've already checked in today"
                message_list.append(self.message.format(**message))
                return ''.join(message_list)
            else:
                # not signed yet: total_sign_day only counts previous days, so
                # the award we're about to claim is at index total_sign_day
                message['award_name'] = awards[total_sign_day]['name']
                message['award_cnt'] = awards[total_sign_day]['cnt']
            if info_list.get('data',{}).get('first_bind') is True:
                message['status'] = f'Please check in manually once'
                message_list.append(self.message.format(**message))
                return ''.join(message_list)

            OS_ACT_ID = getattr(CONFIG, f'{game}_OS_ACT_ID')
            OS_SIGN_URL = getattr(CONFIG, f'{game}_OS_SIGN_URL')

            data = {
                'act_id': OS_ACT_ID
            }
            # space out the sign request so multiple accounts don't hammer the endpoint
            time.sleep(5)
            response = req.to_python(req.request(
                'post', OS_SIGN_URL, headers=self.get_header(game=game),
                data=json.dumps(data, ensure_ascii=False)).text)
            code = response.get('retcode', 99999)
            log.debug('Sign response:')
            log.debug(response)
            # 0:      success
            # -5003:  already checked in
            if code in COOKIE_EXPIRED_RETCODES:
                raise CookieExpired(response.get('message', 'Cookie expired'))
            # a geetest challenge in the response means HoYoLAB wants a captcha
            # solved - the check-in did NOT count even though retcode is 0
            if (response.get('data') or {}).get('gt'):
                raise Exception('Captcha (geetest) triggered on the sign endpoint; please check in manually today')
            if code != 0:
                message_list.append(response)
                return ''.join(message_list)
            message['total_sign_day'] = total_sign_day + 1
            message['status'] = response['message']
            message_list.append(self.message.format(**message))
            
        log.info('Check-in complete')
        return ''.join(message_list)

    @property
    def message(self):
        return CONFIG.MESSAGE_TEMPLATE