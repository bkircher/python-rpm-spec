import asyncio
import concurrent.futures
import os.path
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

import pytest

from pyrpm.spec import Spec

TEST_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

P = ParamSpec("P")
T = TypeVar("T")


def with_timeout(t: float) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    def wrapper(corofunc: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        async def run(*args: P.args, **kwargs: P.kwargs) -> T:
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
        _ = await loop.run_in_executor(pool, Spec.from_file, specfile)
