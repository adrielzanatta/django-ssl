from django.db import models
from django.shortcuts import render
from django.db.models import Case, Value, When, F, Sum, Q
from .models import Player, Person

# Create your views here.


def rankings(request):
    qs = Player.objects.annotate(
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
            output_field=models.PositiveSmallIntegerField(),
        )
    )

    return render(request, "rankings.html", {"players": qs})
