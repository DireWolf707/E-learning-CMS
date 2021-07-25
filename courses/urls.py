from django.urls import path
from .views import ManageContentListView, ManageContentDeleteView, ManageCourseListView, ManageCourseCreateUpdateView, ManageCourseDeleteView, ManageModuleView, ManageContentCreateUpdateView, ContentOrderView, ModuleOrderView
app_name = 'manage_courses'

urlpatterns = [
    # Course
    path('', ManageCourseListView.as_view(), name='manage_course_list'),
    path('create/', ManageCourseCreateUpdateView.as_view(),
         name='manage_course_create'),
    path('<int:pk>/edit/', ManageCourseCreateUpdateView.as_view(),
         name='manage_course_edit'),
    path('<int:pk>/delete/', ManageCourseDeleteView.as_view(),
         name='manage_course_delete'),
    # Module
    path('<int:pk>/modules/', ManageModuleView.as_view(),
         name='manage_module'),
    # Content
    path('<int:module_id>/module/content/<str:model_name>/create/', ManageContentCreateUpdateView.as_view(),
         name='manage_content_create'),
    path('<int:module_id>/module/content/<str:model_name>/<int:item_id>/', ManageContentCreateUpdateView.as_view(),
         name='manage_content_update'),
    path('content/<int:content_id>/delete/', ManageContentDeleteView.as_view(),
         name='manage_content_delete'),
    path('<int:module_id>/module/', ManageContentListView.as_view(),
         name='manage_content_list'),
    # Order
    path('content_order/', ContentOrderView.as_view(),
         name='manage_content_order'),
    path('module_order/', ModuleOrderView.as_view(),
         name='manage_module_order'),

]
