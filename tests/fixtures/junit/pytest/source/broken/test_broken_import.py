"""A module that fails to import, so pytest reports a collection error."""

import module_that_does_not_exist  # noqa: F401


def test_never_collected():
    pass
