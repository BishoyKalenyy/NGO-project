from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


    
 

class profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)

    is_Ngo=models.BooleanField(default=False)
    is_Donor=models.BooleanField(default=False)
    email = models.EmailField(unique=True, null=True)
def __str__(self):
   return str(self.email)

class NGO(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    
    
    

def __str__(self):
   return str(self.user)

class Donor(models.Model):
    User=models.OneToOneField(User, on_delete=models.CASCADE)
def __str__(self):
   return str(self.User)    

class Task(models.Model):
    Task=models.CharField(max_length=50)
    Done=models.BooleanField(default=False)
    Description=models.CharField(max_length=500)
    PostedBy=models.ManyToManyField(NGO,null=True)
    file = models.FileField(upload_to='pdf',blank=True)



    credits = models.CharField(max_length=20, choices=(("Paid", "Paid"), ("Other", "Other")), blank=False,
                               default="Paid")
    #paid here means that you will donate doing task in exchange
def __str__(self):
   return str(self.Task)


class Skill(models.Model):
    owner = models.ManyToManyField(profile, null=True, blank=True)
    skills=models.CharField(max_length=30,blank=False,null=True)
    Need=models.ManyToManyField(NGO)
def __str__(self):
        return str(self.skills)

class UsersSkill(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    user = models.ForeignKey(profile, on_delete=models.CASCADE)
    level_of_proficiency = models.IntegerField(default=1)
    previous_work=models.FileField(upload_to='pdf')
def __str__(self):
   return str(self.skill)


class TaskSkillsRequired(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level_required = models.IntegerField(1)
def __str__(self):
   return str(self.skill)

class Applicant(models.Model):
    NGOuser = models.ManyToManyField(profile)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    time_needed=models.IntegerField(max_length=4)
    time_of_application = models.DateTimeField(auto_now_add=True, blank=True)
def __str__(self):
   return str(self.user)


    
