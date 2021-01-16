from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset,Row, \
    Column, ButtonHolder, Submit,Button
from django.forms.models import inlineformset_factory
from election.models import Candidate, ElectionConfig, Position, Elector
import datetime

class VoteForm(forms.Form):

    position = forms.HiddenInput()
    candidate = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=Candidate.objects.none(), label='')

    def __init__(self, *args, position, **kwargs):
        self.fields["candidate"].queryset = Candidate.objects.filter(position=position)
        super().__init__(*args, **kwargs)


class ElectionConfigForm(forms.ModelForm):
    class Meta:
        model = ElectionConfig
        #fields = '__all__'
        exclude = ('locked',)

    def __init__(self, *args, **kwargs):
        self.readonly = False
        if 'readonly' in kwargs:
            self.readonly = kwargs.pop('readonly')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('description', css_class='form-group col-md-4 mb-0'),
                Column('start_time', css_class='form-group col-md-4 mb-0'),
                Column('end_time', css_class='form-group col-md-4 mb-0'),
                Column('block_time_generation', css_class='form-group col-md-4 mb-0'),
                Column('guess_rate', css_class='form-group col-md-4 mb-0'),
                Column('min_votes_in_block', css_class='form-group col-md-4 mb-0'),
                Column('min_votes_in_last_block', css_class='form-group col-md-4 mb-0'),
                Column('attendance_rate', css_class='form-group col-md-4 mb-0'),
                #Column('locked', css_class='form-group col-md-4 mb-0'),
                #css_class='form-row'
            ),
        )
       
        #Disable all the fields when election is occurring
        if self.readonly:
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
                field.disabled = True
    '''
    def clean_start_time(self):
        start_time = self.cleaned_data['start_time']
        if start_time < datetime.datetime.now():
            raise forms.ValidationError("Start time cannot be in past.")
        return start_time
    
    def clean_end_time(self):
        end_time = self.cleaned_data['end_time']
        if end_time < datetime.datetime.now():
            raise forms.ValidationError("End time cannot be in past.")
        return end_time
    '''

    
    def clean(self):
        super().clean()
        start_time = self.cleaned_data.get("start_time")
        end_time = self.cleaned_data.get("end_time")
        if start_time and end_time:
            if end_time.isoformat() < start_time.isoformat():
                msg = "Start time is greater than End time."
                raise forms.ValidationError(msg)
    


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        self.readonly = False
        if 'readonly' in kwargs:
            self.readonly = kwargs.pop('readonly')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_method = 'post'

        #Disable all the fields when election is occurring
        if self.readonly:
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
                field.disabled = True

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        self.readonly = False
        if 'readonly' in kwargs:
            self.readonly = kwargs.pop('readonly')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_method = 'post'

        #Disable all the fields when election is occurring
        if self.readonly:
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
                field.disabled = True


class ElectorForm(forms.ModelForm):
    class Meta:
        model = Elector
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        self.readonly = False
        if 'readonly' in kwargs:
            self.readonly = kwargs.pop('readonly')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_method = 'post'

        #Disable all the fields when election is occurring
        if self.readonly:
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
                field.disabled = True
