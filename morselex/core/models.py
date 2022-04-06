from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    def create_workspace(self, name):
        return Workspace(owner=self, name=name)


@receiver(post_save, sender=User)
def create_default_workspace(sender, instance, created=None, **kwargs):
    if created:
        instance.create_workspace('home').save()


class Member(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['workspace', 'user'], name='one_perm_per_workspace_and_user'),
        ]

    permission = models.CharField(
        max_length=2,
        choices=[
            ('ro', 'read-only'),
            ('rw', 'read-write'),
        ]
    )
    workspace = models.ForeignKey('Workspace', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Workspace(TimeStampedModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    members = models.ManyToManyField(
        User,
        through=Member,
        through_fields=('workspace', 'user'),
        related_name='workspaces'
    )

    def __str__(self):
        return "<Workspace %s from %s>" % (self.name, self.owner)


class Morsel(TimeStampedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    text = models.TextField()

    tags = models.ManyToManyField(
        'Tag',
        through='Tagging',
        through_fields=('morsel', 'tag'),
        related_name='morsels',
    )

    edges_from = models.ManyToManyField(
        'Morsel',
        through='Edge',
        through_fields=('source', 'dest'),
        symmetrical=True,
    )

    # All these helper functions, maybe they should not exist.
    # Maybe I should just get used to the django model api.
    # Materializing query sets is nice but leads to OOMs.
    # Who would have more than 640 tags?
    def __getitem__(self, key):
        try:
            return self.attribute_set.get(label=key).value
        except Attribute.DoesNotExist:
            raise KeyError(f"Key '{key}' not found.")

    def __setitem__(self, key, value):
        attr, _ = self.attribute_set.update_or_create(label=key, defaults={'value': value})
        attr.save()

    def keys(self):
        return list(self.attribute_set.values_list('label', flat=True))

    def attributes(self):
        return dict((attr.label, attr.value) for attr in self.attribute_set.all())

    def update(self, values):
        for k, v in values.items():
            self[k] = v

    def add_tag(self, tagname):
        self.tags.create(workspace=self.workspace, name=tagname)

    def remove_tag(self, tagname):
        self.tags.filter(name=tagname).delete()

    def clear_tags(self):
        self.tags.all().delete()

    def all_tags(self):
        return list(self.tags.values_list('name', flat=True))


class Attribute(TimeStampedModel):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['morsel', 'label'], name='one_label_per_morsel'),
        ]

    morsel = models.ForeignKey(Morsel, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    value = models.TextField()


class Blobs(TimeStampedModel):
    morsel = models.ForeignKey(Morsel, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)

    blob = models.FileField()
    filename = models.CharField(max_length=100)
    content_type = models.CharField(max_length=100)


class Edge(TimeStampedModel):
    source = models.ForeignKey(Morsel, on_delete=models.CASCADE)
    dest = models.ForeignKey(
        Morsel, on_delete=models.CASCADE,
        related_name='incoming'
    )
    label = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        assert self.source.workspace == self.dest.workspace
        super().save(*args, **kwargs)


class Tag(TimeStampedModel):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class Tagging(TimeStampedModel):
    morsel = models.ForeignKey(Morsel, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        assert self.morsel.workspace == self.tag.workspace
        super().save(*args, **kwargs)
