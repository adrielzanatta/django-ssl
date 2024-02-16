from django.forms import DateInput, ModelForm
from .models import Fixture, Player
from django.forms.models import inlineformset_factory, BaseInlineFormSet


class DateInput(DateInput):
    input_type = "date"


class FixtureForm(ModelForm):
    class Meta:
        model = Fixture
        fields = ["season", "date", "drafter"]
        widgets = {
            "date": DateInput(),
        }


PlayerFormset = inlineformset_factory(
    Fixture,
    Player,
    fields="__all__",
    extra=15,
    can_delete=False,
)

PlayerFormsetDetail = inlineformset_factory(
    Fixture,
    Player,
    fields="__all__",
    extra=1,
    can_delete=True,
)
