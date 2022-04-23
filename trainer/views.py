import json
import random
import re

import django.http.request
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from text.processing import processed_string, default_word_processors, default_solution_processors, standard_date
from trainer.importing import Importer
from trainer.models import ProblemSet, Problem, Setting, Word, TrainingQueue, TrainingQueueItem, Bookmark
from trainer.subparsing import srt_from_vtt
from trainer.training import SolvableProblem
from trainer.utils import (
    ProblemSolution,
    get_real_problem_no,
    get_lines,
    update_problem_score,
    get_fake_problem_no,
    StatRecord,
)


def problem_set(request: django.http.request.HttpRequest):
    all_sets = ProblemSet.objects.all()
    all_bookmarks = Bookmark.objects.all()
    for set in all_sets:
        set.bookmarks = [b for b in all_bookmarks if b.problem.problem_set == set]
        for b in set.bookmarks:
            b.fake_number = get_fake_problem_no(set.id, b.problem.problem_number)
    context = {"problem_set_list": all_sets}
    return HttpResponse(render(request, "trainer/index.html", context))


def importing(request):
    return HttpResponse(render(request, "trainer/fromSubtitles.html"))


def success_import(request):
    return HttpResponse(render(request, "trainer/message.html", {"title": "Success", "message": "Import successful"}))


@transaction.atomic()
def create_queue(request):
    problem_set_id = request.POST["problem_set_id"]
    num_of_problems = int(request.POST["num_of_problems"])
    selected_problem_set = ProblemSet.objects.filter(id=problem_set_id).first()
    training_queue = TrainingQueue.objects.filter(problem_set=selected_problem_set, active=True).first()
    if training_queue is None:
        training_queue = TrainingQueue(date_created=timezone.now(), problem_set=selected_problem_set)
        training_queue.save()
        problems_from_set = list(
            Problem.objects.filter(problem_set=selected_problem_set, active=True).order_by("score")
        )[:num_of_problems]
        for i, problem in enumerate(problems_from_set):
            queue_item = TrainingQueueItem(item_number=i, queue=training_queue, problem=problem)
            queue_item.save()
        print(f"Queue {training_queue.id} with {[q.sentence for q in problems_from_set]} created")
    first_problem_number = (
        TrainingQueueItem.objects.filter(queue=training_queue, item_number=training_queue.current_item_number)
        .first()
        .problem.problem_number
    )
    request.POST = {"trainingQueueId": training_queue.id, "problemNumber": str(first_problem_number)}
    return training(request, selected_problem_set.id, 1)


