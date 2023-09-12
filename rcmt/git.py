import os.path
from typing import Any, Mapping, Optional, Union

import git
import structlog
from git.exc import GitCommandError

log: structlog.stdlib.BoundLogger = structlog.get_logger(package="git")


class Git:
    def __init__(
        self,
        base_branch: str,
        checkout_dir: str,
        clone_opts: Mapping[str, Any],
        repository_name: str,
        user_name: str,
        user_email: str,
    ):
        self.base_branch = base_branch
        self.checkout_dir = checkout_dir
        self.clone_opts = clone_opts
        self.repository_name = repository_name
        self.user_email = user_email
        self.user_name = user_name

        self.git_repo: Optional[git.Repo] = None

    def commit_changes(self, msg: str):
        if self.git_repo is None:
            raise RuntimeError(
                "git repository not initialized - call initialize() first"
            )

        self.git_repo.git.add(all=True)
        self.git_repo.index.commit(msg)

    def has_changes_origin(self, branch: str) -> bool:
        if self.git_repo is None:
            raise RuntimeError(
                "git repository not initialized - call initialize() first"
            )

        try:
            return len(self.git_repo.index.diff(f"origin/{branch}")) > 0
        except git.BadName:
            # git.BadName thrown if "origin/<branch>" does not exist.
            # That means that this is the first time the Task is executed for this
            # repository. Always push in this case, thus return True here.
            return True

    def has_changes_local(self) -> bool:
        if self.git_repo is None:
            raise RuntimeError(
                "git repository not initialized - call initialize() first"
            )

        return (
            len(self.git_repo.index.diff(None)) > 0
            or len(self.git_repo.untracked_files) > 0
        )

    def initialize(self, clone_url: str) -> None:
        """
        1. Clone repository
        2. Checkout base branch
        3. Prune deleted/merged remote branches
        4. Update base branch
        """
        # Do clone/prune/checkout/fetch of base branch only once per run.
        if self.git_repo is not None:
            return None

        if os.path.exists(self.checkout_dir) is False:
            log.debug("Cloning repository", url=clone_url, repo=self.repository_name)
            os.makedirs(self.checkout_dir)
            git_repo = git.Repo.clone_from(
                clone_url, self.checkout_dir, **self.clone_opts
            )
        else:
            git_repo = git.Repo(path=self.checkout_dir)
            git_repo.git.reset("HEAD", hard=True)

        git_repo.config_writer().set_value("user", "email", self.user_email).release()
        git_repo.config_writer().set_value("user", "name", self.user_name).release()
        log.debug(
            "Checking out base branch",
            branch=self.base_branch,
            repo=self.repository_name,
        )
        git_repo.heads[self.base_branch].checkout()
        hash_before_pull = str(git_repo.head.commit)
        log.debug(
            "Pulling changes into base branch",
            branch=self.base_branch,
            repo=self.repository_name,
        )
        git_repo.remotes["origin"].pull()
        git_repo.git.remote("prune", "origin")
        hash_after_pull = str(git_repo.head.commit)
        has_base_branch_update = hash_before_pull != hash_after_pull
        if has_base_branch_update is True:
            log.debug(
                "Base branch contains new commits",
                base_branch=self.base_branch,
                repo=self.repository_name,
            )

        self.git_repo = git_repo

    def prepare_branch(self, branch_name: str) -> bool:
        """
        1. Reset any previous changes
        2. Create branch, if it does not exist
        3. Detect if a merge conflict exists
        4. Rebase changes of default branch onto working branch
        """
        if self.git_repo is None:
            raise RuntimeError(
                "git repository not initialized - call initialize() first"
            )

        if (
            self.validate_branch_name(branch_name=branch_name, git_repo=self.git_repo)
            is False
        ):
            raise RuntimeError(f"Branch name '{branch_name}' is not valid")

        self.git_repo.git.reset("HEAD", hard=True)
        self.git_repo.heads[self.base_branch].checkout()
        exists_local = branch_exists_local(branch_name, self.git_repo)
        remote_branch = get_remote_branch(branch_name, self.git_repo)
        if exists_local is False:
            log.debug("Creating branch", branch=branch_name, repo=self.repository_name)
            if remote_branch is None:
                self.git_repo.create_head(branch_name)
            else:
                self.git_repo.create_head(branch_name, remote_branch)

        has_conflict = False
        if remote_branch is not None:
            try:
                # Try to merge. Errors if there is a merge conflict.
                self.git_repo.git.merge(branch_name, no_ff=True, no_commit=True)
            except GitCommandError as e:
                # Exit codes "1" or "2" indicate that a merge is not successful
                if e.status != 1 and e.status != 2:
                    raise e

                log.debug(
                    "Merge conflict with base branch",
                    base_branch=self.base_branch,
                    repo=self.repository_name,
                )
                has_conflict = True

            try:
                # Abort the merge to not leave the branch in a conflicted state
                self.git_repo.git.merge(abort=True)
            except GitCommandError as e:
                # "128" is the exit code of the git command if no abort was needed
                if e.status != 128:
                    raise e

        log.debug(
            "Checking out work branch", branch=branch_name, repo=self.repository_name
        )
        self.git_repo.heads[branch_name].checkout()
        merge_base = self.git_repo.git.merge_base(self.base_branch, branch_name)
        log.debug(
            "Resetting to merge base", branch=branch_name, repo=self.repository_name
        )
        self.git_repo.git.reset(merge_base, hard=True)
        log.debug(
            "Rebasing onto work branch", branch=branch_name, repo=self.repository_name
        )
        self.git_repo.git.rebase(self.base_branch)
        return has_conflict

    def push(self, branch_name: str):
        if self.git_repo is None:
            raise RuntimeError(
                "git repository not initialized - call initialize() first"
            )

        self.git_repo.git.push("origin", branch_name, force=True, set_upstream=True)

    @staticmethod
    def validate_branch_name(branch_name: str, git_repo: git.Repo) -> bool:
        try:
            git_repo.git.check_ref_format(f"refs/heads/{branch_name}")
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
