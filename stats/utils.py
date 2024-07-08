import plotly.express as px
from django.db.models import QuerySet, Count, Sum, F
from math import ceil


def get_line_chart_cumpoints(qs, label, x, y):
    labels = set(item[label] for item in qs)
    labels = list(labels)
    max_rounds = max([item[x] for item in qs])
    rounds = [r for r in range(max_rounds + 1)]
    points = []

    for item in labels:
        qs_name = [d for d in qs if d[label] == item]
        points_data = [0] * (max_rounds + 1)

        for el in qs_name:
            points_data[el[x]] = el[y]

        for i, el in enumerate(points_data):
            if el == 0 and i != 0:
                points_data[i] = points_data[i - 1]

        points.append(points_data)

    zipped = list(zip(labels, points))

    context = {"rounds": rounds, "labels_points": zipped}

    return context


def cum_points_line_chart(qs):
    fig = px.line(
        x=[e.fixture.number for e in qs],
        y=[e.cum_points for e in qs],
        color=[e.person.nickname for e in qs],
        template="plotly_dark",
        title="Pontos corridos",
        labels={"x": "Rodadas", "y": "Pontos Acumulados"},
        width=800,
        height=800,
    )

    fig.update_layout(
        {
            "plot_bgcolor": "rgb(29, 35, 42)",
            "paper_bgcolor": "rgb(29, 35, 42)",
        }
    )

    return fig


def cum_goals_line_chart(qs):
    fig = px.line(
        x=[e.fixture.number for e in qs],
        y=[e.cum_goals for e in qs],
        color=[e.person.nickname for e in qs],
        template="plotly_dark",
        title="Gols marcados",
        labels={"x": "Rodadas", "y": "Gols Acumulados"},
        width=800,
        height=800,
    )

    fig.update_layout(
        {
            "plot_bgcolor": "rgb(29, 35, 42)",
            "paper_bgcolor": "rgb(29, 35, 42)",
        }
    )

    for i, d in enumerate(fig.data):
        fig.add_scatter(
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

    return fig

def player_attendance(fixtures: QuerySet, qs: QuerySet) -> list:
    fixt_count = fixtures.aggregate(Count("id"))["id__count"]
    min_attendance = ceil((0.5 * fixt_count))
    player_attendance = (
        qs.values('person')
        .annotate(Count('fixture'))
        .order_by('-fixture__count')
        .filter(fixture__count__gte=min_attendance)
    )
    players_on = [p['person'] for p in player_attendance]
    
    players_filtered = qs.filter(person__in=players_on)
    
    return players_filtered
    