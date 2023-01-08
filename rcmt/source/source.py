import datetime
import urllib.parse
from typing import Any, Generator, Optional, TextIO, Union

import humanize


class PullRequest:
    def __init__(
        self,
        auto_merge: bool,
        merge_once: bool,
        run_name: str,
        title_prefix: str,
        title_body: str,
        title_suffix: str,
        custom_body: str = "",
        custom_title: str = "",
        auto_merge_after: Optional[datetime.timedelta] = None,
    ):
        self.auto_merge = auto_merge
        self.auto_merge_after = auto_merge_after
        self.custom_body = custom_body
        self.custom_title = custom_title
        self.merge_once = merge_once
        self.run_name = run_name
        self.title_prefix = title_prefix
        self.title_body = title_body
        self.title_suffix = title_suffix

    def __eq__(self, other: object) -> bool:
        """
        Aids with checking equality during unit tests.

        :param other: Other PullRequest
        :return: bool
        """
        if self.auto_merge != getattr(other, "auto_merge"):
            return False

        if self.auto_merge_after != getattr(other, "auto_merge_after"):
            return False

        if self.custom_body != getattr(other, "custom_body"):
            return False

        if self.custom_title != getattr(other, "custom_title"):
            return False

        if self.merge_once != getattr(other, "merge_once"):
            return False

        if self.run_name != getattr(other, "run_name"):
            return False

        if self.title_prefix != getattr(other, "title_prefix"):
            return False

        if self.title_body != getattr(other, "title_body"):
            return False

        if self.title_suffix != getattr(other, "title_suffix"):
            return False

        return True

    @property
    def body(self) -> str:
        if self.custom_body == "":
            body = f"Apply changes from Run {self.run_name}\n"
        else:
            body = self.custom_body
            body += "\n"

        body += "\n---\n\n"

        body += "**Automerge:** "
        # Add two spaces at the end of each line to make GitLab create a line break.
        if self.auto_merge is True:
            if self.auto_merge_after is None:
                body += "Enabled. rcmt merges this automatically on its next run and if all checks have passed.  \n"
            else:
                after = humanize.naturaldelta(self.auto_merge_after)
                body += f"Enabled. rcmt automatically merges this in {after} and if all checks have passed.  \n"
        else:
            body += "Disabled. Merge this manually.  \n"

        if self.merge_once is True:
            body += "**Ignore:** Close this PR and it will not be recreated again.  \n"
        else:
            body += "**Ignore:** This PR will be recreated if closed.  \n"

        body += """
---

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._"""

        return body

    @property
    def title(self) -> str:
        if self.custom_title != "":
            return self.custom_title

        return f"{self.title_prefix} {self.title_body} {self.title_suffix}".strip()


