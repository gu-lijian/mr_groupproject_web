from django import forms

class jbpmForm(forms.Form):
    number = forms.IntegerField()
    text = forms.CharField()

    def clean_data(self):
        form_data = self.cleaned_data
        ceo_ic = self.cleaned_data['ceo_ic']
        net_income = self.cleaned_data['net_income']
        no_employee = self.cleaned_data['no_employee']
        found_year = self.cleaned_data['found_year']
        total_deposit = self.cleaned_data['total_deposit']
        if form_data['ceo_ic']:
            self._errors["ceo_ic"] = ["CEO IC is empty!"]
            del form_data['ceo_ic']
        return form_data

