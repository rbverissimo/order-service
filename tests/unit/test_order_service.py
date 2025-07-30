import pytest
from unittest.mock import MagicMock, AsyncMock
from app.repositories.order_repository import OrderRepository

@pytest.fixture
def mocker_order_repo(mocker):
    mock = mocker.MagicMock(spec=OrderRepository)
    mock.create = AsyncMock()
    return mock