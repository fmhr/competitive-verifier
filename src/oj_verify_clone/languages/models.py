# Python Version: 3.x
import abc
import pathlib
from typing import Any, Sequence

import oj_verify_clone.languages.special_comments as special_comments


class LanguageEnvironment:
    @abc.abstractmethod
    def get_compile_command(
        self, path: pathlib.Path, *, basedir: pathlib.Path, tempdir: pathlib.Path
    ) -> str:
        """
        :throws Exception:
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_execute_command(
        self, path: pathlib.Path, *, basedir: pathlib.Path, tempdir: pathlib.Path
    ) -> str:
        raise NotImplementedError


class Language:
    def list_attributes(
        self, path: pathlib.Path, *, basedir: pathlib.Path
    ) -> dict[str, Any]:
        """
        :throws Exception:
        """

        attributes: dict[str, Any] = special_comments.list_special_comments(path)
        attributes.setdefault("links", [])
        attributes["links"].extend(special_comments.list_embedded_urls(path))
        return attributes

    @abc.abstractmethod
    def list_dependencies(
        self, path: pathlib.Path, *, basedir: pathlib.Path
    ) -> list[pathlib.Path]:
        """
        :throws Exception:
        """

        raise NotImplementedError

    @abc.abstractmethod
    def bundle(
        self, path: pathlib.Path, *, basedir: pathlib.Path, options: dict[str, Any]
    ) -> bytes:
        """
        :throws Exception:
        :throws NotImplementedError:
        """

        raise NotImplementedError

    def is_verification_file(
        self, path: pathlib.Path, *, basedir: pathlib.Path
    ) -> bool:
        return ".test." in path.name

    @abc.abstractmethod
    def list_environments(
        self, path: pathlib.Path, *, basedir: pathlib.Path
    ) -> Sequence[LanguageEnvironment]:
        raise NotImplementedError