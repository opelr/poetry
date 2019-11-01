from typing import Collection
from typing import Iterator
from typing import Mapping
from typing import Sequence

from poetry.packages import Package
from poetry.utils.helpers import canonicalize_name


def get_extra_package_names(
    packages,  # type: Sequence[Package]
    extras,  # type: Mapping[str, Collection[str]]
    extra_names,  # type: Sequence[str]
):  # type: (...) -> Iterator[str]
    """
    Returns all package names required by the given extras.

    :param packages: A collection of packages, such as from Repository.packages
    :param extras: A mapping of `extras` names to lists of package names, as defined
        in the `extras` section of `poetry.lock`.
    :param extra_names: A list of strings specifying names of extra groups to resolve.
    """
    if not extra_names:
        return []

    # lookup for packages by name, faster than looping over packages repeatedly
    packages_by_name = {package.name: package for package in packages}

    # get and flatten names of packages we've opted into as extras
    extra_package_names = [
        canonicalize_name(extra_package_name)
        for extra_name in extra_names
        for extra_package_name in extras.get(extra_name, ())
    ]

    def _extra_packages(package_names):
        """Recursively find dependencies for packages names"""
        # for each extra pacakge name
        for package_name in package_names:
            # Find the actual Package object. A missing key indicates an implicit
            # dependency (like setuptools), which should be ignored
            package = packages_by_name.get(canonicalize_name(package_name))
            if package:
                yield package.name
                # Recurse for dependencies
                for dependency_package_name in _extra_packages(
                    dependency.name for dependency in package.requires
                ):
                    yield dependency_package_name

    return _extra_packages(extra_package_names)