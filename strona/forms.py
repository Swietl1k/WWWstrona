from django import forms

class GameForm(forms.Form):
    title = forms.CharField(max_length=100, label="Title")
    number_of_choices = forms.ChoiceField(
        choices=[
            (8, '8 Choices'),
            (16, '16 Choices'),
            (32, '32 Choices')
        ],
        label="Number of choices"
    )


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()