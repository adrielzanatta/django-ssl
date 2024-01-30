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
    DecimalField,
)
from django.db.models.functions import Cast
from .models import Player, Season

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
        fixt_points.values("person__name")
        .annotate(
            Sum("points"),
            Sum("goals"),
            Count("is_mvp"),
            Count("fixture"),
            Avg("goals"),
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

    context = {"players": rankings}

    return render(request, "partials/ranking_table.html", context)
