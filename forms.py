from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.db import transaction

class NGOSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super(NGOSignUpForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    #def save(self, commit=True):
        #user = super().save(commit=False)
        #user.is_NGO = True
        #if commit:
            #user.save()
       # return user


class DonorSignUpForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_Donor = True
        user.save()
        don = Donor.objects.create(user=user)
        
        return user

class ProfileForm(ModelForm):
    class Meta:
        model = profile
        fields = '__all__'

class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = '__all__'
        exclude = ['owner','Need']

class taskofrm(ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        exclude=['PostedBy']

class NGOform(ModelForm):
    class  Meta:
        model=NGO
        fields='__all__'

        
        
