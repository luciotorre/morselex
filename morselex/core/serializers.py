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


# TODO: Yes, this could be fast. Thinking required. Not sure it matters yet.

class MorselSerializer(serializers.Serializer):
    author = serializers.CharField(max_length=100, read_only=True)
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    id = serializers.IntegerField(read_only=True)
    text = serializers.CharField(required=False,)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
    )
    attributes = serializers.DictField(
        child=serializers.CharField(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop("author", None)
        self.workspace = kwargs.pop("workspace", None)
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'text': instance.text,
            'tags': instance.all_tags(),
            'attributes': instance.attributes(),
            'author': instance.author.username,
            'created': instance.created,
            'modified': instance.created,
        }

    def create(self, validated_data):
        validated_data['author'] = self.author
        validated_data['workspace'] = self.workspace
        tags = validated_data.pop('tags', None)
        attributes = validated_data.pop('attributes', None)
        m = models.Morsel.objects.create(**validated_data)
        if attributes is not None:
            m.update(attributes)

        if tags is not None:
            m.clear_tags()
            for tag in tags:
                m.add_tag(tag)
        m.save()
        return m

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        if 'attributes' in validated_data:
            instance.attribute_set.all().delete()
            instance.update(validated_data['attributes'])
        if 'tags' in validated_data:
            instance.clear_tags()
            for tag in validated_data['tags']:
                instance.add_tag(tag)
        instance.save()
        return instance
