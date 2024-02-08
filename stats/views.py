from django.shortcuts import render
from django.db.models import (
    Case,
    Value,
    When,
    F,
    Sum,
    Count,
    Q,
    Avg,
    FloatField,
    ExpressionWrapper,
)
from django.db.models.functions import Cast
from .models import Player, Season, Fixture

# Create your views here.


def seasons(request):
    seasons = Season.objects.all()
    context = {"seasons": seasons}
    return render(request, "rankings.html", context)


def ranking_table(request):

    season = request.GET.get("season")

    if season == "all_seasons":
        fixt_list = Player.objects.all()
    else:
        fixt_list = Player.objects.filter(fixture__season__pk=season)

    fixt_points = fixt_list.annotate(
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
        )
    )

    rankings = (
        fixt_points.values("person__nickname")
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

    attendance = request.GET.get("attendance")

    if attendance:
        if season == "all_seasons":
            count_fixtures = Fixture.objects.all()
        else:
            count_fixtures = Fixture.objects.filter(fixture__season__pk=season)

        count_fixtures = count_fixtures.aggregate(Count("id"))["id__count"]

        rankings = rankings.filter(fixture__count__gte=(count_fixtures // 2))

    context = {"players": rankings}

    return render(request, "partials/ranking_table.html", context)


def fixtures(request):
    seasons = Season.objects.all()
    context = {"seasons": seasons}
    return render(request, "fixtures.html", context)


def fixtures_list(request):
    season = request.GET.get("season")

    if season == "all_seasons":
        fixtures = Fixture.objects.all()
    else:
        fixtures = Fixture.objects.filter(season__pk=season)

    fixtures = fixtures.annotate(
        team_1=Sum("players__goals", filter=Q(players__team_played=1)),
        team_2=Sum("players__goals", filter=Q(players__team_played=2)),
    ).order_by("-date")

    context = {"fixtures": fixtures}

    return render(request, "partials/fixtures_list.html", context)
