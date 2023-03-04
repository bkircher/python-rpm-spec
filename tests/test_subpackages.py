import os.path

from pyrpm.spec import Spec

TEST_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


class TestSubpackages:
    def test_subpackages_have_sources_and_patches(self) -> None:
        """Ensure sub-packages can have sources and patches, too.

        Test for AttributeError: 'Package' object has no attribute 'sources' on spec files where sub-packages are defined with
        their own sources. Example:

            %package java
            Summary: Timezone data for Java
            Source3: javazic.tar.gz

        """
        spec = Spec.from_file(os.path.join(TEST_DATA, "tzdata.spec"))

        assert len(spec.packages) == 2
        subpackage = spec.packages[1]
        assert subpackage.name == "tzdata-java"

        assert len(subpackage.sources) == 2
        assert len(subpackage.sources_dict) == 2
        for source in ("Source3", "Source4"):
            assert source in subpackage.sources_dict

        assert len(subpackage.patches) == 5
        assert len(subpackage.patches_dict) == 5
        for patch in (
            "Patch100",
            "Patch101",
            "Patch102",
            "Patch103",
            "Patch104",
        ):
            assert patch in subpackage.patches_dict

        # However, the spec files still contains _all_ sources and all patches, including the ones from the sub-packages.
        assert len(spec.sources) == 4
        assert len(spec.sources_dict) == 4
        assert len(spec.patches) == 7
        assert len(spec.patches_dict) == 7
