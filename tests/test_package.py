import unittest

import rcmt.rcmt
from rcmt import config
from rcmt.package import PackageInvalidError, PackageReader


class PackageReaderTest(unittest.TestCase):
    def test_read_packages(self):
        cfg = config.Config()
        opts = rcmt.rcmt.config_to_options(cfg)

        reader = PackageReader(opts.action_registry, opts.encoding_registry)
        pkgs = reader.read_packages(
            ["tests/fixtures/PackageReaderTest/test_read_packages/"]
        )

        self.assertEqual(1, len(pkgs))
        self.assertEqual("test-package", pkgs[0].name)
        self.assertEqual(1, len(pkgs[0].actions))

    def test_read_packages_no_manifest(self):
        cfg = config.Config()
        opts = rcmt.rcmt.config_to_options(cfg)

        reader = PackageReader(opts.action_registry, opts.encoding_registry)
        with self.assertRaises(PackageInvalidError):
            reader.read_packages(
                ["tests/fixtures/PackageReaderTest/test_read_packages_no_manifest/"]
            )
