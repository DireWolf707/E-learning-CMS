from django.forms.models import modelform_factory
from django.shortcuts import render
from django.views.generic import View, ListView
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse, Http404
from .forms import CourseForm, ModuleFormSet
from .models import Content, Course, Module
from django.contrib.auth.mixins import LoginRequiredMixin
from django.apps import apps
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin


class ManageCourseListView(LoginRequiredMixin, ListView):
    template_name = 'manage/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


class ManageCourseCreateUpdateView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        course = self.get_object()
        form = CourseForm(instance=course)
        return render(request, 'manage/course_form.html', {'form': form, 'course': course})

    def post(self, request, *args, **kwargs):
        course = self.get_object()
        form = CourseForm(self.request.POST, instance=course)
        if form.is_valid():
            if not course:
                form.instance.instructor = self.request.user
                course = form.save()
                course.students.add(self.request.user)
            else:
                form.save()
            return redirect('manage_courses:manage_course_list')
        return render(request, 'manage/course_form.html', {'form': form, 'course': course})

    def get_object(self):
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(
                Course, id=pk, instructor=self.request.user
            )
        return None


class ManageCourseDeleteView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(
            Course, id=self.kwargs['pk'], instructor=self.request.user
        )
        course.delete()
        return JsonResponse(data={'status': 'deleted'})


class ManageModuleView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        course = self.get_object()
        formset = ModuleFormSet(instance=course)
        return render(request, 'manage/module_formset.html', {'course': course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        course = self.get_object()
        formset = ModuleFormSet(instance=course, data=self.request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_courses:manage_course_list')
        return render(request, 'manage/module_formset.html', {'formset': formset, 'course': course})

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(
            Course, id=pk, instructor=self.request.user
        )


class ManageContentCreateUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.set_objects()
        form = self.get_form(self.item_model, instance=self.item)
        return render(self.request, 'manage/content_form.html', {'form': form, 'item': self.item, 'module_id': self.module.id, 'model_name': self.kwargs['model_name']})

    def post(self, request, *args, **kwargs):
        self.set_objects()
        form = self.get_form(self.item_model, instance=self.item,
                             data=self.request.POST, files=self.request.FILES
                             )
        if form.is_valid():
            form.instance.owner = self.request.user
            item = form.save()
            if not self.item_id:
                Content.objects.create(module=self.module, item=item)
            return redirect('manage_courses:manage_content_list', self.module.id)
        return render(self.request, 'manage/content_form.html', {'form': form, 'item': self.item})

    def get_model(self, model_name):
        if model_name in ('text', 'video', 'image', 'file',):
            return apps.get_model(app_label='courses', model_name=model_name)
        raise Http404()

    def get_form(self, model, *args, **kwargs):
        form = modelform_factory(model, exclude=('owner', 'order',))
        return form(*args, **kwargs)

    def set_objects(self):
        self.module = get_object_or_404(Module, id=self.kwargs['module_id'])
        self.item_model = self.get_model(self.kwargs['model_name'])
        self.item_id = self.kwargs.get('item_id')
        self.item = None
        if self.item_id:
            self.item = get_object_or_404(
                self.item_model, id=self.item_id, owner=self.request.user
            )


class ManageContentDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        content = get_object_or_404(
            Content, id=self.kwargs['content_id'], module__course__instructor=self.request.user
        )
        module_id = content.module_id
        content.item.delete()
        content.delete()
        return redirect('manage_courses:manage_content_list', module_id)


class ManageContentListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        id = self.kwargs['module_id']
        module = None
        if id:
            module = get_object_or_404(
                Module, id=id, course__instructor=self.request.user
            )
        return render(self.request, 'manage/content_list.html', {'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request, *args, **kwargs):
        for id, order in self.request_json.items():
            Module.objects.filter(
                id=id, course__instructor=self.request.user
            ).update(order=order)
        return self.render_json_response({"status": "ok!"})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request, *args, **kwargs):
        for id, order in self.request_json.items():
            Content.objects.filter(
                id=id, module__course__instructor=self.request.user
            ).update(order=order)
        return self.render_json_response({"status": "ok!"})
