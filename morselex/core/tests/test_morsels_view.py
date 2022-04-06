
from django.urls import reverse
from rest_framework.test import APIClient

import pytest

from core import models
from fixtures import user, workspace  # noqa: F401
from core.serializers import MorselSerializer


def clean_morsel_data(data):
    if isinstance(data, list):
        return [clean_morsel_data(item) for item in data]
    result = data.copy()
    del result['author']
    del result['created']
    del result['modified']
    del result['id']
    return result


@pytest.mark.django_db
def test_model_serializer(user, workspace):
    m = models.Morsel(author=user, workspace=workspace, text="hello")
    m.save()
    serial = MorselSerializer(m)
    result = clean_morsel_data(serial.data)
    assert result == {'text': 'hello', 'tags': [], 'attributes': {}}

    serial = MorselSerializer(m, data={'text': 'hello', 'tags': ['foo'], 'attributes': {'hello': 'world'}})
    assert serial.is_valid()
    serial.save()

    m.refresh_from_db()

    assert list(m.all_tags()) == ['foo']
    assert m['hello'] == 'world'


@pytest.mark.django_db
def test_morsel_view(user):
    client = APIClient()
    client.force_authenticate(user)
    args = [user.username, 'home']
    url = reverse("morsel-list", args=args)

    # item list view

    # Start with empty
    assert client.get(url).json() == []

    # Create a morsel
    data = {'text': 'morsel_text', 'tags': ['a', 'b'], 'attributes': {'k': 'v'}}
    result = clean_morsel_data(client.post(url, data=data, format='json').json())
    assert result == data

    # One Morsel
    result = clean_morsel_data(client.get(url).json())
    assert result == [data]

    # item detail view
    args = [user.username, 'home', 1]
    detail_url = reverse("morsel-detail", args=args)

    # read it
    result = clean_morsel_data(client.get(detail_url).json())
    assert result == data

    # re name it
    new_data = {'text': 'some_other_text'}
    # Argh, DRF wont process missing values properly unless using json format
    # https://github.com/encode/django-rest-framework/pull/6009
    assert client.put(detail_url, data=new_data, format='json').status_code == 200

    # read it again
    new_full_data = data.copy()
    new_full_data.update(new_data)
    result = clean_morsel_data(client.get(detail_url).json())
    assert result == new_full_data

    # remove it
    assert client.delete(detail_url).status_code == 204

    # End with no morsels
    assert client.get(url).json() == []
