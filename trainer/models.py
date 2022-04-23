from django.db import models


class ProblemSet(models.Model):
    name = models.CharField(max_length=200, unique=True)
    create_date = models.DateTimeField('date created')
    last_fake_problem_number = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Problem(models.Model):
    active = models.BooleanField(default=True)
    problem_set = models.ForeignKey(ProblemSet, on_delete=models.CASCADE)
    problem_number = models.IntegerField(default=0)
    sentence = models.CharField(max_length=1000)
    translation = models.CharField(max_length=1000, null=True, blank=True)
    create_date = models.DateTimeField('date created')
    last_played = models.DateTimeField('last played', null=True, blank=True)
    played = models.IntegerField(default=0)
    success_number = models.IntegerField(default=0)
    score = models.FloatField(default=0)
    audio_file = models.CharField(max_length=300, null=True, default=None, blank=True)

    def __str__(self):
        return self.sentence


class Bookmark(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Word(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    played = models.IntegerField(default=0)
    wrong = models.IntegerField(default=0)

    def __str__(self):
        return self.id


class Setting(models.Model):
    case_sensitive = models.BooleanField(default=True)
    learning_mode = models.BooleanField(default=True)
    record_stats = models.BooleanField(default=False)
    ignore_spacing = models.BooleanField(default=False)
    exact_match = models.BooleanField(default=False)
    import_ignore_in_brackets = models.BooleanField(default=True)
    import_audio_time_added_before = models.FloatField(default=0.0)
    import_audio_time_added_after = models.FloatField(default=0.0)
    number_of_hidden_words = models.IntegerField(default=-1)
    length_hint = models.BooleanField(default=False)
    hide_translation = models.BooleanField(default=False)


class TrainingQueue(models.Model):
    active = models.BooleanField(default=True, help_text="Whether this queue is in progress or finished.")
    date_created = models.DateTimeField(auto_now=True)
    current_item_number = models.IntegerField(default=0)
    problem_set = models.ForeignKey(ProblemSet, on_delete=models.CASCADE)


class TrainingQueueItem(models.Model):
    item_number = models.IntegerField(default=0)
    queue = models.ForeignKey(TrainingQueue, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
