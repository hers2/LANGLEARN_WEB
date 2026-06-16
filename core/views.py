from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count

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
from .forms import VocabularyQuestionForm
from .ai_helper import ai_conversation, check_grammar, analyze_conversation


def is_operator(user):
    return user.is_authenticated and user.is_staff


@login_required(login_url='login')
def dashboard_view(request):
    progress, _ = QuizProgress.objects.get_or_create(user=request.user)

    grammar_count = GrammarCheck.objects.filter(user=request.user).count()
    conversation_count = ConversationSession.objects.filter(user=request.user).count()

    latest_recommendation = ''
    last_conversation = (
        ConversationSession.objects
        .filter(user=request.user)
        .exclude(recommendation='')
        .first()
    )

    if last_conversation:
        latest_recommendation = last_conversation.recommendation

    top_mistake = (
        GrammarMistake.objects
        .filter(grammar_check__user=request.user)
        .values('mistake_type')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )

    return render(request, 'dashboard.html', {
        'progress': progress,
        'accuracy': progress.accuracy(),
        'grammar_count': grammar_count,
        'conversation_count': conversation_count,
        'latest_recommendation': latest_recommendation,
        'top_mistake': top_mistake,
    })


def login_view(request):
    if request.method == 'POST':
        username_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = None

        if '@' in username_input:
            try:
                user_obj = User.objects.get(email=username_input)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password
                )
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(
                request,
                username=username_input,
                password=password
            )

        if user is not None:
            login(request, user)
            messages.success(
                request,
                f'Welcome back, {user.first_name or user.username} 👋'
            )
            return redirect(request.GET.get('next') or 'dashboard')

        messages.error(request, 'Username/email atau password salah.')

    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'Semua field wajib diisi.')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Konfirmasi password tidak cocok.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah digunakan.')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=fullname
        )

        QuizProgress.objects.create(user=user)

        messages.success(request, 'Registrasi berhasil! Silakan login. 🎉')
        return redirect('login')

    return render(request, 'register.html')


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, 'Berhasil logout.')
    return redirect('login')


