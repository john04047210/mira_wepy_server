"""model api"""

from flask import current_app
from invenio_cache import current_cache as cache

from .models import WepyUser


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
