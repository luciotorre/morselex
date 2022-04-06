from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from core import views

urlpatterns = [
    # TODO: user names and workspace name as part of urls without any special care. something will go wrong.
    # A product person would say that workspace name should not be a machine identifier but a
    # humanized string like 'My Home <emoji>'.
    path('<str:user_name>/w/', views.WorkspaceList.as_view(), name="workspace-list"),
    path('<str:user_name>/w/<str:workspace_name>', views.WorkspaceDetail.as_view(), name="workspace-detail"),
    path('<str:user_name>/w/<str:workspace_name>/m', views.MorselList.as_view(), name="morsel-list"),
    path(
        '<str:user_name>/w/<str:workspace_name>/m/<int:morsel_id>', views.MorselDetail.as_view(), name="morsel-detail"
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
