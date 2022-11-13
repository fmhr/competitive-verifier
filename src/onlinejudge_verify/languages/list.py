import pathlib
from logging import getLogger
from typing import Optional

from onlinejudge_verify.config import get_config
from onlinejudge_verify.languages.models import Language

logger = getLogger(__name__)

_dict: Optional[dict[str, Language]] = None


def _get_dict() -> dict[str, Language]:
    from onlinejudge_verify.languages.cplusplus import CPlusPlusLanguage
    from onlinejudge_verify.languages.go import GoLanguage
    from onlinejudge_verify.languages.haskell import HaskellLanguage
    from onlinejudge_verify.languages.java import JavaLanguage
    from onlinejudge_verify.languages.nim import NimLanguage
    from onlinejudge_verify.languages.python import PythonLanguage
    from onlinejudge_verify.languages.ruby import RubyLanguage
    from onlinejudge_verify.languages.rust import RustLanguage
    from onlinejudge_verify.languages.user_defined import UserDefinedLanguage

    global _dict  # pylint: disable=invalid-name
    if _dict is None:
        _dict = {}
        _dict[".cpp"] = CPlusPlusLanguage()
        _dict[".hpp"] = _dict[".cpp"]
        _dict[".cc"] = _dict[".cpp"]
        _dict[".h"] = _dict[".cpp"]
        _dict[".nim"] = NimLanguage()
        _dict[".py"] = PythonLanguage()
        _dict[".hs"] = HaskellLanguage()
        _dict[".ruby"] = RubyLanguage()
        _dict[".go"] = GoLanguage()
        _dict[".java"] = JavaLanguage()
        _dict[".rs"] = RustLanguage()

        for ext, config in get_config().get("languages", {}).items():
            if "." + ext in _dict:
                if not isinstance(_dict["." + ext], UserDefinedLanguage):
                    for key in (
                        "compile",
                        "execute",
                        "bundle",
                        "list_attributes",
                        "list_dependencies",
                    ):
                        if key in config:
                            raise RuntimeError(
                                "You cannot overwrite existing language: .{}".format(
                                    ext
                                )
                            )
            else:
                logger.warning(
                    "config.toml: languages.%s: Adding new languages using `config.toml` is supported but not recommended. Please consider making pull requests for your languages, see https://github.com/kmyk/online-judge-verify-helper/issues/116",
                    ext,
                )
                _dict["." + ext] = UserDefinedLanguage(extension=ext, config=config)
    return _dict


def get(path: pathlib.Path) -> Optional[Language]:
    return _get_dict().get(path.suffix)


def is_verification_file(path: pathlib.Path) -> bool:
    """`is_verification_file` is a thin wrapper for `Languge.is_verification_file`.  This function automatically get the language."""

    import onlinejudge_verify.languages.list

    basedir = pathlib.Path.cwd()
    language = onlinejudge_verify.languages.list.get(path)
    return language is not None and language.is_verification_file(path, basedir=basedir)