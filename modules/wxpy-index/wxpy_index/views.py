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

from flask import Blueprint, current_app, jsonify, render_template, request, url_for, session
from flask_babelex import gettext as _
from invenio_cache import current_cache as cache

from . import config
from .api import WepyUserApi

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
    return jsonify({'code': 0, 'msg': _('success'), 'data': {'uri': url_for('wxpy_index_api.test_api'), 'method': request.method}})


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
