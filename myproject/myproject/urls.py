from django.contrib import admin
from django.urls import path

from myapp.views import get_schedule

urlpatterns = [
    path("admin/", admin.site.urls),
    path('schedule/', get_schedule, name='get_schedule')
]
