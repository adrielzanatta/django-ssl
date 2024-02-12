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


class BasePlayerFormset(BaseInlineFormSet):
    pass


PlayerFormset = inlineformset_factory(
    Fixture,
    Player,
    fields="__all__",
    formset=BasePlayerFormset,
    extra=15,
    can_delete=False,
)

PlayerFormsetDetail = inlineformset_factory(
    Fixture,
    Player,
    fields="__all__",
    formset=BasePlayerFormset,
    extra=1,
    can_delete=False,
)
