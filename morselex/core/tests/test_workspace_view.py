from django.urls import reverse
from rest_framework.test import APIClient

import pytest

from fixtures import user  # noqa: F401


@pytest.mark.django_db
def test_workspace_view(user):
    client = APIClient()
    client.force_authenticate(user)
    args = [user.username]
    url = reverse("workspace-list", args=args)
    default = {'name': 'home'}
    # item list view

    # Start with home
    assert client.get(url).json() == [default]

    # Create a workspace
    ws_name = "my_ws"
    data = {'name': ws_name}
    assert client.post(url, data=data).json() == data

    # One Workspace
    assert client.get(url).json() == [default, data]

    # item detail view
    args = [user.username, ws_name]
    detail_url = reverse("workspace-detail", args=args)

    # read it
    assert client.get(detail_url).json() == data

    # re name it
    new_data = {'name': 'some_other_name'}
    assert client.put(detail_url, data=new_data).status_code == 200

    # read it again
    new_args = [user.username, new_data['name']]
    new_detail_url = reverse("workspace-detail", args=new_args)
    assert client.get(new_detail_url).json() == new_data

    # remove it
    assert client.delete(new_detail_url).status_code == 204

    # End with no workspaces
    assert client.get(url).json() == [default]
