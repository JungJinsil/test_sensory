from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from .models import QuestionSet, Question, Response, ResponseDetail
import random
import csv
import json
from datetime import datetime  # 수정: from datetime import datetime

##################################
# 1. 기본적인 설문 예시
##################################

def survey_form_view(request):
    print("[DEBUG] survey_form_view called. method =", request.method)
    if request.method == 'POST':
        print("[DEBUG] -> POST -> redirect to 'survey_done'")
        return redirect('survey_done', set_id=0)  # 임시로 0 등으로
    else:
        print("[DEBUG] -> GET -> render 'survey_form.html'")
        return render(request, 'survey/survey_form.html')

def survey_done_view(request, set_id):
    # "set_id"를 템플릿에 넘겨주기
    return render(request, 'survey/survey_done.html', {'set_id': set_id})


##################################
# 2. 디자이너 페이지 (문항 수정/추가)
##################################

def designer_view(request):
    """
    /survey/designer/
    """
    print("[DEBUG] designer_view called. method =", request.method)
    if request.method == 'POST':
        name = request.POST.get('name')
        print("[DEBUG] designer_view POST -> name =", name)
        if not name:
            return HttpResponse("QuestionSet 이름이 필요합니다.", status=400)
        new_set = QuestionSet.objects.create(name=name)
        print(f"[DEBUG] Created new QuestionSet id={new_set.id}, name='{new_set.name}'")
        return redirect('designer_view')
    else:
        print("[DEBUG] designer_view GET -> list all QuestionSets")
        all_sets = QuestionSet.objects.all().order_by('-created_at')
        print("[DEBUG] total QuestionSet count =", all_sets.count())
        return render(request, 'survey/designer.html', {
            'question_sets': all_sets
        })

