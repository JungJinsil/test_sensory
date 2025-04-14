# survey/models.py
from django.db import models

class QuestionSet(models.Model):
    name = models.CharField(max_length=200)
    survey_type = models.CharField(max_length=50, null=True, blank=True)
    is_today = models.BooleanField(default=False)  # '오늘의 평가' 여부
    created_at = models.DateTimeField(auto_now_add=True)

    # 이점검사용: Set 수, 시료코드 JSON 등
    set_count = models.IntegerField(default=1)
    codes_json = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=50, default='scale_5')

    def __str__(self):
        return f"[{self.question_set.name}] {self.text}"


class Response(models.Model):
    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # (추가) 패널 이름 & 기타 의견
    panel_name = models.CharField(max_length=100, null=True, blank=True)
    etc_opinion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Response id={self.id}, set={self.question_set.name}"


class ResponseDetail(models.Model):
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        related_name='details'
    )
    # question에 null=True, blank=True
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    answer_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Resp={self.response_id}, Q={self.question_id}, Ans={self.answer_text}"
