"""WEPY models docstring."""

from datetime import datetime
from flask_babelex import gettext as _
from invenio_db import db
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy_utils.types.choice import ChoiceType


class StatusPolicy(object):
    """Table status policy info"""

    NEW = 'N'
    """Record be created"""

    UPT = 'U'
    """Record be updated"""

    DEL = 'D'
    """Record be deleted"""

    descriptions = dict([
        (NEW, _('Created')),
        (UPT, _('Updated')),
        (DEL, _('Deleted')),
    ])

    @classmethod
    def describe(cls, policy):
        """
        Get <code>policy</code> describe info
        :param policy:
        :return: string
        """
        return cls.descriptions[policy] if cls.validates(policy) else None

    @classmethod
    def validates(cls, policy):
        """
        Check <code>policy</code> is valudated
        :param policy:
        :return: boolean true or false
        """
        return policy in [cls.NEW, cls.UPT, cls.DEL]


class TimestampMixin(object):
    """Timestamp model mix-in with fractional seconds support.
    SQLAlchemy-Utils timestamp model does not have support for
    fractional seconds.
    """
    STATUSPOLICY = [
        (StatusPolicy.NEW, _('Record has be created.')),
        (StatusPolicy.UPT, _('Record has be updated.')),
        (StatusPolicy.DEL, _('Record has be deleted.')),
    ]
    """Status policy choices."""

    status = db.Column(
        ChoiceType(STATUSPOLICY, impl=db.String(1)), nullable=False,
        default=StatusPolicy.NEW
    )
    """Policy for status to db record."""

    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    """Creation timestamp."""

    updated = db.Column(db.DateTime, nullable=False, default=datetime.now,
                        onupdate=datetime.now)
    """Updated timestamp."""


class WepyUser(db.Model, TimestampMixin):
    """Save wepy user base info"""

    __tablename__ = 'wepy_user'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment=_('record identifier')
    )
    """Record Identifier"""

    openid = db.Column(
        db.String(32),
        unique=True,
        index=True,
        nullable=False,
        comment=_('wepy user openid')
    )
    """WEPY User Openid"""

    session = db.Column(
        'session_key',
        db.String(32),
        unique=False,
        index=False,
        nullable=False,
        comment=_('wepy user session')
    )
    """WEPY User SessionKey"""

    unionid = db.Column(
        db.String(64),
        nullable=True,
        comment=_('wepy user unionid')
    )
    """WEPY User UnionID"""

    nickname = db.Column(
        'nick_name',
        db.String(64),
        nullable=True,
        comment=_('wepy user nickname')
    )
    """WEPY User nickname"""

    avatar = db.Column(
        'avatar_url',
        db.String(1024),
        nullable=True,
        comment=_('wepy user avatar')
    )
    """WEPY User avatar url"""

    gender = db.Column(
        db.Integer,
        nullable=True,
        default=0,
        comment=_('wepy user gender')
    )
    """WEPY User gender"""

    appid = db.Column(
        db.String(18),
        nullable=True,
        comment=_('the use is from the appid')
    )
    """WEPY User be from the appid"""

    @classmethod
    def create(cls, openid=None, session=None, **kwargs):
        """
        Create Wepy user info
        :param openid:
        :param session:
        :param kwargs:
        :return:
        """
        assert openid
        assert session

        with db.session.begin_nested():
            obj = cls(
                openid=openid,
                session=session,
                **kwargs
            )
            db.session.add(obj)
        db.session.commit()
        return obj

    def get_by_openid(self, openid=None):
        """
        Get Wepy User info by openid
        :param openid:
        :return:
        """
        try:
            if openid:
                return WepyUser.query.filter_by(openid=openid).one_or_none()
        except MultipleResultsFound:
            return None

    def update(self, openid=None, **kwargs):
        """
        Update Wepy User info
        :param openid:
        :param kwargs:
        :return:
        """
        assert openid

        with db.session.begin_nested():
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.merge(self)
        db.session.commit()
        return self
