from django.http import Http404
from django.core.exceptions import PermissionDenied

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.serializers import WorkspaceSerializer, MorselSerializer
from core import models


class BaseWorkspaceAPIView(APIView):
    def ensure_permissions(self, request, user_name):
        # Must be owner or superuser
        user = request.user
        if user.username != user_name:
            if not user.is_superuser:
                raise PermissionDenied("You cant read or write this workspace")


class WorkspaceList(BaseWorkspaceAPIView):
    """
    List all Workspaces, or create a new Workspace.
    """

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


class WorkspaceDetail(BaseWorkspaceAPIView):
    """
    List all snippets, or create a new snippet.
    """

    def get_object(self, user_name, workspace_name):
        try:
            return models.User.objects.get(username=user_name).workspace_set.get(name=workspace_name)
        except models.Workspace.DoesNotExist:
            raise Http404

    def get(self, request, user_name, workspace_name, format=None):
        self.ensure_permissions(request, user_name)

        workspace = self.get_object(user_name, workspace_name)
        serializer = WorkspaceSerializer(workspace)
        return Response(serializer.data)

    def put(self, request, user_name, workspace_name, format=None):
        self.ensure_permissions(request, user_name)
        workspace = self.get_object(user_name, workspace_name)
        serializer = WorkspaceSerializer(workspace, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_name, workspace_name, format=None):
        self.ensure_permissions(request, user_name)
        workspace = self.get_object(user_name, workspace_name)
        workspace.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BaseMorselAPIView(APIView):
    def ensure_permissions(self, request, user_name, workspace_name, write=False):
        # Must be owner or superuser
        # TODO: support workspace permissions
        user = request.user
        if user.username != user_name:
            if not user.is_superuser:
                raise PermissionDenied("You cant read or write this workspace")


class MorselList(BaseMorselAPIView):
    """
    List all Workspaces, or create a new Workspace.
    """

    def get(self, request, user_name, workspace_name, format=None):
        self.ensure_permissions(request, user_name, workspace_name)

        morsels = models.User.objects.get(username=user_name).workspace_set.get(name=workspace_name).morsel_set.all()
        serializer = MorselSerializer(morsels, many=True)
        return Response(serializer.data)

    def post(self, request, user_name, workspace_name, format=None):
        self.ensure_permissions(request, user_name, workspace_name, write=True)

        workspace = models.User.objects.get(username=user_name).workspace_set.get(name=workspace_name)
        serializer = MorselSerializer(data=request.data, author=request.user, workspace=workspace)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MorselDetail(BaseMorselAPIView):
    """
    List all snippets, or create a new snippet.
    """

    def get_object(self, user_name, workspace_name, id):
        try:
            return models.Morsel.objects.get(
                id=id, workspace__name=workspace_name, workspace__owner__username=user_name
            )
        except models.Morsel.DoesNotExist:
            raise Http404

    def get(self, request, user_name, workspace_name, morsel_id, format=None):
        self.ensure_permissions(request, user_name, workspace_name)

        morsel = self.get_object(user_name, workspace_name, morsel_id)
        serializer = MorselSerializer(morsel)
        return Response(serializer.data)

    def put(self, request, user_name, workspace_name, morsel_id, format=None):
        self.ensure_permissions(request, user_name, workspace_name)
        morsel = self.get_object(user_name, workspace_name, morsel_id)
        serializer = MorselSerializer(morsel, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_name, workspace_name, morsel_id, format=None):
        self.ensure_permissions(request, user_name, workspace_name)
        morsel = self.get_object(user_name, workspace_name, morsel_id)
        morsel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
