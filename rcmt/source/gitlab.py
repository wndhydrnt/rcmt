import gitlab

from rcmt.source import Repository, SourceLister


class GitlabRepository(Repository):
    def __init__(self, project: dict, url: str):
        self._project = project
        self.url = url

    @property
    def base_branch(self) -> str:
        return self._project["default_branch"]

    @property
    def clone_url(self) -> str:
        return self._project["http_url_to_repo"]

    @property
    def name(self) -> str:
        return self._project["path"]

    @property
    def project(self) -> str:
        return self._project["namespace"]["path"]

    @property
    def source(self) -> str:
        return self.url


class Gitlab(SourceLister):
    def __init__(self, url: str, private_token: str):
        self.client = gitlab.Gitlab(url, private_token=private_token)
        self.url = url

    def list_repositories(self) -> list[Repository]:
        projects = self.client.projects.list(
            all=True, archived=False, min_access_level=30
        )
        repositories: list[GitlabRepository] = []
        for p in projects:
            repositories.append(GitlabRepository(project=p, url=self.url))

        return repositories
