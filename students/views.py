from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.views.generic import View
from courses.models import Subject, Course, Module
from django.db.models import Count, Sum
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class CourseListView(View):
    def get(self, request, *args, **kwargs):
        all_courses = Course.objects.count()
        subjects = Subject.objects.annotate(
            total_courses=Count('subject_courses')
        )
        courses = Course.objects.annotate(total_modules=Count('modules'))
        subject = self.kwargs.get('subject')
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        return render(self.request, 'student/course_list.html', {'subjects': subjects, 'courses': courses, 'subject': subject, 'all_courses': all_courses})


class CourseDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.setup_data()
        if self.request.user not in self.course.students.all():
            return render(self.request, 'student/course_enroll.html', {'course': self.course})
        return redirect('students:student_course_detail', self.course.id)

    def post(self, request, *args, **kwargs):
        self.setup_data()
        self.course.students.add(self.request.user)
        return redirect('students:student_course_detail', self.course.id)

    def setup_data(self, data=None):
        course = self.kwargs['course']
        self.course = get_object_or_404(Course, slug=course)


class StudentCourseListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        courses = Course.objects.filter(students__in=[self.request.user]).annotate(
            total_modules=Count('modules'))
        return render(self.request, 'student/student_course_list.html', {'courses': courses})


class StudentCourseDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        if self.kwargs.get('module_id'):
            module = get_object_or_404(Module, id=self.kwargs['module_id'])
        else:
            module = self.course.modules.first()
        return render(self.request, 'student/student_course_detail.html', {'course': self.course, 'module': module})

    def test_func(self):
        self.course = get_object_or_404(
            Course, id=self.kwargs.get('course_id')
        )
        return self.request.user in self.course.students.all()
