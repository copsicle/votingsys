from django.core.exceptions import ValidationError
from django import forms
from datetime import date


class VoterForm(forms.Form):
    pid = forms.CharField(max_length=9, min_length=9, widget=forms.TextInput(
        attrs={'class': "form-control", 'placeholder': "ID Number"}))
    birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, date.today().year - 17),
                                                          attrs={'class': "form-control", 'type': "date"}),
                            initial=date.today().replace(date.today().year - 18))

    def clean_pid(self):
        value = self.cleaned_data['pid']
        if len(value) != 9 or not value.isdecimal():
            raise ValidationError('Not a valid id number')
        count = -1
        id_sum = 0
        for let in value:
            count += 1
            if let == 0:
                continue
            inc_num = int(let) * ((count % 2) + 1)
            id_sum += inc_num
            if inc_num > 9:
                id_sum -= 9
        if (id_sum % 10) != 0:
            raise ValidationError('Not a valid id number')
        return value

    def clean_birth(self):
        data = self.cleaned_data['birth']
        today = date.today()
        if ((today.year - data.year) - ((today.month, today.day) < (data.month, data.day))) < 18:
            raise ValidationError('You are too young to vote')
        return data
