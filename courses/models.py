from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_ordered_field import OrderedField

User = get_user_model()


class Subject(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return self.title


class Course(models.Model):
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses'
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='subject_courses'
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self) -> str:
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='modules'
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = OrderedField()

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return self.title


class Content(models.Model):
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name='modules'
    )
    order = OrderedField()

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, limit_choices_to={
            'model__in': ('text', 'video', 'image', 'file')}
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['order']


class BaseItem(models.Model):
    owner = models.ForeignKey(
        User, related_name='%(class)s', on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def get_image_loc(instance, filename):
    return f'images/{instance.owner.username}/{filename}'


def get_file_loc(instance, filename):
    return f'files/{instance.owner.username}/{filename}'


class Text(BaseItem):
    text = models.TextField()


class File(BaseItem):
    file = models.FileField(upload_to=get_file_loc)


class Image(BaseItem):
    image = models.ImageField(upload_to=get_image_loc)


class Video(BaseItem):
    url = models.URLField()
