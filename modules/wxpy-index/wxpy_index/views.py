# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2018 QiaoPeng.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.

"""weixin program develop."""

# TODO: This is an example file. Remove it if you do not need it, including
# the templates and static folders as well as the test case.

from __future__ import absolute_import, print_function

import requests as http

from datetime import datetime
from flask import Blueprint, current_app, jsonify, render_template, request, url_for, session
from flask_babelex import gettext as _
from invenio_cache import current_cache

from . import config
from .types import ObjDict
from .api import WepyUserApi, WepyTokenApi

blueprint = Blueprint(
    'wxpy_index',
    __name__,
    template_folder='templates',
    static_folder='static',
    # url_prefix='/wxpy',
)

blueprint_rest = Blueprint(
    'wxpy_index_api',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/')
@blueprint.route('/index')
def index():
    """Render a basic view."""
    return render_template(
        'wxpy_index/index.html',
        module_name=_('Wxpy-Index'))


@blueprint_rest.route('/test')
def test_api():
    """Return a basic json.

    access uri: /api/test
    """
    return jsonify({
        'code': 0,
        'msg': _('success'),
        'data': {
            'uri': url_for('wxpy_index_api.test_api'),
            'method': request.method
        }
    })


@blueprint_rest.route('/access_token')
def get_access_token_and_ticket():
    result = {'code': -1, 'msg': _('appid is empty')}
    try:
        with_ticket = int(request.args.get('with_ticket', '0'))
        appid = request.headers['APPID']
        if not appid:
            appid = request.args.get('appid', None)
        if not appid:
            return jsonify(result)
        token = WepyTokenApi.getAccessToken(appid)
        if token:
            return jsonify({
                'code': 0,
                'msg': _('success'),
                'data': {
                    'from': 'cache',
                    'access_token': token.access_token,
                    'create_time': token.create_time,
                    'jsapi_ticket': token.jsapi_ticket
                }
            })
        appsecret = config.WXPY_APPID[appid]['appsecret']
        payload = {'appid': appid, 'secret': appsecret, 'grant_type': 'client_credential'}
        r = http.get(config.WXPY_GET_TOKEN_URL, params=payload)
        # https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html
        current_app.logger.debug("get_access_token[{}] result: {}".format(appid, r.text))
        if r and r.status_code == 200:
            resp = ObjDict(**r.json())
            if 'access_token' in resp:
                # success
                wepy_access_token = resp.access_token
                wepy_expire_in = resp.expires_in    # 凭证有效时间，单位：秒
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
                            result = {
                                'code': 0,
                                'msg': _('success'),
                                'data': {
                                    'access_token': wepy_access_token,
                                    'create_time': wepy_create_time,
                                    'jsapi_ticket': wepy_jsapi_ticket
                                }
                            }
                        else:
                            return jsonify({
                                'code': -1,
                                'msg': resp.errmsg
                            })
                    else:
                        return jsonify({
                            'code': -1,
                            'msg': 'get ticket from wepy error'
                        })
                else:
                    result = {
                        'code': 0,
                        'msg': _('success'),
                        'data': {
                            'access_token': wepy_access_token,
                            'create_time': wepy_create_time,
                            'jsapi_ticket': ''
                        }
                    }
                WepyTokenApi.setAccessToken(appid, ObjDict(**result['data']), expire_in=wepy_expire_in)
            else:
                result['msg'] = "[{}]{}".format(resp['errcode'], resp['errmsg'])
                current_app.logger.error("jscode2session[{}] error[{}]: {}".format(
                    appid, resp['errcode'], resp['errmsg']))
        else:
            result['msg'] = 'get access token from wepy error'
    except Exception as ex:
        current_app.logger.error("get_access_token_and_ticket[{}] except: {}".format(appid, ex), ex)
        result['msg'] = "Exception: {}".format(ex)
    return jsonify(result)


@blueprint_rest.route('/jscode2session/<string:code>', methods=['GET'])
def jscode2session(code):
    """登录凭证校验。通过 wx.login() 接口获得临时登录凭证 code 换取 openId session 等信息

    https://developers.weixin.qq.com/miniprogram/dev/api/code2Session.html
    GET https://api.weixin.qq.com/sns/jscode2session?appid=APPID&secret=SECRET&js_code=JSCODE&grant_type=authorization_code
    请求参数
    属性        类型     默认值  必填  说明
    appid      string         是    小程序 appId
    secret     string         是    小程序 appSecret
    js_code    string         是    登录时获取的 code
    grant_type string         是    授权类型，此处只需填写 authorization_code
    """

    result = {'code': -1, 'msg': _('code is empty')}
    try:
        if code:
            appid = request.headers['APPID']
            if not appid:
                appid = config.WXPY_APPID_DEF
            appsecret = config.WXPY_APPID[appid]['appsecret']
            payload = {'appid': appid, 'secret': appsecret, 'js_code': code, 'grant_type': 'authorization_code'}
            r = http.get(config.WXPY_CODE2SESSION_URL, params=payload)
            current_app.logger.debug("jscode2session[{}] result: {}".format(appid, r.text))
            if r and r.status_code == 200:
                resp = r.json()
                if 'openid' in resp:
                    # success
                    wepy_openid = resp['openid']
                    wepy_session = resp['session_key']
                    wepy_unionid = resp['unionid'] if 'unionid' in resp else None
                    result = {
                        'code': 0,
                        'msg': _('success'),
                        'data': {
                            'openid': wepy_openid
                        }
                    }
                    session['openid'] = {
                            'openid': wepy_openid,
                            'session': wepy_session,
                            'unionid': wepy_unionid
                        }
                    WepyUserApi.save(wepy_openid, **{'session': wepy_session, 'appid': appid})
                else:
                    result['msg'] = "[{}]{}".format(resp['errcode'], resp['errmsg'])
                    current_app.logger.error("jscode2session[{}] error[{}]: {}".format(
                        appid, resp['errcode'], resp['errmsg']))
    except Exception as ex:
        current_app.logger.error("jscode2session[{}] except: {}".format(appid, ex), ex)
        result['msg'] = "Exception: {}".format(ex)
    return jsonify(result)


@blueprint_rest.route('/user/me', methods=['GET', 'PUT'])
def userinfo():
    """Get or Update wepy userinfo (nickname, avatar)"""

    result = {'code': -1, 'msg': _('params is empty')}
    try:
        appid = request.headers['APPID']
        openid = request.headers['OPENID']
        if not appid:
            result = {'code': -1, 'msg': _('appid is empty')}
        if not openid:
            result = {'code': -1, 'msg': _('openid is empty')}
        if appid and openid:
            user_info = WepyUserApi.get(openid)
            if user_info is not None and request.method == 'PUT':
                payload = request.get_json()
                user_info = WepyUserApi.save(
                    openid,
                    **{'nickname': payload['nickName'],
                       'avatar': payload['avatarUrl'],
                       'gender': payload['gender']}
                )
            if user_info is not None and user_info.nickname is not None:
                result = {
                    'code': 0 if user_info.nickname else -2,
                    'msg': _('success'),
                    'data': {
                        'nickName': user_info.nickname,
                        'avatarUrl': user_info.avatar,
                        'gender': user_info.gender
                    }
                }
            else:
                result = {
                    'code': -2,
                    'msg': _('data not exist')
                }

    except Exception as ex:
        current_app.logger.error('userinfo{} except: {}'.format(openid, ex), ex)
        result['msg'] = "Exception: {}".format(ex)
    return jsonify(result)


@blueprint_rest.route('/cache/test', methods=['GET'])
def test_cache_ui():
    with_update = request.args.get('update', '0')
    with_delete = request.args.get('delete', '0')
    with_update = True if int(with_update) else False
    with_delete = True if int(with_delete) else False

    if with_update:
        if with_delete:
            current_cache.delete('test_key')
        current_cache.set('test_key', ObjDict(**{
            'device_id': 12345678,
            'cache_time': datetime.today()
        }), timeout=60)

    test_value = current_cache.get('test_key')
    if not test_value:
        cache_rtn = current_cache.set('test_key', ObjDict(**{
            'device_id': 12345678,
            'cache_time': datetime.today()
        }), timeout=60)
        if not cache_rtn:
            return jsonify({
                'code': -1,
                'msg': 'cache set error'
            })
        test_value = current_cache.get('test_key')
    return jsonify({
        'code': 0,
        'msg': 'success',
        'data': {
            'dev_id': test_value.device_id,
            'store_time': test_value.cache_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


@blueprint_rest.route('/cache/test', methods=['DELETE'])
def del_test_cache_ui():
    current_cache.delete('test_key')
    return jsonify({
        'code': 0,
        'msg': 'success'
    })
