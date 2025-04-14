# survey/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 기본 설문 페이지
    path('', views.survey_form_view, name='survey_form'),
     path('done/<int:set_id>/', views.survey_done_view, name='survey_done'),
    path('designer/', views.designer_view, name='designer_view'),
    path('designer/<int:set_id>/add-question/', views.add_question_view, name='add_question'),
    path('today/', views.today_survey_view, name='today_survey'),
    path('list/', views.survey_list_view, name='survey_list'),
    
    # 설문 만들기 2단계
    path('create/', views.create_menu_view, name='create_menu'),
    path('create/from-list/', views.create_from_list_view, name='create_from_list'),
    path('create/copy/<int:set_id>/', views.copy_and_edit_view, name='copy_and_edit'),

    # 이점검사 생성 (구형)
    path('create/dif-test/', views.create_dif_test_view, name='create_dif_test'),
    
     # (추가) preview 용 url (필요하다면)
    path('create/dif-test/preview/', views.create_dif_test_preview, name='create_dif_test_preview'),
    path('create/dif-test/confirm/', views.create_dif_test_confirm, name='create_dif_test_confirm'),

    # 평가 선택
    path('create/select/', views.create_select_type_view, name='create_select_type'),
    path('create/select/<str:chosen_type>/', views.create_survey_by_type_view, name='create_by_type'),

    # 응답(기존 do_survey_view) -> 제거 or 주석
    # path('do/<int:set_id>/', views.do_survey_view, name='do_survey'),  # 제거

    # 새 이점검사 평가 로직
    path('diff/<int:set_id>/', views.do_diff_test_view, name='do_diff_test'),

    # 응답확인 & 다운로드
    path('responses/<int:set_id>/', views.survey_responses_view, name='survey_responses'),
    path('responses/<int:set_id>/download/', views.download_csv, name='download_csv'),
]