def add_question_view(request, set_id):
    """
    /survey/designer/<int:set_id>/add-question/
    """
    print("[DEBUG] add_question_view called. set_id =", set_id, "method =", request.method)
    qs = get_object_or_404(QuestionSet, id=set_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        question_type = request.POST.get('question_type', 'scale_5')
        print("[DEBUG] add_question_view POST -> text =", text, "question_type =", question_type)
        if not text:
            return HttpResponse("질문 내용이 필요합니다.", status=400)
        new_q = Question.objects.create(
            question_set=qs,
            text=text,
            question_type=question_type
        )
        print(f"[DEBUG] Created Question id={new_q.id}, text='{new_q.text}'")
        return redirect('designer_view')
    else:
        print("[DEBUG] add_question_view GET -> render 'add_question.html'")
        return render(request, 'survey/add_question.html', {
            'question_set': qs
        })


##################################
# 3. 오늘의 평가
##################################

def today_survey_view(request):
    print("[DEBUG] today_survey_view called.")
    todays = QuestionSet.objects.filter(is_today=True).order_by('-created_at')
    print("[DEBUG] is_today=True sets count =", todays.count())
    return render(request, 'survey/today.html', {
        'todays': todays
    })


##################################
# 4. 설문목록(전체)
##################################

def survey_list_view(request):
    print("[DEBUG] survey_list_view called. method =", request.method)
    all_sets = QuestionSet.objects.all().order_by('-created_at')
    print("[DEBUG] total QuestionSet count =", all_sets.count())
    return render(request, 'survey/survey_list.html', {
        'surveys': all_sets
    })


##################################
# 5. (신형) 2단계 설문 만들기 로직
##################################

def create_menu_view(request):
    print("[DEBUG] create_menu_view called.")
    return render(request, 'survey/create_menu.html')

def create_from_list_view(request):
    print("[DEBUG] create_from_list_view called.")
    all_sets = QuestionSet.objects.all().order_by('-created_at')
    print("[DEBUG] total sets count =", all_sets.count())
    return render(request, 'survey/create_from_list.html', {
        'surveys': all_sets
    })

def copy_and_edit_view(request, set_id):
    print("[DEBUG] copy_and_edit_view called. set_id =", set_id, "method =", request.method)
    source = get_object_or_404(QuestionSet, id=set_id)
    if request.method == 'POST':
        new_name = request.POST.get('new_name', "")
        print("[DEBUG] copy_and_edit_view POST -> new_name =", new_name)
        if not new_name:
            return HttpResponse("새 설문 이름이 필요합니다.", status=400)
        new_set = QuestionSet.objects.create(
            name=new_name,
            survey_type=source.survey_type
        )
        print(f"[DEBUG] Copied new_set id={new_set.id}, name='{new_set.name}' from id={source.id}")
        for q in source.questions.all():
            new_q = Question.objects.create(
                question_set=new_set,
                text=q.text,
                question_type=q.question_type
            )
            print(f"[DEBUG] Copied question id={new_q.id}, text='{new_q.text}'")
        return redirect('survey_list')
    else:
        print("[DEBUG] copy_and_edit_view GET -> render 'copy_edit.html'")
        return render(request, 'survey/copy_edit.html', {
            'source_set': source
        })

def create_select_type_view(request):
    print("[DEBUG] create_select_type_view called. method =", request.method)
    return render(request, 'survey/create_select.html')

def create_survey_by_type_view(request, chosen_type):
    """
    /survey/create/select/<str:chosen_type>/
    """
    print("[DEBUG] create_survey_by_type_view called. chosen_type =", chosen_type, "method =", request.method)
    if request.method == 'POST':
        if chosen_type == '이점검사':
            return redirect('create_dif_test')
        elif chosen_type == '삼점검사':
            return redirect('create_tri_test')  # 새로 추가
        else:
            return redirect('survey_list')
    else:
        print("[DEBUG] create_survey_by_type_view -> GET method")
        return render(request, 'survey/create_by_type.html', {
            'chosen_type': chosen_type
        })


##################################
# 6. 이점검사 설문 만들기 (두 단계: 미리보기 -> 확인)
##################################

def create_dif_test_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        set_count_str = request.POST.get('set_count', '1')
        try:
            set_count = int(set_count_str)
        except ValueError:
            set_count = 1

        action = request.POST.get('action')  # 'preview' or 'create'

        if action == 'preview':
            # 미리보기
            request.session['dif_test_data'] = {
                'title': title,
                'description': description,
                'set_count': set_count
            }
            return redirect('create_dif_test_preview')

        elif action == 'create':
            # 즉시 생성
            total_samples = set_count * 2
            excluded = {'111','222','333','444','555','666','777','888','999'}
            used_codes = set()
            all_codes = []
            while len(all_codes) < total_samples:
                code = str(random.randint(101,999))
                if code not in used_codes and code not in excluded:
                    used_codes.add(code)
                    all_codes.append(code)

            pairs = []
            idx = 0
            for i in range(set_count):
                pairs.append([all_codes[idx], all_codes[idx+1]])
                idx += 2

            new_set = QuestionSet.objects.create(
                name=title,
                survey_type='이점검사',
                set_count=set_count,
                codes_json=json.dumps(pairs)
            )
            return render(request, 'survey/dif_test_result.html', {
                'title': title,
                'description': description,
                'set_count': set_count,
                'pairs': pairs,
                'set_id': new_set.id
            })
        else:
            return HttpResponse("잘못된 요청", status=400)

    else:
        return render(request, 'survey/create_dif_test.html')

def create_dif_test_preview(request):
    stored = request.session.get('dif_test_data')
    if not stored:
        return redirect('create_dif_test')

    title = stored['title']
    description = stored['description']
    set_count = stored['set_count']

    total_samples = set_count * 2
    excluded = {'111','222','333','444','555','666','777','888','999'}
    used = set()
    codes = []
    while len(codes) < total_samples:
        code = str(random.randint(101,999))
        if code not in used and code not in excluded:
            used.add(code)
            codes.append(code)

    pairs = []
    idx = 0
    for i in range(set_count):
        pairs.append([codes[idx], codes[idx+1]])
        idx += 2

    return render(request, 'survey/dif_test_preview.html', {
        'title': title,
        'description': description,
        'set_count': set_count,
        'pairs': pairs
    })

def create_dif_test_confirm(request):
    stored = request.session.get('dif_test_data')
    if not stored:
        return redirect('create_dif_test')

    title = stored['title']
    description = stored['description']
    set_count = stored['set_count']

    total_samples = set_count * 2
    excluded = {'111','222','333','444','555','666','777','888','999'}
    used_codes = set()
    all_codes = []
    while len(all_codes) < total_samples:
        code = str(random.randint(101,999))
        if code not in used_codes and code not in excluded:
            used_codes.add(code)
            all_codes.append(code)

    pairs = []
    idx = 0
    for i in range(set_count):
        pairs.append([all_codes[idx], all_codes[idx+1]])
        idx += 2

    new_set = QuestionSet.objects.create(
        name=title,
        survey_type='이점검사',
        set_count=set_count,
        codes_json=json.dumps(pairs)
    )
    del request.session['dif_test_data']

    return render(request, 'survey/dif_test_result.html', {
        'title': title,
        'description': description,
        'set_count': set_count,
        'pairs': pairs,
        'set_id': new_set.id,
    })


##################################
# [새로 추가] 6. 삼점검사 설문 만들기
##################################

def create_tri_test_view(request):
    """
    /survey/create/tri-test/
    삼점검사 설문 만들기:
      - GET -> 기본값(오늘날짜+\" (삼점검사)\", 설명문, Set=2) 표시
      - POST -> 시료코드 3개씩 set_count*3 생성 -> DB 저장 -> tri_test_result.html
    """
    if request.method == 'POST':
        # 1) 폼 입력
        title = request.POST.get('title')
        description = request.POST.get('description')
        set_count_str = request.POST.get('set_count', '2')
        try:
            set_count = int(set_count_str)
        except ValueError:
            set_count = 2

        # 2) 시료코드 생성 (3개씩)
        total_samples = set_count * 3
        excluded = {'111','222','333','444','555','666','777','888','999'}
        used_codes = set()
        all_codes = []
        while len(all_codes) < total_samples:
            code = str(random.randint(101,999))
            if code not in used_codes and code not in excluded:
                used_codes.add(code)
                all_codes.append(code)

        # 3) triplets
        triplets = []
        idx = 0
        for i in range(set_count):
            triplets.append([all_codes[idx], all_codes[idx+1], all_codes[idx+2]])
            idx += 3

        # 4) DB에 QuestionSet 저장(survey_type='삼점검사')
        new_set = QuestionSet.objects.create(
            name=title,
            survey_type='삼점검사',
            set_count=set_count,
            codes_json=json.dumps(triplets)
        )

        # 5) 결과 페이지
        return render(request, 'survey/tri_test_result.html', {
            'title': title,
            'description': description,
            'set_count': set_count,
            'triplets': triplets,
            'set_id': new_set.id,
        })

    else:
        # GET -> 기본값
        today_str = datetime.now().strftime("%y%m%d")  # 예) "250329"
        default_title = f"{today_str} (삼점검사)"
        default_description = "세 시료 중 다른 하나를 선택해 주세요."
        default_set_count = 2

        return render(request, 'survey/create_tri_test.html', {
            'default_title': default_title,
            'default_description': default_description,
            'default_set_count': default_set_count,
        })


##################################
# 7. 설문 응답(do) - 이점검사 로직
##################################

def do_diff_test_view(request, set_id):
    """
    /survey/diff/<int:set_id>/
    ...
    """
    question_set = get_object_or_404(QuestionSet, id=set_id)
    set_count = question_set.set_count
    pairs = json.loads(question_set.codes_json)

    sets_data = []
    for i, pair in enumerate(pairs, start=1):
        random.shuffle(pair)
        sets_data.append({
            "set_no": i,
            "codes": pair
        })

    if request.method == "POST":
        panel_name = request.POST.get("panel_name", "").strip()
        etc_opinion = request.POST.get("etc_opinion", "").strip()

        resp = Response.objects.create(
            question_set=question_set,
            panel_name=panel_name,
            etc_opinion=etc_opinion
        )
        for sdata in sets_data:
            s_no = sdata["set_no"]
            chosen_code = request.POST.get(f"set_{s_no}")
            if chosen_code:
                ResponseDetail.objects.create(
                    response=resp,
                    question=None,
                    answer_text=f"{s_no}Set {chosen_code}"
                )
        return redirect('survey_done', set_id=set_id)
    else:
        return render(request, 'survey/do_diff_test.html', {
            "question_set": question_set,
            "description": "이점검사 설명문",
            "sets_data": sets_data
        })


##################################
# 8. 응답확인 & 다운로드
##################################

def survey_responses_view(request, set_id):
    qs = get_object_or_404(QuestionSet, id=set_id)
    responses = Response.objects.filter(question_set=qs).order_by('-id')

    max_set_count = qs.set_count or 1

    table_rows = []
    for r in responses:
        panel_name = r.panel_name if r.panel_name else f"Resp#{r.id}"

        set_dict = {}
        for i in range(1, max_set_count+1):
            set_dict[f"{i}Set"] = ""

        for detail in r.details.all():
            splitted = detail.answer_text.split()
            if len(splitted) == 2:
                set_label = splitted[0]
                code_val = splitted[1]
                set_dict[set_label] = code_val
        
        row_array = [panel_name]
        for i in range(1, max_set_count+1):
            key = f"{i}Set"
            row_array.append(set_dict[key])
        
        table_rows.append(row_array)

    range_list = range(1, max_set_count + 1)

    return render(request, 'survey/survey_responses.html', {
        'question_set': qs,
        'table_rows': table_rows,
        'range_list': range_list,
    })

def download_csv(request, set_id):
    qs = get_object_or_404(QuestionSet, id=set_id)
    responses = Response.objects.filter(question_set=qs).order_by('id')
    max_set_count = qs.set_count or 1

    response = HttpResponse(content_type='text/csv')
    filename = f"{qs.name}_responses.csv".replace(' ', '_')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    header = ["패널이름"] + [f"{i}Set" for i in range(1, max_set_count+1)]
    writer.writerow(header)

    for r in responses:
        panel_name = r.panel_name if r.panel_name else f"Resp#{r.id}"
        set_dict = {}
        for i in range(1, max_set_count+1):
            set_dict[f"{i}Set"] = ""
        for detail in r.details.all():
            splitted = detail.answer_text.split()
            if len(splitted) == 2:
                set_label, code_val = splitted
                set_dict[set_label] = code_val

        row_array = [panel_name]
        for i in range(1, max_set_count+1):
            row_array.append(set_dict[f"{i}Set"])

        writer.writerow(row_array)

    return response
