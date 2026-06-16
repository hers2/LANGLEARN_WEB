from django.db import models
from django.contrib.auth.models import User


class QuizProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_quiz = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    topic_stats = models.JSONField(default=dict, blank=True)

    def accuracy(self):
        if self.total_quiz == 0:
            return 0
        return int((self.correct_answers / self.total_quiz) * 100)

    def __str__(self):
        return self.user.username


class GrammarCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grammar_checks')
    original_text = models.TextField()
    corrected_text = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - Grammar Check {self.created_at:%Y-%m-%d}'


class GrammarMistake(models.Model):
    grammar_check = models.ForeignKey(
        GrammarCheck,
        on_delete=models.CASCADE,
        related_name='mistakes'
    )
    mistake_type = models.CharField(max_length=100, default='General Grammar')
    original = models.CharField(max_length=255, blank=True)
    correction = models.CharField(max_length=255, blank=True)
    explanation = models.TextField(blank=True)

    def __str__(self):
        return f'{self.mistake_type}: {self.original} -> {self.correction}'


class ConversationSession(models.Model):
    TOPIC_CHOICES = [
        ('Daily Conversation', 'Daily Conversation'),
        ('Travel', 'Travel'),
        ('Education', 'Education'),
        ('Job Interview', 'Job Interview'),
        ('Business', 'Business'),
        ('Restaurant', 'Restaurant'),
        ('Shopping', 'Shopping'),
        ('Custom', 'Custom'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_sessions')
    topic = models.CharField(max_length=100, choices=TOPIC_CHOICES)
    custom_topic = models.CharField(max_length=150, blank=True)
    summary = models.TextField(blank=True)
    grammar_score = models.IntegerField(default=0)
    vocabulary_score = models.IntegerField(default=0)
    fluency_score = models.IntegerField(default=0)
    recommendation = models.TextField(blank=True)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    @property
    def display_topic(self):
        if self.topic == 'Custom' and self.custom_topic:
            return self.custom_topic
        return self.topic

    def __str__(self):
        return f'{self.user.username} - {self.display_topic}'


class ConversationMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI'),
    ]

    session = models.ForeignKey(
        ConversationSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender}: {self.text[:40]}'


class VocabularyQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(
        max_length=1,
        choices=[
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
        ]
    )
    category = models.CharField(max_length=100, default='General')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Easy')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'difficulty', 'id']

    def options(self):
        return [
            ('A', self.option_a),
            ('B', self.option_b),
            ('C', self.option_c),
            ('D', self.option_d),
        ]

    def __str__(self):
        return f'[{self.category}] {self.question[:60]}'


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.score}'


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(VocabularyQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.question_id} - {self.selected_option}'