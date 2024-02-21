from django.db import models
from django.db.models import Sum


# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=200)
    nickname = models.CharField(max_length=200)

    def __str__(self):
        return self.nickname

    class Meta:
        ordering = ["nickname"]


class Season(models.Model):
    year = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.year)


class Fixture(models.Model):
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="fixtures"
    )
    date = models.DateField()
    number = models.PositiveSmallIntegerField(blank=True, null=True)
    drafter = models.ForeignKey(
        Person, on_delete=models.PROTECT, related_name="fixtures"
    )
    winner_team = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Season: {self.season} - Round: {self.number} - Date: {self.date}"

    def get_round(self, season: Season):
        number_of_fixtures = Fixture.objects.filter(season__year=season.year).count()
        actual_fixture = number_of_fixtures + 1
        return actual_fixture

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.number = self.get_round(self.season)
        super().save(*args, **kwargs)
        self.winner_team = self.winner
        super().save(*args, **kwargs)

    @property
    def team_1_goals(self):
        goals = self.players.filter(team_played=1).aggregate(Sum("goals"))["goals__sum"]
        return goals

    @property
    def team_2_goals(self):
        goals = self.players.filter(team_played=2).aggregate(Sum("goals"))["goals__sum"]
        return goals

    @property
    def diff(self):
        diff = abs(self.team_1_goals - self.team_2_goals)
        return diff

    @property
    def winner(self):
        if self.team_1_goals == self.team_2_goals:
            return 0
        elif self.team_1_goals > self.team_2_goals:
            return 1
        else:
            return 2


class Player(models.Model):
    teams = {"": "-", 1: 1, 2: 2}
    team_played = models.PositiveSmallIntegerField(choices=teams)
    fixture = models.ForeignKey(
        Fixture, on_delete=models.CASCADE, related_name="players"
    )
    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="played")
    goals = models.PositiveSmallIntegerField(default=0)
    mvp_votes = models.PositiveSmallIntegerField(default=0)
    is_mvp = models.BooleanField()

    def save(self, **kwargs):
        MVP_TRESHOLD = 3
        if self.mvp_votes >= MVP_TRESHOLD:
            self.is_mvp = True
        if (
            update_fields := (kwargs.get("update_fields")) is not None
            and "mvp_votes" in update_fields
        ):
            update_fields = {"is_mvp"}.union(update_fields)
        super().save(**kwargs)

    def __str__(self):
        return str(self.person.nickname)
