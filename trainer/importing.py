import os
from datetime import datetime

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from pydub import AudioSegment

from text.processing import default_line_processors, processed_string, default_word_processors, standard_date
from trainer.models import ProblemSet, Setting
from trainer.utils import *


class Importer:

    @staticmethod
    @transaction.atomic
    def from_subtitles(original_lines: List[str], translation_lines: List[str], name: str, audio_file) -> None:
        problem_set_name = name
        langapp_settings = Setting.objects.first()
        before_start = langapp_settings.import_audio_time_added_before
        after_start = langapp_settings.import_audio_time_added_after
        if len(ProblemSet.objects.filter(name=name)) > 0:
            problem_set_name += f'{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}'
        problem_set = ProblemSet(name=problem_set_name, create_date=timezone.now())
        whole_audio = None
        if audio_file is not None:
            whole_audio = AudioSegment.from_file(audio_file)
            os.makedirs(os.path.join(settings.MEDIA_ROOT, problem_set.name), exist_ok=True)
        problem_set.save()
        problem_num = 0
        missed = 0
        for i in range(len(original_lines)):
            if i % 3 == 0:
                problem = Problem(problem_set_id=problem_set.id, create_date=timezone.now(), problem_number=problem_num)
            elif i % 3 == 1:
                time_text = original_lines[i]
                start_total, end_total = timetext_to_time(time_text)
                if whole_audio is not None:
                    token_audio = whole_audio[(start_total - before_start) * 1000:(end_total + after_start) * 1000]
                    token_url = f'{settings.MEDIA_ROOT}/{problem_set.name}/{problem_num}.wav'
                    token_audio.export(token_url, format="wav")
                    problem.audio_file = f'{settings.MEDIA_URL}/{problem_set.name}/{problem_num}.wav'
            elif i % 3 == 2:
                processors = default_line_processors()
                sentence = processed_string(original_lines[i], processors)
                problem.sentence = sentence
                if translation_lines is not None:
                    problem.translation = guess_trans_line(start_total, end_total, translation_lines, 0.7)
                    if problem.translation is None:
                        print(f'Warning: Translation for problem "{sentence}" missing ({int(i / 3)})')
                        missed += 1
                words = sentence.split()
                for word in words:
                    word = processed_string(word, default_word_processors())
                    word = Word(word)
                    word.save()
                problem.save()
                problem_num += 1

        print("Import finished")
        print(f"{missed} out of {problem_num} translations missed (~{round(missed / problem_num * 100, 1)}%)")
