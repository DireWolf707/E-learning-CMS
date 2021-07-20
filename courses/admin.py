from django.contrib import admin
from .models import Course, Subject, Module


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    #list_display = ('title')
    prepopulated_fields = {'slug': ('title',)}


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'created')
    list_filter = ('created', 'subject')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
