# sensory_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import render
from .views import home_view  # 메인 페이지 뷰

# [삭제] from . import views  ← 여기서 ImportError가 나고 있음

def home_view(request):
    return render(request, 'home.html')
    return HttpResponse("<h1>메인 페이지</h1><p>/survey/ 로 이동해주세요.</p>")

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('survey/', include('survey.urls')),
]
