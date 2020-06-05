"""model api"""

import requests as http

from datetime import datetime
from flask import current_app
from invenio_cache import current_cache as cache

from . import config
from .models import WepyUser
from .types import ObjDict


class WepyUserApi(object):
    """Wepy User api"""

    @classmethod
    def save(cls, openid=None, **kwargs):
        """
        Save Wepy user info
        :param openid:
        :param kwargs:
        :return:
        """
        assert openid

        try:
            cache.set(openid, kwargs)
            db_wepy_user = WepyUser()
            wepy_user = db_wepy_user.get_by_openid(openid)
            if wepy_user is None:
                wepy_user = WepyUser.create(openid, kwargs.pop('session'))
            else:
                wepy_user.update(openid, **kwargs)
        except Exception as ex:
            current_app.logger.error('WepyUserApi.save({}) Except: '.format(openid), ex)
        return wepy_user

    @classmethod
    def get(cls, openid=None, **kwargs):
        """
        Get Wepy user info
        :param openid:
        :param kwargs:
        :return:
        """
        assert openid

        try:
            db_wepy_user = WepyUser()
            wepy_user = db_wepy_user.get_by_openid(openid)
        except Exception as ex:
            current_app.logger.error('WepyUserApi.get({}) Except: '.format(openid), ex)
        return wepy_user


class WepyTokenApi(object):
    @classmethod
    def getAccessToken(cls, appid, with_ticket=None):
        token = cache.get('token-'+appid)
        if token:
            return True, {
                'from': 'cache',
                'access_token': token.access_token,
                'create_time': token.create_time,
                'jsapi_ticket': token.jsapi_ticket
            }
        appsecret = config.WXPY_APPID[appid]['appsecret']
        if with_ticket is None:
            with_ticket = config.WXPY_APPID[appid]['with_ticket']
        payload = {'appid': appid, 'secret': appsecret, 'grant_type': 'client_credential'}
        r = http.get(config.WXPY_GET_TOKEN_URL, params=payload)
        # https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html
        current_app.logger.debug("get_access_token[{}] result: {}".format(appid, r.text))
        if r and r.status_code == 200:
            resp = ObjDict(**r.json())
            if 'access_token' in resp:
                # success
                wepy_access_token = resp.access_token
                wepy_expire_in = resp.expires_in  # 凭证有效时间，单位：秒
                wepy_create_time = int(datetime.today().timestamp())
                if with_ticket:
                    query = {'access_token': wepy_access_token, 'type': 'jsapi'}
                    r = http.get(config.WXPY_GET_TICKET_URL, params=query)
                    # https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/JS-SDK.html#63
                    # 附录1-JS-SDK使用权限签名算法
                    # jsapi_ticket
                    # 生成签名之前必须先了解一下jsapi_ticket，jsapi_ticket是公众号用于调用微信JS接口的临时票据。
                    # 正常情况下，jsapi_ticket的有效期为7200秒，通过access_token来获取。由于获取jsapi_ticket的api
                    # 调用次数非常有限，频繁刷新jsapi_ticket会导致api调用受限，影响自身业务，
                    # 开发者必须在自己的服务全局缓存jsapi_ticket 。
                    # 1.参考以下文档获取access_token（有效期7200秒，开发者必须在自己的服务全局缓存access_token）：
                    # https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html
                    # 2.用第一步拿到的access_token 采用http GET方式请求获得jsapi_ticket（有效期7200秒，
                    # 开发者必须在自己的服务全局缓存jsapi_ticket）：
                    # https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=ACCESS_TOKEN&type=jsapi
                    # 成功返回如下JSON：
                    # {
                    #     "errcode": 0,
                    #     "errmsg": "ok",
                    #     "ticket": "bxLdikRXVbTPdHSM05e5u5sUoXNKd8-41ZO3MhKoyN5OfkWITDGgnr2fwJ0m9E8NYzWKVZvdVtaUgWvsdshFKA",
                    #     "expires_in": 7200
                    # }
                    # 获得jsapi_ticket之后，就可以生成JS - SDK权限验证的签名了。
                    if r and r.status_code == 200:
                        resp = ObjDict(**r.json())
                        if resp.errcode == 0:
                            wepy_jsapi_ticket = resp.ticket
                            token_info = {
                                'access_token': wepy_access_token,
                                'create_time': wepy_create_time,
                                'jsapi_ticket': wepy_jsapi_ticket
                            }
                        else:
                            return False, resp.errmsg
                    else:
                        return False, 'get ticket from wepy error'
                else:
                    token_info = {
                        'access_token': wepy_access_token,
                        'create_time': wepy_create_time,
                        'jsapi_ticket': ''
                    }
                WepyTokenApi.setAccessToken(appid, ObjDict(**token_info), expire_in=wepy_expire_in)
                return True, token_info
            else:
                return False, "[{}]{}".format(resp['errcode'], resp['errmsg'])
                current_app.logger.error("jscode2session[{}] error[{}]: {}".format(
                    appid, resp['errcode'], resp['errmsg']))
        else:
            return False, 'get access token from wepy error'

    @classmethod
    def setAccessToken(cls, appid, token, expire_in=7200):
        cache.set('token-'+appid, token, timeout=expire_in)
