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

"""weixin program develop"""

# TODO: This is an example file. Remove it if your package does not use any
# extra configuration variables.

WXPY_INDEX_DEFAULT_VALUE = 'foobar'
"""Default value for the application."""

WXPY_INDEX_BASE_TEMPLATE = 'wxpy_index/base.html'
"""Default base template for the demo page."""

CACHE_TYPE = 'redis'

CACHE_REDIS_URL = 'redis://wepy_redis:6379/1'
"""Redis location and database."""

CACHE_DEFAULT_TIMEOUT = 3600

WXPY_APPID = {
  'wxa55f028bafde4230': {
    'appsecret': '3956974f30fca6fe6ec7f5aa598e5b2c'
  }
}
WXPY_APPID_DEF = 'wxa55f028bafde4230'    # 日本語的学習
WXPY_SCHEMA = 'https:'
WXPY_BASE_URL = WXPY_SCHEMA + '//api.weixin.qq.com'
WXPY_CODE2SESSION_URL = WXPY_BASE_URL + '/sns/jscode2session'
