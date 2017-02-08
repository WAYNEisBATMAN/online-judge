from django.conf.urls import include, url
from django.contrib import admin
from judge.views import home, upload_code, upload_files, compile_code, execute_code

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home),
    url(r'^upload_code/', upload_code),
    url(r'^upload_files/', upload_files),
    url(r'^compile_code/', compile_code),
    url(r'^execute_code/', execute_code)
]
