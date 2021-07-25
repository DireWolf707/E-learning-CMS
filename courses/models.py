from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django_ordered_field import OrderedCollectionField
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

User = get_user_model()


class Subject(models.Model):
    title = models.CharField(max_length=100, unique=True)
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
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(
        User, related_name='student_joined', blank=True
    )

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
    order = OrderedCollectionField(collection='course')

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return self.title


class Content(models.Model):
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name='contents'
    )
    order = OrderedCollectionField(collection='module')

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

    def render(self):
        return render_to_string(f'student/content/{self._meta.model_name}.html', {'item': self})


def get_image_loc(instance, filename):
    return f'images/{instance.owner.username}/{get_random_string(length=10)}{filename}'


def get_file_loc(instance, filename):
    return f'files/{instance.owner.username}/{get_random_string(length=10)}{filename}'


class Text(BaseItem):
    text = models.TextField()


class File(BaseItem):
    file = models.FileField(upload_to=get_file_loc)


class Image(BaseItem):
    image = models.ImageField(upload_to=get_image_loc)


class Video(BaseItem):
    url = models.URLField()


@receiver(post_delete, sender=File)
@receiver(post_delete, sender=Image)
def content_delete(sender, instance, using, *args, **kwargs):
    if hasattr(instance, 'image'):
        path = instance.image.path
    elif hasattr(instance, 'file'):
        path = instance.file.path
    if os.path.isfile(path):
        os.remove(path)


@receiver(pre_save, sender=Course)
def slugify_title(sender, instance, raw, using, update_fields, *args, **kwargs):
    instance.slug = slugify(instance.title)