@login_required(login_url='login')
def grammar_view(request):
    result = None
    user_text = ''

    if request.method == 'POST':
        user_text = request.POST.get('text', '').strip()

        if user_text:
            response = check_grammar(user_text)

            if response.get('success'):
                data = response.get('data', {})

                result = {
                    'original': user_text,
                    'corrected': data.get('corrected', user_text),
                    'errors': data.get('errors', []),
                }

                grammar_check = GrammarCheck.objects.create(
                    user=request.user,
                    original_text=user_text,
                    corrected_text=result['corrected'],
                    score=data.get('score', 0),
                    feedback=data.get('feedback', ''),
                )

                errors = result['errors']

                if errors:
                    for err in errors:
                        mistake_type = err.get('type', 'General Grammar')

                        if 'vocabulary' in mistake_type.lower() or 'word' in mistake_type.lower():
                            mistake_type = 'Vocabulary'

                        GrammarMistake.objects.create(
                            grammar_check=grammar_check,
                            mistake_type=mistake_type,
                            original=err.get('original', ''),
                            correction=err.get('correction', ''),
                            explanation=err.get('explanation', ''),
                        )
                else:
                    GrammarMistake.objects.create(
                        grammar_check=grammar_check,
                        mistake_type='No Grammar Mistake',
                        original=user_text,
                        correction=result['corrected'],
                        explanation='Kalimat sudah cukup baik dan tidak ditemukan kesalahan grammar utama.'
                    )

            else:
                result = {
                    'original': user_text,
                    'corrected': 'Gagal menganalisis.',
                    'errors': [],
                }

    top_errors = (
        GrammarMistake.objects
        .filter(grammar_check__user=request.user)
        .exclude(mistake_type='No Grammar Mistake')
        .values('mistake_type')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    return render(request, 'grammar.html', {
        'result': result,
        'user_text': user_text,
        'top_errors': top_errors,
    })


@login_required(login_url='login')
def grammar_history_by_type_view(request, mistake_type):
    histories = (
        GrammarMistake.objects
        .filter(
            grammar_check__user=request.user,
            mistake_type=mistake_type
        )
        .select_related('grammar_check')
        .order_by('-grammar_check__created_at')
    )

    return render(request, 'grammar_history_by_type.html', {
        'mistake_type': mistake_type,
        'histories': histories,
    })


@login_required(login_url='login')
def chat_start_view(request):
    if request.method == 'POST':
        topic = request.POST.get('topic', 'Daily Conversation')
        custom_topic = request.POST.get('custom_topic', '').strip()

        session = ConversationSession.objects.create(
            user=request.user,
            topic=topic,
            custom_topic=custom_topic,
        )

        return redirect('chat_session', session_id=session.id)

    topics = [choice[0] for choice in ConversationSession.TOPIC_CHOICES]
    sessions = ConversationSession.objects.filter(user=request.user)[:8]

    return render(request, 'chat_start.html', {
        'topics': topics,
        'sessions': sessions
    })


@login_required(login_url='login')
def chat_session_view(request, session_id):
    session = get_object_or_404(
        ConversationSession,
        id=session_id,
        user=request.user
    )

    if request.method == 'POST' and not session.is_finished:
        user_message = request.POST.get('message', '').strip()

        if user_message:
            ConversationMessage.objects.create(
                session=session,
                sender='user',
                text=user_message
            )

            history = list(session.messages.values('sender', 'text'))

            response = ai_conversation(
                user_message,
                topic=session.display_topic,
                history=history
            )

            ConversationMessage.objects.create(
                session=session,
                sender='ai',
                text=response.get('message', 'Maaf, AI belum bisa merespons.')
            )

        return redirect('chat_session', session_id=session.id)

    return render(request, 'chat.html', {
        'session': session,
        'chat_history': session.messages.all()
    })


@login_required(login_url='login')
def finish_chat_view(request, session_id):
    session = get_object_or_404(
        ConversationSession,
        id=session_id,
        user=request.user
    )

    if request.method == 'POST':
        analysis = analyze_conversation(
            session.display_topic,
            session.messages.all()
        )

        session.summary = analysis.get('summary', '')
        session.grammar_score = analysis.get('grammar_score', 0)
        session.vocabulary_score = analysis.get('vocabulary_score', 0)
        session.fluency_score = analysis.get('fluency_score', 0)
        session.recommendation = analysis.get('recommendation', '')
        session.is_finished = True
        session.save()

        messages.success(
            request,
            'Percakapan selesai dan feedback AI sudah disimpan.'
        )

    return redirect('chat_session', session_id=session.id)


@login_required(login_url='login')
def clear_chat_view(request, session_id):
    session = get_object_or_404(
        ConversationSession,
        id=session_id,
        user=request.user
    )

    if request.method == 'POST':
        session.messages.all().delete()
        messages.success(request, 'Isi chat berhasil dibersihkan.')

    return redirect('chat_session', session_id=session.id)


@login_required(login_url='login')
def delete_chat_view(request, session_id):
    session = get_object_or_404(
        ConversationSession,
        id=session_id,
        user=request.user
    )

    if request.method == 'POST':
        session.delete()
        messages.success(request, 'History chat berhasil dihapus.')

    return redirect('chat')


@login_required(login_url='login')
def quiz_view(request):
    questions = list(
        VocabularyQuestion.objects
        .filter(is_active=True)
        .order_by('id')
    )

    if not questions:
        messages.warning(
            request,
            'Belum ada soal quiz. Operator perlu menambahkan soal dulu.'
        )
        return render(request, 'quiz.html', {
            'no_questions': True
        })

    current_index = int(request.GET.get('q', 0))

    if current_index >= len(questions):
        return redirect('progress')

    question = questions[current_index]
    selected_answer = None
    is_correct = False

    attempt_id = request.session.get('quiz_attempt_id')
    restart = request.GET.get('restart') == '1'

    if not attempt_id or (current_index == 0 and restart):
        attempt = QuizAttempt.objects.create(
            user=request.user,
            total_questions=len(questions)
        )
        request.session['quiz_attempt_id'] = attempt.id
        request.session['answered_questions'] = []
    else:
        attempt = get_object_or_404(
            QuizAttempt,
            id=attempt_id,
            user=request.user
        )

    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        answered_questions = request.session.get('answered_questions', [])
        is_correct = selected_answer == question.correct_option

        if question.id not in answered_questions:
            QuizAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_answer,
                is_correct=is_correct,
            )

            progress, _ = QuizProgress.objects.get_or_create(
                user=request.user
            )

            progress.total_quiz += 1

            if is_correct:
                progress.score += 10
                progress.correct_answers += 1
                attempt.correct_answers += 1
                attempt.score += 10

            topic = question.category

            if not progress.topic_stats:
                progress.topic_stats = {}

            if topic not in progress.topic_stats:
                progress.topic_stats[topic] = {
                    'correct': 0,
                    'total': 0
                }

            progress.topic_stats[topic]['total'] += 1

            if is_correct:
                progress.topic_stats[topic]['correct'] += 1

            progress.save()
            attempt.save()

            answered_questions.append(question.id)
            request.session['answered_questions'] = answered_questions
            request.session.modified = True

    return render(request, 'quiz.html', {
        'quiz': question,
        'question_number': current_index + 1,
        'total_questions': len(questions),
        'next_question': current_index + 1,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
    })


