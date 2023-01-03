import datetime
from typing import Generator

import rcmt.encoding
import rcmt.source
from rcmt.source import Repository


class MyCustomRepository(rcmt.source.Repository):
    """
    Implement all methods of class rcmt.source.Repository here.
    """

    pass


class MyCustomSource(rcmt.source.Base):
    def list_repositories(
        self, since: datetime.datetime
    ) -> list[rcmt.source.Repository]:
        return [MyCustomRepository()]

    def list_repositories_with_open_pull_requests(
        self,
    ) -> Generator[Repository, None, None]:
        yield from []


class MyCustomEncoding(rcmt.encoding.Encoding):
    """
    Implement all methods of class rcmt.encoding.Encoding here.
    """


# Basic setup
opts = rcmt.options_from_config("<path to rcmt config file>")
opts.run_paths = ["<paths to run files>"]

# Add the custom Source
opts.sources["custom"] = MyCustomSource()

# Add the custom Encoding
opts.encoding_registry.register(enc=MyCustomEncoding(), extensions=[".myc"])

# Execute rcmt
rcmt.execute(opts)
