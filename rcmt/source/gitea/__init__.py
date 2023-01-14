import datetime

from ..source import Base, Repository


class Gitea(Base):
    def list_repositories(self, since: datetime.datetime) -> list[Repository]:
        pass