@login_required(login_url='login')
def progress_view(request):
    progress, _ = QuizProgress.objects.get_or_create(user=request.user)

    topic_data = []

    for topic, values in (progress.topic_stats or {}).items():
        total = values.get('total', 0)
        correct = values.get('correct', 0)
        score = int((correct / total) * 100) if total else 0

        topic_data.append({
            'name': topic,
            'score': score
        })

    top_errors = (
        GrammarMistake.objects
        .filter(grammar_check__user=request.user)
        .values('mistake_type')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    latest_sessions = ConversationSession.objects.filter(
        user=request.user,
        is_finished=True
    )[:5]

    badges = []

    if progress.total_quiz > 0:
        badges.append('First Quiz')

    if progress.total_quiz >= 7:
        badges.append('7 Day Streak')

    if progress.accuracy() >= 80 and progress.total_quiz > 0:
        badges.append('Top Scorer')

    return render(request, 'progress.html', {
        'progress': progress,
        'accuracy': progress.accuracy(),
        'topic_data': topic_data,
        'badges': badges,
        'top_errors': top_errors,
        'latest_sessions': latest_sessions,
    })


@login_required(login_url='login')
def reset_progress_view(request):
    if request.method == 'POST':
        progress, _ = QuizProgress.objects.get_or_create(user=request.user)

        progress.score = 0
        progress.total_quiz = 0
        progress.correct_answers = 0
        progress.topic_stats = {}
        progress.save()

        request.session.pop('quiz_attempt_id', None)
        request.session.pop('answered_questions', None)

        messages.success(request, 'Progress quiz berhasil direset!')

    return redirect('progress')


@user_passes_test(is_operator, login_url='dashboard')
def operator_questions_view(request):
    questions = VocabularyQuestion.objects.all()

    return render(request, 'operator_questions.html', {
        'questions': questions
    })


@user_passes_test(is_operator, login_url='dashboard')
def operator_question_create_view(request):
    form = VocabularyQuestionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Soal berhasil ditambahkan.')
        return redirect('operator_questions')

    return render(request, 'operator_question_form.html', {
        'form': form,
        'title': 'Tambah Soal'
    })


@user_passes_test(is_operator, login_url='dashboard')
def operator_question_update_view(request, pk):
    question = get_object_or_404(VocabularyQuestion, pk=pk)
    form = VocabularyQuestionForm(request.POST or None, instance=question)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Soal berhasil diupdate.')
        return redirect('operator_questions')

    return render(request, 'operator_question_form.html', {
        'form': form,
        'title': 'Edit Soal'
    })


@user_passes_test(is_operator, login_url='dashboard')
def operator_question_delete_view(request, pk):
    question = get_object_or_404(VocabularyQuestion, pk=pk)

    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Soal berhasil dihapus.')
        return redirect('operator_questions')

    return render(request, 'operator_question_delete.html', {
        'question': question
    })