class Repository:
    """
    Repository provides all methods needed to interact with a single repository of a
    Source.
    """

    def __str__(self):
        return f"{self.source}/{self.project}/{self.name}"

    @property
    def base_branch(self) -> str:
        """
        :return: Name of the base branch of this repository.
        :rtype: str
        """
        raise NotImplementedError("class does not implement Repository.base_branch()")

    def can_merge_pull_request(self, identifier: Any) -> bool:
        """
        Checks if a pull request can be merged.

        Use this function to check if a Source, e.g. GitHub, indicates that merge
        conflicts exist.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        :return: Indicates if the pull request can be merged.
        :rtype: bool
        """
        raise NotImplementedError(
            "class does not implement Repository.can_merge_pull_request()"
        )

    @property
    def clone_url(self) -> str:
        """
        :return: Url to clone this repository.
        :rtype: str
        """
        raise NotImplementedError("class does not implement Repository.clone_url()")

    def close_pull_request(self, message: str, pr: Any) -> None:
        """
        Closes a pull request and adds a comment that explains why the pull request has
        been closed.

        :param message: Message to post as a comment.
        :param pr: The pull request.
        :rtype: None
        """
        raise NotImplementedError(
            "class does not implement Repository.close_pull_request()"
        )

    def create_pull_request(self, branch: str, pr: PullRequest) -> None:
        """
        Creates a pull request for the given branch.

        :param branch: Name of the branch.
        :param pr: The pull request.
        :rtype: None
        """
        raise NotImplementedError(
            "class does not implement Repository.create_pull_request()"
        )

    def delete_branch(self, identifier: Any) -> None:
        raise NotImplementedError(
            "class does not implement Repository.delete_pull_request()"
        )

    def find_pull_request(self, branch: str) -> Union[Any, None]:
        """
        Finds and returns the pull request opened by rcmt.

        :param branch: Name of the branch from which a pull request has been created.
        :return: Implementation of this method should return None if no pull request is open. Any other value will be
                 passed to merge_pull_request() so it can identify which PR to merge.
        :rtype: Any, None
        """
        raise NotImplementedError(
            "class does not implement Repository.has_open_pull_request()"
        )

    def get_file(self, path: str) -> TextIO:
        raise NotImplementedError("class does not implement Repository.has_file()")

    def has_file(self, path: str) -> bool:
        """
        Checks if a file exists in a repository.

        rcmt calls this function when matching repositories. This is more efficient than
        checking out the whole repository to check if a file exists.

        :param path: Path to a file or directory in the repository.
        :return: Indicates if the files exists.
        :rtype: bool
        """
        raise NotImplementedError("class does not implement Repository.has_file()")

    def has_successful_pr_build(self, identifier: Any) -> bool:
        """
        Checks if a pull request has passed all checks. rcmt will call merge_pull_request if this function returns
        True.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        :return: Indicates if the build is successful.
        :rtype: bool
        """
        raise NotImplementedError(
            "class does not implement Repository.has_successful_build()"
        )

    def is_pr_closed(self, identifier: Any) -> bool:
        """
        Checks if a pull request has been closed by the user.
        A pull request is closed if a user manually closes it without merging it.
        If a user has closed a pull request without merging it, rcmt will not create a
        new one.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        :return: Indicates that a pull request has been closed by the user.
        :rtype: bool
        """
        raise NotImplementedError("class does not implement Repository.is_pr_closed()")

    def is_pr_merged(self, identifier: Any) -> bool:
        """
        Checks if a pull request has been merged.
        rcmt uses this information to determine if it can create new pull requests.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        :return: Indicates that a pull request has been merged.
        :rtype: bool
        """
        raise NotImplementedError("class does not implement Repository.is_pr_merged()")

    def is_pr_open(self, identifier: Any) -> bool:
        """
        Checks if a pull request is open.
        rcmt will attempt to merge the pull request if this method returns true and
        there are no new changes from Actions.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        :return: Indicates that a pull request is open.
        :rtype: bool
        """
        raise NotImplementedError("class does not implement Repository.is_pr_open()")

    def merge_pull_request(self, identifier: Any) -> None:
        """
        Merges a pull request.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        """
        raise NotImplementedError(
            "class does not implement Repository.merge_pull_request()"
        )

    @property
    def name(self) -> str:
        """
        :return: Name of the repository.
        :rtype: str
        """
        raise NotImplementedError("class does not implement Repository.name()")

    def pr_created_at(self, pr: Any) -> datetime.datetime:
        """
        Returns the date and time at which the pull request was created.

        :param pr: The pull request identifier as returned by find_pull_request().
        :return: Date and time at which the pull request was created.
        :rtype: datetime.datetime
        """
        raise NotImplementedError("class does not implement Repository.pr_created_at()")

    @property
    def project(self) -> str:
        """
        :return: Name of the project the repository belongs to.
        :rtype: str
        """

        raise NotImplementedError("class does not implement Repository.project()")

    @property
    def source(self) -> str:
        """
        :return: Name of the source that hosts the repository.
        :rtype: str
        """
        raise NotImplementedError("class does not implement Repository.source()")

    def update_pull_request(self, pr: Any, pr_data: PullRequest) -> None:
        """
        Updates the title and body of a pull request.

        To reduce calls to the API, the implementation of this function should check if
        title or body have changed and only update the pull request if necessary.

        :param pr: Data to identify the pull request as returned by find_pull_request.
        :param pr_data: Data of the pull request that rcmt wants to create/update.
        :rtype: None
        """
        raise NotImplementedError(
            "class does not implement Repository.update_pull_request()"
        )


class Base:
    """
    Base defines the methods every Source needs to implement.

    """

    def list_repositories_with_open_pull_requests(
        self,
    ) -> Generator[Repository, None, None]:
        raise NotImplementedError(
            "class does not implement Base.list_open_pull_requests()"
        )

    def list_repositories(self, since: datetime.datetime) -> list[Repository]:
        """
        :param since: Date and time of the last run of rcmt to find only those repositories that have received and update since.

        :return: List of all known repositories.
        :rtype: list[rcmt.source.Repository]
        """
        raise NotImplementedError("class does not implement Base.list_repositories()")


def add_credentials_to_url(url: str, password: str, username: str = "") -> str:
    parsed = urllib.parse.urlparse(url)
    if username == "":
        credentials = password
    else:
        credentials = f"{username}:{password}"

    return parsed._replace(netloc=f"{credentials}@{parsed.netloc}").geturl()
