from django.contrib import admin
from stats.models import Fixture, Person, Player, Season
from django.db.models import Sum


# Register your models here.
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    pass


class PlayerInLine(admin.TabularInline):
    model = Player


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInLine,
    ]

    def save_related(self, request, form, formsets, change):
        super(FixtureAdmin, self).save_related(request, form, formsets, change)
        # form.instance stores the saved object
        form.instance.winner_team = get_winner(form)
        form.instance.save()


def get_winner(form):
    goals_team_1 = Player.objects.filter(
        fixture__id=form.instance.id, team_played=1
    ).aggregate(Sum("goals"))
    goals_team_2 = Player.objects.filter(
        fixture__id=form.instance.id, team_played=2
    ).aggregate(Sum("goals"))

    diff_goals = goals_team_1["goals__sum"] - goals_team_2["goals__sum"]

    if diff_goals > 0:
        return 1
    elif diff_goals < 0:
        return 2
    else:
        return 0
