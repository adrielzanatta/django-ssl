from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import (
    Case,
    Value,
    When,
    F,
    Sum,
    Q,
    Count,
    Avg,
    ExpressionWrapper,
    FloatField,
    Window,
    CharField,
)
from django.db.models.functions import Cast, Concat
from stats.forms import FixtureForm, PlayerFormset, PlayerFormsetDetail
from .models import Player, Season, Fixture
from .utils import get_line_chart_cumpoints
import plotly.express as px
import math


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
                When(team_played=F("fixture__winner_team"), then=Value(3)),
                When(fixture__winner_team=0, then=Value(1)),
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

        rankings = rankings.filter(fixture__count__gte=math.ceil(count_fixtures / 2))

    context = {"players": rankings}

    return render(request, "partials/ranking_table.html", context)


def graph(request):
    seasons = Season.objects.all()
    context = {"seasons": seasons}
    return render(request, "content.html", context)


def graph_positions(request):
    season = request.GET.get("filter_season")
    if season == "all_seasons":
        fixt_list = Fixture.objects.all()
    else:
        fixt_list = Fixture.objects.filter(season__pk=season)

    qs_cumpoints = (
        Player.objects.filter(fixture__in=fixt_list)
        .annotate(
            points=Case(
                When(team_played=F("fixture__winner_team"), then=Value(3)),
                When(fixture__winner_team=0, then=Value(1)),
                default=Value(0),
            ),
        )
        .order_by("fixture__number")
        .annotate(
            cum_points=Window(
                expression=Sum("points"),
                partition_by=F("person__nickname"),
                order_by=F("fixture__number").asc(),
            )
        )
        .values("person__nickname", "cum_points", "fixture__number")
        .order_by("fixture__number", "-cum_points")
    )

    fig_cumpoints = px.line(
        x=[e["fixture__number"] for e in qs_cumpoints],
        y=[e["cum_points"] for e in qs_cumpoints],
        color=[e["person__nickname"] for e in qs_cumpoints],
        template="plotly_dark",
        title="Pontos corridos",
        labels={"x": "Rodadas", "y": "Pontos Acumulados"},
        width=800,
        height=800,
    )

    fig_cumpoints.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )

    chart_cumpoints = fig_cumpoints.to_html()

    qs_goals = (
        Player.objects.filter(fixture__in=fixt_list)
        .annotate(
            cum_goals=Window(
                expression=Sum("goals"),
                partition_by=F("person__nickname"),
                order_by=F("fixture__number").asc(),
            ),
            text=Concat(
                "cum_goals", Value("-"), "person__nickname", output_field=CharField()
            ),
        )
        .values("person__nickname", "cum_goals", "fixture__number", "text")
        .order_by("-fixture__number", "-cum_goals")
    )

    fig_goals = px.line(
        x=[e["fixture__number"] for e in qs_goals],
        y=[e["cum_goals"] for e in qs_goals],
        color=[e["person__nickname"] for e in qs_goals],
        template="plotly_dark",
        title="Gols acumulados",
        labels={"x": "Rodadas", "y": "Gols Acumulados"},
        width=800,
        height=800,
    )

    fig_goals.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
        },
        showlegend=False,
    )

    for i, d in enumerate(fig_goals.data):
        fig_goals.add_scatter(
            x=[d.x[0]],
            y=[d.y[0]],
            mode="markers+text",
            text=str(d.y[0]) + "-" + d.name,
            textfont=dict(color=d.line.color, size=11),
            textposition="middle right",
            marker=dict(color=d.line.color, size=8),
            legendgroup=d.name,
            showlegend=False,
        )

    chart_cumgoals = fig_goals.to_html()

    context = {"chart_cumpoints": chart_cumpoints, "chart_cumgoals": chart_cumgoals}

    return render(request, "partials/ranking_graph.html", context)


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


def fixture_details(request, pk):

    if request.method == "POST":

        if "delete" in request.POST:
            fixture = get_object_or_404(Fixture, id=pk)
            fixture.delete()
            return redirect("fixtures")

        if "save" in request.POST:
            fixt = get_object_or_404(Fixture, id=pk)
            form = FixtureForm(request.POST, instance=fixt)
            formset = PlayerFormsetDetail(request.POST, instance=fixt)
            if form.is_valid():
                fixture = form.save(commit=False)
                if formset.is_valid():
                    formset.save()
                    fixture.save()
                else:
                    formset = PlayerFormsetDetail(instance=fixt)
            else:
                form = FixtureForm(instance=fixt)
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
            if form.is_valid():
                fixture = form.save()
                formset = PlayerFormset(request.POST, instance=fixture)
                if formset.is_valid():
                    formset.save()
                    fixture.save()

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
