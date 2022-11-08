import pathlib
from logging import getLogger

import competitive_verifier.github as github
from competitive_verifier.models import VerificationInput, VerifyCommandResult

from .page import check_pushed_to_github_head_branch, push_documents_to_gh_pages

logger = getLogger(__name__)

_src_dir = pathlib.Path(".competitive-verifier/markdown")


class DocumentBuilder:
    input: VerificationInput
    result: VerifyCommandResult

    def __init__(self, input: VerificationInput, result: VerifyCommandResult) -> None:
        self.input = input
        self.result = result

    def build(self) -> bool:
        logger.info("generate documents...")
        result = self.impl()
        logger.info("generated.")

        if github.env.is_in_github_actions():
            if check_pushed_to_github_head_branch():
                # Push gh-pages when in GitHub head branch
                if not push_documents_to_gh_pages(srcdir=_src_dir):
                    result = False
        else:
            logger.info(
                "\n".join(
                    [
                        "To see the generated document, do the following steps:",  # noqa: E501
                        "    1. Install Ruby with the files to build native modules. In Ubuntu, $ sudo apt install ruby-all-dev",  # noqa: E501
                        "    2. Install Ruby's Bundler (https://bundler.io/). In Ubuntu, $ sudo apt install ruby-bundler",  # noqa: E501
                        "    3. $ cd " + _src_dir.as_posix(),  # noqa: E501
                        "    4. $ bundle install --path .vendor/bundle",  # noqa: E501
                        "    5. $ bundle exec jekyll serve --incremental",  # noqa: E501
                        "    6. Open http://127.0.0.1:4000 on your web browser",  # noqa: E501
                    ]
                ),
            )

        return result

    def impl(self) -> bool:
        return True