@transaction.atomic()
def create_bookmark(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        name = str(data["name"])
        problem_id = int(data["problem_id"])
        problem = Problem.objects.filter(id=problem_id).first()
        bookmark = Bookmark.objects.filter(problem__problem_set=problem.problem_set, name=name).first()
        if bookmark:
            bookmark.problem = problem
        else:
            bookmark = Bookmark(problem=problem, name=name)
        bookmark.save()
        return HttpResponse(f"Bookmark {name} created.", content_type="text/plain")
    except:
        return HttpResponse(content="Creation of bookmark failed.", content_type="text/plain")


def from_subtitles(request):
    original = request.FILES["original"]
    name, extension = re.search(r"^(.*)\.([^.]+)$", original.name).groups()
    translation = request.FILES.get("translation")
    audio = request.FILES.get("audio")
    if extension == "srt":
        Importer.from_subtitles(get_lines(original), get_lines(translation), name, audio)
    if extension == "vtt":
        Importer.from_subtitles(get_lines(srt_from_vtt(original).splitlines()), get_lines(translation), name, audio)
    return HttpResponseRedirect(reverse("successImport"))


@transaction.atomic()
def training(request, set_id, repeat):
    setting = Setting.objects.first()
    current_problem_set = ProblemSet.objects.filter(id=set_id).first()
    training_queue = None
    fake_problem_number = int(request.POST["problemNumber"]) + (0 if repeat == 1 else 1)
    training_queue_id = request.POST.get("trainingQueueId")
    if training_queue_id is not None:
        training_queue = TrainingQueue.objects.filter(id=training_queue_id).first()
        if training_queue is not None:
            training_queue_item = TrainingQueueItem.objects.filter(
                queue=training_queue, item_number=training_queue.current_item_number
            ).first()
            if training_queue_item is None:
                training_queue.active = False
                training_queue.save()
                context = {"message": "Training complete. Well done!"}  # TODO: display summary
                return render(request, "trainer/message.html", context)
            else:
                problem = training_queue_item.problem
                fake_problem_number = training_queue.current_item_number
        else:
            return render(request, "trainer/message.html", {"message": "No training queue found."})
    else:
        real_problem_number = get_real_problem_no(set_id, fake_problem_number)
        if fake_problem_number > real_problem_number:
            fake_problem_number = 0
        problem = Problem.objects.filter(problem_set_id=set_id, problem_number=real_problem_number).first()
        current_problem_set.last_fake_problem_number = fake_problem_number
        current_problem_set.save()
    hidden_positions = None
    if setting.number_of_hidden_words >= 0:
        number_of_hidden_words = min(setting.number_of_hidden_words, len(problem.sentence.split()))
        words_in_sentence = list(range(len(problem.sentence.split())))
        if setting.number_of_hidden_words == 0:
            number_of_hidden_words = len(words_in_sentence)
        random.shuffle(words_in_sentence)
        hidden_positions = words_in_sentence[:number_of_hidden_words]
    s_problem = SolvableProblem(problem, hidden_positions, setting.length_hint)
    audio_url = problem.audio_file
    stat_record = StatRecord(
        score=str(round(problem.score, 3)),
        last_played_date=standard_date(problem.last_played) if problem.last_played is not None else "never",
        played=problem.played,
        success=problem.success_number,
        record_stats="Recording stats" if setting.record_stats else "",
    )
    context = {
        "set": current_problem_set,
        "problem": None if problem is None else s_problem,
        "problem_number": fake_problem_number,
        "audio_url": audio_url,
        "training_queue": training_queue,
        "stats": stat_record,
    }
    return render(request, "trainer/problemTraining.html", context)


@transaction.atomic()
def evaluate(request, set_id, problem_number):  # TODO: Refactor this shit
    if request.method == "POST":
        training_queue_id = request.POST.get("trainingQueueId")
        if training_queue_id is not None:
            real_problem_number = request.POST["problem_number"]
            training_queue = TrainingQueue.objects.filter(id=training_queue_id).first()
            training_queue.current_item_number += 1
            training_queue.save()
        else:
            training_queue_id = False
            real_problem_number = get_real_problem_no(set_id, problem_number)
        setting = Setting.objects.first()
        translation_hidden = setting.hide_translation
        problem_set = ProblemSet.objects.filter(id=set_id).first()
        bookmarks = Bookmark.objects.filter(problem__problem_set=problem_set).all()
        for bookmark in bookmarks:
            bookmark.fake_number = get_fake_problem_no(set_id, bookmark.problem.problem_number)
        problem_set.bookmarks = bookmarks
        orig_problem = Problem.objects.filter(problem_set_id=set_id, problem_number=real_problem_number).first()
        orig_words = [
            processed_string(w, default_word_processors())
            for w in (
                orig_problem.sentence.split() if setting.case_sensitive else orig_problem.sentence.lower().split()
            )
        ]
        orig_submitted_answer = request.POST["solution"]
        orig_score = orig_problem.score
        partial_solution = request.POST.get("partial_solution")
        submitted_answer = orig_submitted_answer if orig_submitted_answer is not None else ""
        missing_positions = None
        if partial_solution is not None:
            missing_positions = [i for i, word in enumerate(partial_solution.split()) if re.match(r"#+|\$", word)]
            for missing_word in orig_submitted_answer.split():
                partial_solution = re.sub(r"#+|\$", missing_word, partial_solution, 1)
            submitted_answer = partial_solution
        submitted_answer = processed_string(
            (submitted_answer if setting.case_sensitive else submitted_answer.lower()), default_solution_processors()
        )
        sub_answer_words = submitted_answer.split()
        for i in range(len(orig_words) - len(sub_answer_words)):
            sub_answer_words.append(" ")
        solution = []
        is_solution = True
        for i, sub_answer_word in enumerate(sub_answer_words):
            if i < len(orig_words):
                word = None
                if setting.record_stats:
                    if missing_positions is None or i in missing_positions:
                        word = Word.objects.filter(id=orig_words[i]).first()
                        if word is not None:
                            word.played = word.played + 1
                            print(f"Word {word.id} played {word.played} times")
                if orig_words[i] != sub_answer_word:  # Word was wrongly guessed
                    solution.append(ProblemSolution(i, sub_answer_word, orig_words[i]))
                    if setting.record_stats and isinstance(word, Word):
                        if missing_positions is None or i in missing_positions:
                            word.wrong += 1
                            print(f"Word {word.id} guessed wrong {word.wrong} times")
                if setting.record_stats and isinstance(word, Word):
                    word.save()
            else:
                solution.append(ProblemSolution(i, sub_answer_words[i], " "))
        if setting.record_stats:
            orig_problem.last_played = timezone.now()
            orig_problem.played += 1
            if len(solution) == 0:
                orig_problem.success_number += 1
            orig_problem = update_problem_score(orig_problem)
        orig_problem.save()
        audio_url = orig_problem.audio_file if orig_problem.audio_file is not None else None
        stat_record = StatRecord(
            score=f"{round(orig_score, 3)} -> {round(orig_problem.score, 3)}",
            last_played_date=standard_date(orig_problem.last_played)
            if orig_problem.last_played is not None
            else "never",
            played=orig_problem.played,
            success=orig_problem.success_number,
            record_stats="Recording stats" if setting.record_stats else "",
        )
        context = {
            "set": problem_set,
            "is_solution": is_solution,
            "problem": orig_problem,
            "orig_sentence_words": orig_words,
            "sub_answer": sub_answer_words,
            "solution": solution,
            "problem_number": problem_number,
            "mistake_num": len(solution),
            "audio_url": audio_url,
            "training_queue_id": training_queue_id,
            "translation_hidden": translation_hidden,
            "stats": stat_record,
        }
        return render(request, "trainer/problemTraining.html", context)
