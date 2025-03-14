import time
import json
from settings import log, CONFIG, req


class Base(object):
    def __init__(self, cookies: str = None):
        if not isinstance(cookies, str):
            raise TypeError('%s want a %s but got %s' %
                            (self.__class__, type(__name__), type(cookies)))
        self._cookie = cookies

    # set headers based on the game for check in
    def get_header(self, game='GI'):
        if game == 'GI':
            header = {
                'User-Agent': CONFIG.GI_WB_USER_AGENT,
                'Referer': CONFIG.GI_OS_REFERER_URL,
                'Accept-Encoding': 'gzip, deflate, br',
                'Cookie': self._cookie
            } 
        elif game == 'ZZZ':
            header = {
                'User-Agent': CONFIG.ZZZ_WB_USER_AGENT,
                'Referer': CONFIG.ZZZ_OS_REFERER_URL,
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Cookie': self._cookie,
                'x-rpc-signgame': 'zzz' # 11/10/2024 - additional request header for successful response
            }
        else:
            header = {
                'User-Agent': CONFIG.HI3_WB_USER_AGENT,
                'Referer': CONFIG.HI3_OS_REFERER_URL,
                'Accept-Encoding': 'gzip, deflate, br',
                'Cookie': self._cookie
            }
        
        return header


class Roles(Base):
    def get_awards(self, game='GI'):
        response = {}
        try:
            if game == 'GI':
                response = req.to_python(req.request(
                'get', CONFIG.GI_OS_REWARD_URL, headers=self.get_header(game=game)).text)
            elif game == 'ZZZ':
                response = req.to_python(req.request(
                'get', CONFIG.ZZZ_OS_REWARD_URL, headers=self.get_header(game=game)).text)
            else:
                response = req.to_python(req.request(
                'get', CONFIG.HI3_OS_REWARD_URL, headers=self.get_header(game=game)).text)
        except json.JSONDecodeError as e:
            raise Exception(e)
        
        # print('DEBUG: get_awards: ')
        return response

    def get_roles(self, game='GI'):
        response = {}
        try:
            if game == 'GI':
                response = req.to_python(req.request(
                'get', CONFIG.GI_OS_ROLE_URL, headers=self.get_header(game=game)).text)
            elif game == 'ZZZ':
                response = req.to_python(req.request(
                'get', CONFIG.ZZZ_OS_ROLE_URL, headers=self.get_header(game=game)).text)
            else:
                response = req.to_python(req.request(
                'get', CONFIG.HI3_OS_ROLE_URL, headers=self.get_header(game=game)).text)
            message = response['message']
        except Exception as e:
            raise Exception(e)
        if response.get(
            'retcode', 1) != 0 or response.get('data', None) is None:
            raise Exception(message)

        # print('DEBUG: get_roles: ')
        # print(response)
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

    def get_info(self,game='GI'):
        index = 0
        user_game_roles = Roles(self._cookie).get_roles(game=game)
        role_list = user_game_roles.get('data', {}).get('list', [])

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

        aid = self._cookie.split('account_id=')[1].split(';')[0]
        aid = str(aid).replace(
            str(aid)[1:len(aid)-1], ' ▓ ▓ ▓ ▓ ▓ ▓ ', 1)
        log.info(f'Checking in account id {aid}...')
        
        if game == 'GI':
            info_url = CONFIG.GI_OS_INFO_URL
        elif game == 'ZZZ':
            info_url = CONFIG.ZZZ_OS_INFO_URL
        else:
            info_url = CONFIG.HI3_OS_INFO_URL
        
        try:
            response = req.request(
                'get', info_url, headers=self.get_header(game=game)).text
            return req.to_python(response)
        except Exception as e:
            log.error('failure in get_info')
            raise

    def run(self, game="GI"):
        info_list = self.get_info(game=game)
        message_list = []
        
        if info_list:
            today = info_list.get('data',{}).get('today')
            total_sign_day = info_list.get('data',{}).get('total_sign_day')
            awards = Roles(self._cookie).get_awards(game=game).get('data',{}).get('awards')
            uid = str(self._uid).replace(
                str(self._uid)[1:7], ' ▓ ▓ ▓ ▓ ▓ ▓ ▓ ', 1)

            time.sleep(10)
            message = {
                'today': today,
                'region_name': self._region_name,
                'uid': uid,
                'level': self._level,
                'nick_name': self._nick_name,
                'total_sign_day': total_sign_day,
                'end': '',
            }
            
            if game == 'GI':
                job = 'Traveler'
            elif game == 'ZZZ':
                job = 'Proxy'
            else:
                job = 'Captain'
            
            if info_list.get('data',{}).get('is_sign') is True:
                message['award_name'] = awards[total_sign_day - 1]['name']
                message['award_cnt'] = awards[total_sign_day - 1]['cnt']
                message['status'] = f"{job}, you've already checked in today"
                message_list.append(self.message.format(**message))
                return ''.join(message_list)
            else:
                message['award_name'] = awards[total_sign_day]['name']
                message['award_cnt'] = awards[total_sign_day]['cnt']
            if info_list.get('data',{}).get('first_bind') is True:
                message['status'] = f'Please check in manually once'
                message_list.append(self.message.format(**message))
                return ''.join(message_list)

            if game == 'GI':
                OS_ACT_ID = CONFIG.GI_OS_ACT_ID
                OS_SIGN_URL = CONFIG.GI_OS_SIGN_URL
            elif game == 'ZZZ':
                OS_ACT_ID = CONFIG.ZZZ_OS_ACT_ID
                OS_SIGN_URL = CONFIG.ZZZ_OS_SIGN_URL
            else:
                OS_ACT_ID = CONFIG.HI3_OS_ACT_ID
                OS_SIGN_URL = CONFIG.HI3_OS_SIGN_URL
                
            data = {
                'act_id': OS_ACT_ID
            }         
            try:
                response = req.to_python(req.request(
                    'post', OS_SIGN_URL, headers=self.get_header(game=game),
                    data=json.dumps(data, ensure_ascii=False)).text)
            except Exception as e:
                raise
            code = response.get('retcode', 99999)
            # 0:      success
            # -5003:  already checked in
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