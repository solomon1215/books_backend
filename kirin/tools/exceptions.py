# -*- coding: utf-8 -*-

import logging
import traceback
from inspect import currentframe
from kirin.tools.func import frame_codeinfo
from kirin.misc.response_code import ResponseCode as CODE

_logger = logging.getLogger(__name__)


def params_numeric_parsing_exception(**kwargs):
    try:
        for key, item in kwargs.items():
            kwargs[key] = [float(item)]

    except Exception as e:
        _logger.error(f"{traceback.print_exc()}")
        _logger.error(f"{e}")
        response = {
            'content': '请传入正确的price等numeric类型参数!'
        }
        response.update(CODE.CODE_406)
        return False, 406, response

    return True, 200, kwargs


def params_integer_parsing_exception(**kwargs):
    try:
        for key, item in kwargs.items():
            kwargs[key] = [int(item)]

    except Exception as e:
        _logger.error(f"{traceback.print_exc()}")
        _logger.error(f"{e}")
        response = {
            'content': '请传入正确的page, size等整数类型参数!'
        }
        response.update(CODE.CODE_406)
        return False, 406, response

    return True, 200, kwargs


# kept for backward compatibility
class except_orm(Exception):
    def __init__(self, name, value=None):
        if type(self) == except_orm:
            caller = frame_codeinfo(currentframe(), 1)
            _logger.warning(
                'except_orm is deprecated. Please use specific exceptions like UserError or AccessError. Caller: %s:%s',
                *caller)
        self.name = name
        self.value = value
        self.args = (name, value)


class UserError(except_orm):
    def __init__(self, msg):
        super(UserError, self).__init__(msg, value='')


# deprecated due to collision with builtins, kept for compatibility
Warning = UserError


class RedirectWarning(Exception):
    """ Warning with a possibility to redirect the user instead of simply
    diplaying the warning message.

    Should receive as parameters:
      :param int action_id: id of the action where to perform the redirection
      :param string button_text: text to put on the button that will trigger
          the redirection.
    """

    # using this RedirectWarning won't crash if used as an except_orm
    @property
    def name(self):
        return self.args[0]


class AccessDenied(Exception):
    """ Login/password error. no traceback.
    Example: When you try to log with a wrong password."""

    def __init__(self, message='Access denied'):
        super(AccessDenied, self).__init__(message)
        self.with_traceback(None)
        self.__cause__ = None
        self.traceback = ('', '', '')


class AccessError(except_orm):
    """ Access rights error.
    Example: When you try to read a record that you are not allowed to."""

    def __init__(self, msg):
        super(AccessError, self).__init__(msg)


class CacheMiss(except_orm, KeyError):
    """ Missing value(s) in cache.
    Example: When you try to read a value in a flushed cache."""

    def __init__(self, record, field):
        super(CacheMiss, self).__init__("%s.%s" % (str(record), field.name))


class MissingError(except_orm):
    """ Missing record(s).
    Example: When you try to write on a deleted record."""

    def __init__(self, msg):
        super(MissingError, self).__init__(msg)


class ValidationError(except_orm):
    """ Violation of python constraints
    Example: When you try to create a new user with a users which already exist in the db."""

    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class DeferredException(Exception):
    """ Exception object holding a traceback for asynchronous reporting.

    Some RPC calls (database creation and report generation) happen with
    an initial request followed by multiple, polling requests. This class
    is used to store the possible exception occuring in the thread serving
    the first request, and is then sent to a polling request.

    ('Traceback' is misleading, this is really a exc_info() triple.)
    """

    def __init__(self, msg, tb):
        self.message = msg
        self.traceback = tb


class QWebException(Exception):
    pass
