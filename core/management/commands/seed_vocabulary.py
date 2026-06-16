from django.core.management.base import BaseCommand
from core.models import VocabularyQuestion


DEFAULT_QUESTIONS = [
    ('Business', 'Easy', 'What does the word "Resilient" mean?', 'Easily broken or damaged', 'Very attractive and charming', 'Able to recover quickly from difficulties', 'Moving at a very fast pace', 'C'),
    ('Business', 'Easy', 'What does the idiom "Break the ice" mean?', 'Start a friendly conversation', 'Destroy something cold', 'Become angry', 'End a relationship', 'A'),
    ('Business', 'Easy', 'What does the word "Ambitious" mean?', 'Lazy', 'Having strong goals and determination', 'Easily bored', 'Very shy', 'B'),
    ('Business', 'Easy', 'What does the idiom "Piece of cake" mean?', 'A dessert', 'Something expensive', 'Something very easy', 'Something impossible', 'C'),
    ('Business', 'Easy', 'What does the word "Reliable" mean?', 'Can be trusted', 'Dangerous', 'Expensive', 'Nervous', 'A'),
    ('Travel', 'Easy', 'What does the idiom "Hit the books" mean?', 'Throw books away', 'Buy books', 'Study hard', 'Write a novel', 'C'),
    ('Travel', 'Easy', 'What does the word "Generous" mean?', 'Selfish', 'Willing to give and share', 'Angry', 'Dishonest', 'B'),
    ('Travel', 'Easy', 'What does the idiom "Spill the beans" mean?', 'Cook food', 'Reveal a secret', 'Waste money', 'Make a joke', 'B'),
    ('Travel', 'Easy', 'What does the word "Confident" mean?', 'Believing in your abilities', 'Easily scared', 'Very angry', 'Uncertain', 'A'),
    ('Travel', 'Easy', 'What does the idiom "Under the weather" mean?', 'Feeling sick', 'Traveling abroad', 'Feeling excited', 'Going outside', 'A'),
]


class Command(BaseCommand):
    help = 'Seed default vocabulary quiz questions into database'

    def handle(self, *args, **options):
        created = 0
        for topic, level, question, a, b, c, d, answer in DEFAULT_QUESTIONS:
            obj, was_created = VocabularyQuestion.objects.get_or_create(
                question=question,
                defaults={
                    'topic': topic,
                    'level': level,
                    'option_a': a,
                    'option_b': b,
                    'option_c': c,
                    'option_d': d,
                    'correct_answer': answer,
                    'is_active': True,
                }
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} default quiz questions added.'))
