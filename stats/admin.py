from django.contrib import admin
from stats.models import Fixture, Person, Player, Season


# Register your models here.
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    pass


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


class PlayerInLine(admin.TabularInline):
    model = Player


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInLine,
    ]
