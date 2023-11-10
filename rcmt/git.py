# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os.path
import shutil
from typing import Any, Mapping, Tuple, Union

import git
import structlog
from git.exc import GitCommandError

from rcmt import source

log: structlog.stdlib.BoundLogger = structlog.get_logger(package="git")


class BranchModifiedError(RuntimeError):
    def __init__(self, checksums: list[str]):
        self.checksums = checksums


class Git:
    def __init__(
        self,
        branch_name: str,
        clone_opts: Mapping[str, Any],
        data_dir: str,
        user_name: str,
        user_email: str,
    ):
        self.branch_name = branch_name
        self.clone_opts = clone_opts
        self.data_dir = data_dir
        self.user_email = user_email
        self.user_name = user_name

    def checkout_dir(self, repo: source.Repository) -> str:
        return os.path.join(self.data_dir, repo.source, repo.project, repo.name)

    def commit_changes(self, repo_dir: str, msg: str):
        git_repo = git.Repo(path=repo_dir)
        git_repo.git.add(all=True)
        git_repo.index.commit(msg)

    def _detect_modified_branch(
        self,
        merge_base: str,
        repo: git.Repo,
    ) -> None:
        foreign_commits: list[str] = []
        for commit in repo.iter_commits():
            if commit.hexsha == merge_base:
                break

            if commit.author.email != self.user_email:
                foreign_commits.append(commit.hexsha)

        if len(foreign_commits) > 0:
            raise BranchModifiedError(foreign_commits)

    @staticmethod
    def has_changes_origin(branch: str, repo_dir: str) -> bool:
        git_repo = git.Repo(path=repo_dir)
        try:
            return len(git_repo.index.diff(f"origin/{branch}")) > 0
        except git.BadName:
            # git.BadName thrown if "origin/<branch>" does not exist.
            # That means that this is the first time the Task is executed for this
            # repository. Always push in this case, thus return True here.
            return True

    @staticmethod
    def has_changes_local(repo_dir: str) -> bool:
        git_repo = git.Repo(path=repo_dir)
        return len(git_repo.index.diff(None)) > 0 or len(git_repo.untracked_files) > 0

    def prepare(
        self, repo: source.Repository, force_rebase: bool, iteration: int = 0
    ) -> Tuple[str, bool]:
        """
        1. Clone repository
        2. Checkout base branch
        3. Update base branch
        4. Create task branch
        5. Reset task branch to base branch
        """
        checkout_dir = self.checkout_dir(repo)
        if os.path.exists(checkout_dir) is False:
            log.debug("Cloning repository", url=repo.clone_url)
            os.makedirs(checkout_dir)
            git_repo = git.Repo.clone_from(
                repo.clone_url, checkout_dir, **self.clone_opts
            )
        else:
            git_repo = git.Repo(path=checkout_dir)
            self.reset(git_repo)

        if self.validate_branch_name(git_repo) is False:
            raise RuntimeError(f"Branch name '{self.branch_name}' is not valid")

        git_repo.config_writer().set_value("user", "email", self.user_email).release()
        git_repo.config_writer().set_value("user", "name", self.user_name).release()
        log.debug("Checking out base branch", branch=repo.base_branch)
        try:
            git_repo.heads[repo.base_branch].checkout()
        except IndexError as e:
            # Protection against infinite loops
            if iteration != 0:
                log.error(
                    "Base branch does not exist on second iteration - stopping processing of repository and re-raising exception"
                )
                raise e

            log.debug(
                "Base branch does not exist - deleting local repository and triggering another clone",
                branch=repo.base_branch,
            )
            shutil.rmtree(checkout_dir)
            return self.prepare(force_rebase=force_rebase, iteration=1, repo=repo)

        hash_before_pull = str(git_repo.head.commit)
        log.debug(
            "Pulling changes into base branch",
            branch=repo.base_branch,
        )
        git_repo.remotes["origin"].pull()
        git_repo.git.remote("prune", "origin")
        hash_after_pull = str(git_repo.head.commit)
        has_base_branch_update = hash_before_pull != hash_after_pull
        if has_base_branch_update is True:
            log.debug(
                "Base branch contains new commits",
                base_branch=repo.base_branch,
            )

        exists_local = branch_exists_local(self.branch_name, git_repo)
        remote_branch = get_remote_branch(self.branch_name, git_repo)
        if exists_local is False:
            log.debug("Creating branch", branch=self.branch_name)
            if remote_branch is None:
                git_repo.create_head(self.branch_name)
            else:
                git_repo.create_head(self.branch_name, remote_branch)

        has_conflict = False
        if remote_branch is not None:
            try:
                # Try to merge. Errors if there is a merge conflict.
                git_repo.git.merge(self.branch_name, no_ff=True, no_commit=True)
            except GitCommandError as e:
                # Exit codes "1" or "2" indicate that a merge is not successful
                if e.status != 1 and e.status != 2:
                    raise e

                log.debug(
                    "Merge conflict with base branch",
                    base_branch=repo.base_branch,
                )
                has_conflict = True

            try:
                # Abort the merge to not leave the branch in a conflicted state
                git_repo.git.merge(abort=True)
            except GitCommandError as e:
                # "128" is the exit code of the git command if no abort was needed
                if e.status != 128:
                    raise e

        log.debug("Checking out work branch", branch=self.branch_name)
        git_repo.heads[self.branch_name].checkout()
        if remote_branch is not None:
            log.debug("Pulling changes into work branch", branch=self.branch_name)
            # `rebase=True` to end up with a clean history.
            # `strategy_option="theirs"` to always prefer changes from the remote.
            # Commits by someone else will be preserved with this strategy and there
            # will be no conflict.
            git_repo.remotes["origin"].pull(
                self.branch_name, rebase=True, strategy_option="theirs"
            )

        merge_base = git_repo.git.merge_base(repo.base_branch, self.branch_name)
        if force_rebase is False:
            self._detect_modified_branch(merge_base=merge_base, repo=git_repo)

        log.debug("Resetting to merge base", branch=self.branch_name)
        git_repo.git.reset(merge_base, hard=True)
        log.debug("Rebasing onto work branch", branch=self.branch_name)
        git_repo.git.rebase(repo.base_branch)

        return checkout_dir, has_conflict

    def push(self, repo_dir):
        git_repo = git.Repo(path=repo_dir)
        git_repo.git.push("origin", self.branch_name, force=True, set_upstream=True)

    @staticmethod
    def reset(repo: git.Repo) -> None:
        repo.git.reset("HEAD", hard=True)

    def validate_branch_name(self, repo: git.Repo) -> bool:
        try:
            repo.git.check_ref_format(f"refs/heads/{self.branch_name}")
            return True
        except GitCommandError:
            return False


def branch_exists_local(name: str, repo: git.Repo) -> bool:
    for b in repo.heads:
        if b.name == name:
            return True

    return False


def get_remote_branch(name: str, repo: git.Repo) -> Union[git.RemoteReference, None]:
    remote = repo.remote()
    for r in remote.refs:
        if r.name == f"{remote.name}/{name}":
            return r

    return None
