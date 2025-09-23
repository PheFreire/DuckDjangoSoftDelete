import pytest
from freezegun import freeze_time as _freeze_time_ctx

@pytest.fixture
def freeze_time():
    with _freeze_time_ctx("2025-01-01 12:00:00+00:00"):
        yield
