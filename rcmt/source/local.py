from rcmt.source import Repository


class Local(Repository):
    def __init__(self, source_name: str, project_name: str, repo_name: str):
        self.project_name = project_name
        self.repo_name = repo_name
        self.source_name = source_name

    @property
    def name(self) -> str:
        return self.repo_name

    @property
    def project(self) -> str:
        return self.project_name

    @property
    def source(self) -> str:
        return self.source_name
