class CustomInlineFormset(forms.models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.template = "bootstrap4/table_inline_formset.html"

        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def is_valid(self):
        return super(CustomInlineFormset, self).is_valid() and not any(
            [bool(e) for e in self.errors]
        )

    def clean(self):
        # get forms that actually have valid data
        count = 0
        total_size = 0
        for form in self.forms:
            try:
                if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                    count += 1
                    file = form.cleaned_data.get("file", None)
                    if file:
                        total_size += file.size
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            raise ValidationError("You must have at least one file uploaded")
        if total_size > 104857600:
            raise ValidationError(
                "You can only upload a total of 100 MB in files. Currently have {0:.2f} MB".format(
                    total_size / 1048576
                )
            )


FileInlineFormset = inlineformset_factory(
    Case, File, fields=["file"], formset=CustomInlineFormset, extra=1
)
