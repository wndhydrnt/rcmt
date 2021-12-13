import rcmt
import rcmt.encoding
import rcmt.source


class MyCustomRepository(rcmt.source.Repository):
    """
    Implement all methods of class rcmt.source.Repository here.
    """

    pass


class MyCustomSource(rcmt.source.Base):
    def list_repositories(self) -> list[rcmt.source.Repository]:
        return [MyCustomRepository()]


class MyCustomEncoding(rcmt.encoding.Encoding):
    """
    Implement all methods of class rcmt.encoding.Encoding here.
    """


# Basic setup
opts = rcmt.options_from_config("<path to rcmt config file>")
opts.matcher_path = "<path to run file>"
opts.packages_paths = ["<path to packages directory>"]

# Add the custom Source
opts.sources.append(MyCustomSource())

# Add the custom Encoding
opts.encoding_registry.register(enc=MyCustomEncoding(), extensions=[".myc"])

# Execute rcmt
rcmt.execute(opts)
