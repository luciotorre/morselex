import pytest

from core import models


@pytest.fixture
def user():
    user = models.User.objects.create(username='username')
    user.save()
    return user


@pytest.fixture
def workspace():
    user = models.User.objects.get(username='username')
    ws = user.create_workspace('default')
    ws.save()
    return ws


@pytest.fixture
def another_user():
    user = models.User.objects.create(username='another_username')
    user.save()
    return user
