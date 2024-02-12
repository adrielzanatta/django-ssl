from django.shortcuts import render, get_object_or_404, redirect
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
    Func,
)
from django.db.models.functions import Cast
from .models import Player, Season, Fixture
from .forms import FixtureForm, PlayerFormset, PlayerFormsetDetail

# Create your views here.


def seasons(request):
    seasons = Season.objects.all()
    context = {"seasons": seasons}
    return render(request, "rankings.html", context)


def ranking_table(request):

    # season = request.GET.get("season")

    # if season == "all_seasons":
    #     player_list = Player.objects.all()
    #     fixt_list = Fixture.objects.all()
    # else:
    #     player_list = Player.objects.filter(fixture__season__pk=season)
    #     fixt_list = Fixture.objects.filter(season__pk=season)

    # fixtures = fixt_list.annotate(
    #     team_1=Sum("players__goals", filter=Q(players__team_played=1)),
    #     team_2=Sum("players__goals", filter=Q(players__team_played=2)),
    #     diff_real=(F("team_1") - F("team_2")),
    #     winner_team=Case(
    #         When(Q(diff_real__gt=0), then=Value(1)),
    #         When(Q(diff_real__lt=0), then=Value(2)),
    #         When(Q(diff_real=0), then=Value(0)),
    #     ),
    # )

    # fixt_points = player_list.annotate(
    #     points=Case(
    #         When(
    #             team_played=F("fixtures__winner_team"),
    #             then=Value(3),
    #         ),
    #         When(
    #             fixture__winner_team=0,
    #             then=Value(1),
    #         ),
    #         default=Value(0),
    #     )
    # )

    # rankings = (
    #     fixt_points.values("person__nickname")
    #     .annotate(
    #         Sum("points"),
    #         Sum("goals"),
    #         Count("fixture"),
    #         Avg("goals"),
    #         is_mvp__count=Count("is_mvp", filter=Q(is_mvp=True)),
    #         wins=Count("fixture", filter=Q(points=3)),
    #         ties=Count("fixture", filter=Q(points=1)),
    #         losses=Count("fixture", filter=Q(points=0)),
    #         pct_points=ExpressionWrapper(
    #             (
    #                 100
    #                 * Cast(F("points__sum"), output_field=FloatField())
    #                 / (Cast(F("fixture__count"), output_field=FloatField()) * 3)
    #             ),
    #             output_field=FloatField(),
    #         ),
    #     )
    #     .order_by("-points__sum", "-goals__sum")
    # )

    # attendance = request.GET.get("attendance")

    # if attendance:
    #     if season == "all_seasons":
    #         count_fixtures = Fixture.objects.all()
    #     else:
    #         count_fixtures = Fixture.objects.filter(season__pk=season)

    #     count_fixtures = count_fixtures.aggregate(Count("id"))["id__count"]

    #     rankings = rankings.filter(fixture__count__gte=(count_fixtures // 2))

    # context = {"players": rankings}

    context = {}
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
        diff_real=(F("team_1") - F("team_2")),
        winner_team=Case(
            When(Q(diff_real__gt=0), then=Value(1)),
            When(Q(diff_real__lt=0), then=Value(2)),
            When(Q(diff_real=0), then=Value(0)),
        ),
        diff=Func((F("team_1") - F("team_2")), function="ABS"),
    ).order_by("-date", "-number")

    context = {"fixtures": fixtures}
    return render(request, "partials/fixtures_list.html", context)


def fixture_details(request, pk):

    if request.method == "POST":

        if "delete" in request.POST:
            fixture = get_object_or_404(Fixture, id=pk)
            fixture.delete()
            return redirect("fixtures")

        elif "save" in request.POST:
            fixture = get_object_or_404(Fixture, id=pk)
            form = FixtureForm(request.POST, instance=fixture)

            if form.is_valid():
                instance = form.save()
                formset = PlayerFormsetDetail(request.POST, instance=instance)

                for form in formset:

                    if form.is_valid():
                        form.save()
                    else:
                        formset = PlayerFormsetDetail(instance=instance)

                return redirect("fixtures")

            else:
                form = FixtureForm(instance=fixture)
    else:
        fixture = get_object_or_404(Fixture, id=pk)
        fixture_form = FixtureForm(instance=fixture)
        player_formset = PlayerFormsetDetail(instance=fixture)

        context = {
            "fixture_form": fixture_form,
            "player_formset": player_formset,
            "fixture": fixture,
        }

        return render(request, "fixture_details.html", context)


def fixture_add(request):

    if request.method == "POST":

        if "save" in request.POST:
            form = FixtureForm(request.POST)
            if form.is_valid():
                instance = form.save()
                formset = PlayerFormset(request.POST, instance=instance)
                if formset.is_valid():
                    formset.save()
                else:
                    formset = PlayerFormset(instance=instance)

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

    return render(request, "fixture_add.html", context)
