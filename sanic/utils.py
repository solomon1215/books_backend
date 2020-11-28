from importlib.util import module_from_spec, spec_from_file_location
from os import environ as os_environ
from re import findall as re_findall
from typing import Union

from .exceptions import LoadFileException


def str_to_bool(val: str) -> bool:
    """Takes string and tries to turn it into bool as human would do.

    If val is in case insensitive (
        "y", "yes", "yep", "yup", "t",
        "true", "on", "enable", "enabled", "1"
    ) returns True.
    If val is in case insensitive (
        "n", "no", "f", "false", "off", "disable", "disabled", "0"
    ) returns False.
    Else Raise ValueError."""

    val = val.lower()
    if val in {
        "y",
        "yes",
        "yep",
        "yup",
        "t",
        "true",
        "on",
        "enable",
        "enabled",
        "1",
    }:
        return True
    elif val in {"n", "no", "f", "false", "off", "disable", "disabled", "0"}:
        return False
    else:
        raise ValueError(f"Invalid truth value {val}")


def load_module_from_file_location(
    location: Union[bytes, str], encoding: str = "utf8", *args, **kwargs
):
    """Returns loaded module provided as a file path.

    :param args:
        Coresponds to importlib.util.spec_from_file_location location
        parameters,but with this differences:
        - It has to be of a string or bytes type.
        - You can also use here environment variables
          in format ${some_env_var}.
          Mark that $some_env_var will not be resolved as environment variable.
    :encoding:
        If location parameter is of a bytes type, then use this encoding
        to decode it into string.
    :param args:
        Coresponds to the rest of importlib.util.spec_from_file_location
        parameters.
    :param kwargs:
        Coresponds to the rest of importlib.util.spec_from_file_location
        parameters.

    For example You can:

        some_module = load_module_from_file_location(
            "some_module_name",
            "/some/path/${some_env_var}"
        )
    """

    # 1) Parse location.
    if isinstance(location, bytes):
        location = location.decode(encoding)

    # A) Check if location contains any environment variables
    #    in format ${some_env_var}.
    env_vars_in_location = set(re_findall(r"\${(.+?)}", location))

    # B) Check these variables exists in environment.
    not_defined_env_vars = env_vars_in_location.difference(os_environ.keys())
    if not_defined_env_vars:
        raise LoadFileException(
            "The following environment variables are not set: "
            f"{', '.join(not_defined_env_vars)}"
        )

    # C) Substitute them in location.
    for env_var in env_vars_in_location:
        location = location.replace("${" + env_var + "}", os_environ[env_var])

    # 2) Load and return module.
    name = location.split("/")[-1].split(".")[
        0
    ]  # get just the file name without path and .py extension
    _mod_spec = spec_from_file_location(name, location, *args, **kwargs)
    module = module_from_spec(_mod_spec)
    _mod_spec.loader.exec_module(module)  # type: ignore

    return module