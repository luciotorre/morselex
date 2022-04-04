
import re
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.core.exceptions import PermissionDenied

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from core.serializers import WorkspaceSerializer, MorselSerializer
from core import models

class WorkspaceList(APIView):
    """
    List all Workspaces, or create a new Workspace.
    """

    def ensure_permissions(self, request, user_name):
        user = request.user
        if user.username != user_name:
            if not user.is_superuser:
                raise PermissionDenied()

    def get(self, request, user_name, format=None):
        self.ensure_permissions(request, user_name)

        workspaces = request.user.workspace_set.all()
        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data)

    def post(self, request, user_name, format=None):
        self.ensure_permissions(request, user_name)

        owner = models.User.objects.get(username=user_name)
        serializer = WorkspaceSerializer(data=request.data, owner=owner)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkspaceDetail(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get_object(self, pk):
        try:
            return Snippet.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    def ensure_permissions(self, request, user_name):
        user = request.user
        if user.username != user_name:
            if not user.is_superuser:
                raise PermissionDenied()

    def get(self, request, user_name, format=None):
        self.ensure_permissions(request, user_name)

        workspaces = request.user.workspace_set.all()
        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data)

    def post(self, request, user_name, format=None):
        self.ensure_permissions(request, user_name)

        owner = models.User.objects.get(username=user_name)
        serializer = WorkspaceSerializer(data=request.data, owner=owner)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)