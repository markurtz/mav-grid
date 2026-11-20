# Copyright 2026 markurtz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test that the custom plate example runs."""

from __future__ import annotations

import pytest

from examples.custom_plate.main import main


@pytest.mark.smoke
def test_example_follows_the_constant() -> None:
    """A wider opening gives a narrower plate top."""
    tops = main(opening=9.0)
    assert tops["spec"] == (56.0, 56.0)
    assert tops["trial"] == (55.0, 55.0)
