# sensory_project/views.py
from django.http import HttpResponse
# 또는 from django.shortcuts import render
from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')
    return HttpResponse("<h1>메인 페이지</h1><p>/survey/ 로 이동해주세요.</p>")
