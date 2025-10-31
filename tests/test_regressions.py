import os.path
import asyncio
import concurrent.futures

import pytest

from pyrpm.spec import Spec

TEST_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


def with_timeout(t):
    def wrapper(corofunc):
        async def run(*args, **kwargs):
            return await asyncio.wait_for(corofunc(*args, **kwargs), timeout=t)

        return run

    return wrapper


@pytest.mark.asyncio
@with_timeout(5)
async def test_endless_loop() -> None:
    """Make sure spec._parse() doesn't call replace_macros().

    Ensure we don't get stuck in an endless loop."""

    specfile = os.path.join(TEST_DATA, "xscreensaver.spec")
    loop = asyncio.get_running_loop()

    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, Spec.from_file, specfile)
