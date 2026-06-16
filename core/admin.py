from django.contrib import admin

from .models import (
    QuizProgress,
    GrammarCheck,
    GrammarMistake,
    ConversationSession,
    ConversationMessage,
    VocabularyQuestion,
    QuizAttempt,
    QuizAnswer,
)


class GrammarMistakeInline(admin.TabularInline):
    model = GrammarMistake
    extra = 0


@admin.register(GrammarCheck)
class GrammarCheckAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'created_at')
    search_fields = ('user__username', 'original_text', 'corrected_text')
    list_filter = ('created_at', 'score')
    inlines = [GrammarMistakeInline]


@admin.register(GrammarMistake)
class GrammarMistakeAdmin(admin.ModelAdmin):
    list_display = ('mistake_type', 'original', 'correction')
    search_fields = ('mistake_type', 'original', 'correction')
    list_filter = ('mistake_type',)


class ConversationMessageInline(admin.TabularInline):
    model = ConversationMessage
    extra = 0


@admin.register(ConversationSession)
class ConversationSessionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'topic',
        'custom_topic',
        'is_finished',
        'created_at',
    )
    list_filter = ('topic', 'is_finished', 'created_at')
    search_fields = ('user__username', 'custom_topic', 'summary')
    inlines = [ConversationMessageInline]


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'created_at')
    search_fields = ('text',)
    list_filter = ('sender', 'created_at')


@admin.register(VocabularyQuestion)
class VocabularyQuestionAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'category',
        'difficulty',
        'correct_option',
        'is_active',
    )
    list_filter = ('category', 'difficulty', 'is_active')
    search_fields = ('question', 'category')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'score',
        'total_questions',
        'correct_answers',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = ('user__username',)


@admin.register(QuizProgress)
class QuizProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'total_quiz', 'correct_answers')
    search_fields = ('user__username',)


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = (
        'attempt',
        'question',
        'selected_option',
        'is_correct',
        'created_at',
    )
    list_filter = ('is_correct', 'created_at')