"""Runner for assignment sanity checkers, including PyTA.

Copyright (c) 2023 Anya Tafliovich
"""

import sys
from copy import deepcopy
from typing import Any

ERROR_MSG = 'The call {}({}) caused an error: {}'
TYPE_ERROR_MSG = '{} should return a {}, but returned {}.'


def ensure_no_io(modulename: str) -> None:
    """Mock built-in functions input and print, so that they raise
    exceptions.

    """

    test_module = sys.modules[modulename]
    setattr(test_module, "input", _mock_disallow("input"))
    setattr(test_module, "print", _mock_disallow("print"))


def run_pyta(filename: str, config_file: str) -> None:
    """Run PYTA with configuration config_file on the file named filename.

    """

    sys.path.insert(0, 'pyta')
    import python_ta
    python_ta.check_all(filename, config=config_file)


def type_check_simple(func: callable, args: list,
                      expected: type) -> tuple[bool, Any]:
    """Check if func(args) returns a result of type expected.

    Return (True, result-of-call) if the check succeeds.
    Return (False, error-or-failure-message) if anything goes wrong.
    """

    try:
        args_copy = deepcopy(args)
        returned = func(*args_copy)
    except Exception as exn:
        return (False, error_message(func, args, exn))

    if isinstance(returned, expected):
        return (True, returned)

    return (False,
            type_error_message(func.__name__, expected.__name__, returned))


def type_check_full(func: callable, args: list,
                    checker_function: callable) -> tuple[bool, Any]:
    """Run checker_function on func(args).

    Pre: checker_function is also a type-checker (i.e. returns tuple
          in the same format).

    Return (True, result-of-call-func-args) if the check succeeds.
    Return (False, error-or-failure-message) if anything goes wrong.
    """

    try:
        args_copy = deepcopy(args)
        returned = func(*args_copy)
    except Exception as exn:
        return (False, error_message(func, args, exn))

    return checker_function(returned)


def type_error_message(func: str, expected: str, got: object) -> str:
    """Return an error message for function func returning got, where the
    correct return type is expected.

    """

    return TYPE_ERROR_MSG.format(func, expected, got)


def error_message(func: callable, args: list,
                  error: Exception) -> str:
    """Return an error message: func(args) raised an error."""

    return ERROR_MSG.format(func.__name__, ','.join(map(str, args)),
                            error)


def returns_list_of(func: callable, args: list, typ: type) -> tuple[bool, Any]:
    """Check if func(args) returns a list of elements of type typ.

    Return (True, result-of-call) if the check succeeds.
    Return (False, error-or-failure-message) if anything goes wrong.

    """

    result = type_check_simple(func, args, list)
    if not result[0]:
        return (False, result[1])

    msg = type_error_message(func.__name__, f'list of {typ.__name__}s',
                             result[1])
    for item in result[1]:
        if not isinstance(item, typ):
            return (False, msg)

    return (True, result[1])


def returns_tuple_of(func: callable, args: list, tup: tuple) -> tuple[bool, Any]:
    """Check if func(args) returns a tuple of elements of the same types
    as in tup.

    tup is a tuple of types.

    Return (True, result-of-call) if the check succeeds.
    Return (False, error-or-failure-message) if anything goes wrong.

    """

    result = type_check_simple(func, args, tuple)
    if not result[0]:
        return (False, result[1])

    types = ', '.join([typ.__name__ for typ in tup])
    msg = type_error_message(func.__name__,
                             f'tuple of ({types})',
                             result[1])
    if len(result[1]) != len(tup):
        return (False, msg)

    for i in range(len(result[1])):
        if not isinstance(result[1][i], tup[i]):
            return (False, msg)

    return (True, result[1])


def returns_dict_of(func: callable, args: list, key_type: type,
                    value_type: type) -> tuple[bool, Any]:
    """Check if func(args) returns a dict that maps objects of type
    key_type to obects of type value_type.

    Return (True, result-of-call) if the check succeeds.
    Return (False, error-or-failure-message) if anything goes wrong.

    """

    result = type_check_simple(func, args, dict)
    if not result[0]:
        return (False, result[1])

    msg = type_error_message(
        func.__name__,
        f'dict of {key_type.__name__}s to {value_type.__name__}s',
        result[1])

    for key, value in result[1].items():
        if not isinstance(key, key_type) or not isinstance(value, value_type):
            return (False, msg)

    return (True, result[1])


def returns_dict_keys_from(func: callable, args: list, keyset: set):
    """Check if func(args) returns a dict whose keys are all from keyset.

    Return (True, result-of-call) if the check succeeds.
    Return (False, error-or-failure-message) if anything goes wrong.

    """

    result = type_check_simple(func, args, dict)
    if not result[0]:
        return (False, result[1])

    msg = error_message(func, args, 'Incorrect key: {}. Allowed keys are: {}')

    for key in result[1]:
        if key not in keyset:
            return (False, msg.format(key, keyset))

    return (True, result[1])


def returns_dict_keys(func: callable, args: list, keyset: set):
    """Check if func(args) returns a dict whose keys are exactly those
    from keyset.

    Return (True, result-of-call) if the check succeeds.
    Return (False, error-or-failure-message) if anything goes wrong.

    """

    result = type_check_simple(func, args, dict)
    if not result[0]:
        return (False, result[1])

    actual_keyset = set(result[1].keys())
    msg = error_message(
        func,
        args,
        f'Incorrect keys: {actual_keyset}. Keys must be: {keyset}')
    if actual_keyset != keyset:
        return (False, msg)

    return (True, result[1])


def _mock_disallow(func_name: str):
    """Raise an Exception saying that use of function func_name is not
    allowed.

    """

    def mocker(*args):
        raise Exception(
            f'The use of function {func_name} is not allowed.')

    return mocker
