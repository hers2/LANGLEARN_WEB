from django.core.management.base import BaseCommand
from core.models import VocabularyQuestion


class Command(BaseCommand):
    help = 'Seed contoh soal vocabulary quiz ke database'

    def handle(self, *args, **kwargs):
        data = [
            ('What does the word "Resilient" mean?', 'Easily broken', 'Very attractive', 'Able to recover quickly from difficulties', 'Moving fast', 'C', 'Business', 'Medium'),
            ('What does the idiom "Break the ice" mean?', 'Start a friendly conversation', 'Destroy something cold', 'Become angry', 'End a relationship', 'A', 'Business', 'Easy'),
            ('What does the word "Reliable" mean?', 'Can be trusted', 'Dangerous', 'Expensive', 'Nervous', 'A', 'Business', 'Easy'),
            ('What does the idiom "Hit the books" mean?', 'Throw books away', 'Buy books', 'Study hard', 'Write a novel', 'C', 'Education', 'Easy'),
            ('What does the word "Generous" mean?', 'Selfish', 'Willing to give and share', 'Angry', 'Dishonest', 'B', 'Daily Conversation', 'Easy'),
            ('What does the idiom "Spill the beans" mean?', 'Cook food', 'Reveal a secret', 'Waste money', 'Make a joke', 'B', 'Daily Conversation', 'Medium'),
            ('What does the word "Confident" mean?', 'Believing in your abilities', 'Easily scared', 'Very angry', 'Uncertain', 'A', 'Job Interview', 'Easy'),
            ('What does "reservation" mean?', 'Booking a place or service', 'Buying clothes', 'Losing a ticket', 'Canceling travel', 'A', 'Travel', 'Easy'),
            ('What does "destination" mean?', 'The place you are going to', 'A small bag', 'A train ticket', 'A type of food', 'A', 'Travel', 'Easy'),
            ('What does "receipt" mean?', 'Proof of payment', 'Discount card', 'Shopping basket', 'Price label', 'A', 'Shopping', 'Easy'),
        ]

        created = 0
        for question, a, b, c, d, answer, category, difficulty in data:
            obj, is_created = VocabularyQuestion.objects.get_or_create(
                question=question,
                defaults={
                    'option_a': a,
                    'option_b': b,
                    'option_c': c,
                    'option_d': d,
                    'correct_option': answer,
                    'category': category,
                    'difficulty': difficulty,
                    'is_active': True,
                }
            )
            if is_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} soal berhasil ditambahkan.'))
