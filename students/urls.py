from django.urls import path
from .views import CourseListView, CourseDetailView, StudentCourseListView, StudentCourseDetailView
app_name = 'students'

urlpatterns = [
    path('courses/',
         StudentCourseListView.as_view(), name='student_course_list'),
    path('subject/all/',
         CourseListView.as_view(), name='course_list'),
    path('subject/<slug:subject>/',
         CourseListView.as_view(), name='course_list_subject'),
    path('<slug:course>/',
         CourseDetailView.as_view(), name='course_detail'),

    path('course/<int:course_id>/',
         StudentCourseDetailView.as_view(), name='student_course_detail'),
    path('course/<int:course_id>/<int:module_id>/',
         StudentCourseDetailView.as_view(), name='student_course_detail_module'),
]
