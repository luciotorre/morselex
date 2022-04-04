from rest_framework import serializers

from . import models


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workspace
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data['owner'] = self.owner
        return models.Workspace.objects.create(**validated_data)


class MorselSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Morsel
        fields = ['text']