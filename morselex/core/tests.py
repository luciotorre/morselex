import pytest

from . import models


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


@pytest.mark.django_db
def test_create_morsel(user, workspace):
    m = models.Morsel(author=user, workspace=workspace)
    m.save()


@pytest.mark.django_db
def test_attributes(user, workspace):
    m = models.Morsel(author=user, workspace=workspace)
    m.save()

    title = "From the earth to the moon."
    with pytest.raises(KeyError):
        m['title']

    assert m.keys() == []
    assert m.attributes() == {}

    m['title'] = title
    assert m['title'] == title

    assert m.keys() == ['title']
    assert m.attributes() == {'title': title}

    values = dict(
        author='Ursula',
        title='The dispossessed'
    )
    m.update(values)

    assert m.attributes() == values


@pytest.mark.django_db
def test_tags(user, workspace):
    m = models.Morsel(author=user, workspace=workspace)
    m.save()

    assert m.all_tags() == []

    m.add_tag("foo")
    assert m.all_tags() == ['foo']

    m.add_tag("bar")
    assert sorted(m.all_tags()) == ['bar', 'foo']

    m.remove_tag("foo")
    assert m.all_tags() == ['bar']

    m.add_tag("baz")
    m.clear_tags()
    assert m.all_tags() == []
