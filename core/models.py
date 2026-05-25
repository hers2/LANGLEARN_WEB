from django.db import models
from django.contrib.auth.models import User

class QuizProgress(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    score = models.IntegerField(default=0)
    total_quiz = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    
    # WAJIB TAMBAHKAN KOLOM INI: Untuk menyimpan skor per topik (Business & Travel)
    topic_stats = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.user.username