import os.path

import git
import structlog

from rcmt import source

log = structlog.get_logger(package="git")


class Git:
    def __init__(
        self, branch_name: str, data_dir: str, user_name: str, user_email: str
    ):
        self.branch_name = branch_name
        self.data_dir = data_dir

        if user_email == "":
            self.author = user_name
        else:
            self.author = f"{user_name} <{user_email}>"

    def checkout_dir(self, repo: source.Repository) -> str:
        return os.path.join(self.data_dir, repo.source, repo.project, repo.name)

    def commit_changes(self, repo_dir: str, msg: str):
        git_repo = git.Repo(path=repo_dir)
        git_repo.git.add(all=True)
        # Bug in GitPython where the type hint of `author`says the parameter is a string
        # but the underlying code expects an Actor.
        git_repo.index.commit(
            msg, author=git.objects.commit.Actor._from_string(self.author)
        )

    @staticmethod
    def has_changes(repo_dir: str) -> bool:
        git_repo = git.Repo(path=repo_dir)
        return len(git_repo.index.diff(None)) > 0 or len(git_repo.untracked_files) > 0

    def needs_push(self, repo_dir: str) -> bool:
        git_repo = git.Repo(path=repo_dir)
        try:
            return len(git_repo.index.diff(f"origin/{self.branch_name}")) > 0
        except git.BadName:
            return True

    def prepare(self, repo: source.Repository) -> str:
        checkout_dir = self.checkout_dir(repo)
        if os.path.exists(checkout_dir) is False:
            log.debug("Cloning repository", url=repo.clone_url, repo=str(repo))
            os.makedirs(checkout_dir)
            git_repo = git.Repo.clone_from(repo.clone_url, checkout_dir)
        else:
            git_repo = git.Repo(path=checkout_dir)

        if branch_exists(self.branch_name, git_repo) is False:
            log.debug("Creating branch", branch=self.branch_name, repo=str(repo))
            git_repo.create_head(self.branch_name)

        log.debug("Checking out base branch", branch=repo.base_branch, repo=str(repo))
        git_repo.heads[repo.base_branch].checkout()
        log.debug(
            "Pulling changes into base branch", branch=repo.base_branch, repo=str(repo)
        )
        git_repo.remotes["origin"].pull()
        log.debug("Checking out work branch", branch=self.branch_name, repo=str(repo))
        git_repo.heads[self.branch_name].checkout()
        merge_base = git_repo.git.merge_base(repo.base_branch, self.branch_name)
        log.debug("Resetting to merge base", branch=self.branch_name, repo=str(repo))
        git_repo.git.reset(merge_base, hard=True)
        log.debug("Rebasing onto work branch", branch=self.branch_name, repo=str(repo))
        git_repo.git.rebase(repo.base_branch)
        return checkout_dir

    def push(self, repo_dir):
        git_repo = git.Repo(path=repo_dir)
        git_repo.git.push("origin", self.branch_name, force=True, set_upstream=True)


def branch_exists(name: str, repo: git.Repo) -> bool:
    for b in repo.heads:
        if b.name == name:
            return True

    return False
