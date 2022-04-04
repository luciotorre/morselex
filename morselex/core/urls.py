from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from core import views

urlpatterns = [
    path('<str:user_name>/w/', views.WorkspaceList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)