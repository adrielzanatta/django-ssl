from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import (
    Case,
    Value,
    When,
    F,
    Sum,
    Q,
    Func,
    Count,
    Avg,
    ExpressionWrapper,
    FloatField,
    OuterRef,
    Subquery,
    Prefetch,
    IntegerField,
)
from django.db.models.functions import Cast
from .models import Player, Season, Fixture
from .forms import FixtureForm, PlayerFormset, PlayerFormsetDetail

# Create your views here.


def ranking(request):
    seasons = Season.objects.all()
    context = {"seasons": seasons}
    return render(request, "content.html", context)


def ranking_table(request):
    season = request.GET.get("filter_season")
    if season == "all_seasons":
        fixt_list = Fixture.objects.all()
    else:
        fixt_list = Fixture.objects.filter(season__pk=season)

    rankings = (
        Player.objects.filter(fixture__in=fixt_list)
        .annotate(
            points=Case(
                When(
                    team_played=F("fixture__winner_team"),
                    then=Value(3),
                ),
                When(
                    fixture__winner_team=0,
                    then=Value(1),
                ),
                default=Value(0),
            ),
        )
        .values("person__nickname")
        .annotate(
            Sum("points"),
            Sum("goals"),
            Count("fixture"),
            Avg("goals"),
            is_mvp__count=Count("is_mvp", filter=Q(is_mvp=True)),
            wins=Count("fixture", filter=Q(points=3)),
            ties=Count("fixture", filter=Q(points=1)),
            losses=Count("fixture", filter=Q(points=0)),
            pct_points=ExpressionWrapper(
                (
                    100
                    * Cast(F("points__sum"), output_field=FloatField())
                    / (Cast(F("fixture__count"), output_field=FloatField()) * 3)
                ),
                output_field=FloatField(),
            ),
        )
        .order_by("-points__sum", "-goals__sum")
    )

    attendance = request.GET.get("filter_attendance")

    if attendance:
        if season == "all_seasons":
            count_fixtures = Fixture.objects.all()
        else:
            count_fixtures = Fixture.objects.filter(season__pk=season)

        count_fixtures = count_fixtures.aggregate(Count("id"))["id__count"]

        rankings = rankings.filter(fixture__count__gte=(count_fixtures // 2))

    context = {"players": rankings}

    return render(request, "partials/ranking_table.html", context)


def fixtures(request):
    seasons = Season.objects.all()
    context = {"seasons": seasons}
    return render(request, "content.html", context)


def fixtures_list(request):
    season = request.GET.get("filter_season")
    if season == "all_seasons":
        fixtures = Fixture.objects.all()
    else:
        fixtures = Fixture.objects.filter(season__pk=season)

    fixtures = fixtures.order_by("-date", "-number")

    context = {"fixtures": fixtures}
    return render(request, "partials/fixtures_list.html", context)


def get_winner(team1, team2):
    diff = team1 - team2
    if diff > 0:
        return 1
    elif diff < 0:
        return 2
    else:
        return 0


def fixture_details(request, pk):

    if request.method == "POST":

        if "delete" in request.POST:
            fixture = get_object_or_404(Fixture, id=pk)
            fixture.delete()
            return redirect("fixtures")

        elif "save" in request.POST:

            fixt = get_object_or_404(Fixture, id=pk)
            form = FixtureForm(request.POST, instance=fixt)
            formset = PlayerFormsetDetail(request.POST, instance=fixt)

            if form.is_valid():
                fixture = form.save(commit=False)

                team_1_goals, team_2_goals = 0, 0

                if formset.is_valid():
                    formset.save()

                    for f in formset:
                        team_played = f.cleaned_data.get("team_played")
                        goals = f.cleaned_data.get("goals")

                        if team_played == 1:
                            team_1_goals += goals
                        elif team_played == 2:
                            team_2_goals += goals

                    fixture.team_1_goals = team_1_goals
                    fixture.team_2_goals = team_2_goals
                    fixture.diff = abs(team_1_goals - team_2_goals)
                    fixture.winner_team = get_winner(team_1_goals, team_2_goals)
                    fixture.save()

                else:

                    formset = PlayerFormsetDetail(instance=fixt)

            else:
                fixt_form = FixtureForm(instance=fixt)

            return redirect("fixtures")

    else:
        fixt = get_object_or_404(Fixture, id=pk)
        fixture_form = FixtureForm(instance=fixt)
        player_formset = PlayerFormsetDetail(instance=fixt)

        context = {
            "fixture_form": fixture_form,
            "player_formset": player_formset,
            "fixture": fixt,
        }

        return render(request, "fixture_details.html", context)


def fixture_add(request):

    if request.method == "POST":

        if "save" in request.POST:
            form = FixtureForm(request.POST)
            formset = PlayerFormset(request.POST, instance=fixture)

            if form.is_valid():
                fixture = form.save(commit=False)

                team_1_goals, team_2_goals = 0, 0

                if formset.is_valid():
                    formset.save()

                    for f in formset:
                        team_played = f.cleaned_data.get("team_played")
                        goals = f.cleaned_data.get("goals")

                        if team_played == 1:
                            team_1_goals += goals
                        elif team_played == 2:
                            team_2_goals += goals

                    fixture.team_1_goals = team_1_goals
                    fixture.team_2_goals = team_2_goals
                    fixture.diff = abs(team_1_goals - team_2_goals)
                    fixture.winner_team = get_winner(team_1_goals, team_2_goals)
                    fixture.save()

                else:
                    formset = PlayerFormset(instance=fixture)

                return redirect("fixtures")

            else:
                form = FixtureForm()
    else:
        formset = PlayerFormset()
        form = FixtureForm()

        context = {
            "fixture_form": form,
            "player_formset": formset,
        }

    return render(request, "fixture_details.html", context)
