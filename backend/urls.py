from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('', RedirectView.as_view(url=reverse_lazy('students:course_list'))),
    path('my_courses/', include('courses.urls', namespace='courses')),
    path('browse/', include('students.urls', namespace='students')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
