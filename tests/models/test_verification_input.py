# flake8: noqa E501
import json
from pathlib import Path

from competitive_verifier.models import VerificationInput

test_input = VerificationInput.parse_obj(
    {
        "files": {
            "foo/bar1.py": {},
            "foo/bar2.py": {"dependencies": ["foo/bar1.py"]},
            "foo/baz.py": {},
            "foo/barbaz.py": {
                "dependencies": [
                    "foo/bar2.py",
                    "foo/baz.py",
                ],
            },
            "hoge/1.py": {},
            "hoge/hoge.py": {
                "dependencies": [
                    "hoge/fuga.py",
                    "hoge/1.py",
                ],
            },
            "hoge/piyo.py": {
                "dependencies": [
                    "hoge/fuga.py",
                    "hoge/hoge.py",
                ],
            },
            "hoge/fuga.py": {"dependencies": ["hoge/piyo.py"]},
            "hoge/piyopiyo.py": {"dependencies": ["hoge/piyo.py"]},
            "test/test.py": {
                "verification": [{"status": "success", "type": "const"}],
                "dependencies": ["hoge/piyopiyo.py"],
            },
        }
    }
)


def test_to_dict():
    assert test_input.dict() == test_input.impl.dict()


def test_to_json():
    assert test_input.json() == test_input.impl.json()
    assert VerificationInput.parse_raw(test_input.json()) == test_input

    obj = VerificationInput.parse_obj(
        {
            "files": {
                "foo/bar.py": {},
                "foo/baz.py": {
                    "path": "foo/baz.py",
                    "document_attributes": {"title": "foo-baz"},
                    "dependencies": ["foo/bar.py"],
                    "verification": [
                        {
                            "type": "const",
                            "status": "success",
                        }
                    ],
                },
            },
        }
    )
    assert json.loads(obj.json()) == {
        "files": {
            "foo/bar.py": {
                "dependencies": [],
                "document_attributes": {},
                "verification": [],
            },
            "foo/baz.py": {
                "document_attributes": {"title": "foo-baz"},
                "dependencies": ["foo/bar.py"],
                "verification": [
                    {
                        "type": "const",
                        "status": "success",
                    }
                ],
            },
        },
    }


def test_repr():
    obj = VerificationInput.parse_obj(
        {
            "files": {
                "foo/bar.py": {},
                "foo/baz.py": {
                    "path": "foo/baz.py",
                    "document_attributes": {
                        "title": "foo-baz",
                    },
                    "dependencies": ["foo/bar.py"],
                    "verification": [
                        {
                            "type": "const",
                            "status": "success",
                        }
                    ],
                },
            },
        }
    )
    print(repr(obj))
    assert repr(obj) == (
        "VerificationInput("
        + f"files={{{repr(Path('foo/bar.py'))}: VerificationFile(dependencies=[], verification=[], document_attributes={{}}),"
        + f" {repr(Path('foo/baz.py'))}: VerificationFile(dependencies=[{repr(Path('foo/bar.py'))}], verification=[ConstVerification(type='const', status=<ResultStatus.SUCCESS: 'success'>)], document_attributes={{'title': {repr('foo-baz')}}})"
        + f"}})"
    )


def test_transitive_depends_on():
    simple = {
        "foo/bar1.py": ["foo/bar1.py"],
        "foo/bar2.py": ["foo/bar1.py", "foo/bar2.py"],
        "foo/baz.py": ["foo/baz.py"],
        "foo/barbaz.py": ["foo/barbaz.py", "foo/baz.py", "foo/bar1.py", "foo/bar2.py"],
        "hoge/1.py": ["hoge/1.py"],
        "hoge/hoge.py": ["hoge/hoge.py", "hoge/piyo.py", "hoge/fuga.py", "hoge/1.py"],
        "hoge/piyo.py": ["hoge/hoge.py", "hoge/piyo.py", "hoge/fuga.py", "hoge/1.py"],
        "hoge/fuga.py": ["hoge/hoge.py", "hoge/piyo.py", "hoge/fuga.py", "hoge/1.py"],
        "hoge/piyopiyo.py": [
            "hoge/piyopiyo.py",
            "hoge/hoge.py",
            "hoge/piyo.py",
            "hoge/fuga.py",
            "hoge/1.py",
        ],
        "test/test.py": [
            "hoge/1.py",
            "hoge/fuga.py",
            "hoge/hoge.py",
            "hoge/piyo.py",
            "hoge/piyopiyo.py",
            "test/test.py",
        ],
    }
    expected = {Path(p): set(Path(s) for s in d) for p, d in simple.items()}

    assert test_input.transitive_depends_on == expected
    assert test_input.transitive_depends_on is test_input.transitive_depends_on
    assert test_input.transitive_depends_on == expected


def test_depends_on():
    simple = {
        "foo/bar1.py": [],
        "foo/bar2.py": [("foo/bar1.py")],
        "foo/baz.py": [],
        "foo/barbaz.py": ["foo/bar2.py", "foo/baz.py"],
        "hoge/1.py": [],
        "hoge/hoge.py": ["hoge/fuga.py", "hoge/1.py"],
        "hoge/piyo.py": ["hoge/fuga.py", "hoge/hoge.py"],
        "hoge/fuga.py": ["hoge/piyo.py"],
        "hoge/piyopiyo.py": ["hoge/piyo.py"],
        "test/test.py": ["hoge/piyopiyo.py"],
    }
    expected = {Path(p): set(Path(s) for s in d) for p, d in simple.items()}

    assert test_input.depends_on == expected
    assert test_input.depends_on is test_input.depends_on
    assert test_input.depends_on == expected


def test_required_by():
    simple = {
        "foo/bar1.py": ["foo/bar2.py"],
        "foo/bar2.py": ["foo/barbaz.py"],
        "foo/baz.py": ["foo/barbaz.py"],
        "foo/barbaz.py": [],
        "hoge/1.py": ["hoge/hoge.py"],
        "hoge/hoge.py": ["hoge/piyo.py"],
        "hoge/piyo.py": ["hoge/fuga.py", "hoge/piyopiyo.py"],
        "hoge/fuga.py": ["hoge/piyo.py", "hoge/hoge.py"],
        "hoge/piyopiyo.py": [],
        "test/test.py": [],
    }
    expected = {Path(p): set(Path(s) for s in d) for p, d in simple.items()}

    assert test_input.required_by == expected
    assert test_input.required_by is test_input.required_by
    assert test_input.required_by == expected


def test_verified_with():
    simple = {
        "foo/bar1.py": [],
        "foo/bar2.py": [],
        "foo/baz.py": [],
        "foo/barbaz.py": [],
        "hoge/1.py": [],
        "hoge/hoge.py": [],
        "hoge/piyo.py": [],
        "hoge/fuga.py": [],
        "hoge/piyopiyo.py": ["test/test.py"],
        "test/test.py": [],
    }
    expected = {Path(p): set(Path(s) for s in d) for p, d in simple.items()}
    assert test_input.verified_with == expected
    assert test_input.verified_with is test_input.verified_with
    assert test_input.verified_with == expected
