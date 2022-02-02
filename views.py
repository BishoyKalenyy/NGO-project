from asyncio import tasks
from cProfile import Profile
import json
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


#from base.decoreters import Donor_required, NGO_required
from .models import NGO,Task
from django.contrib.auth.models import User
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from django.db import connection
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)



        
        
    
    

 
        


def recommended_jobs(cuser):
    jobs_recommended = list()
    users_skill_obj_list = UsersSkill.objects.filter(user=cuser)
    skills_list = set([obj.skill for obj in users_skill_obj_list])
    jobs = Task()
    if jobs:
        for job in jobs:
            taskskreq_obj_list = TaskSkillsRequired.objects.filter(task=job)
            job_req_skills = set([obj.skill for obj in taskskreq_obj_list])
            common_job_skill = skills_list.intersection(job_req_skills)
            if len(common_job_skill) > 0:
                jobs_recommended.append(job)
    return jobs_recommended


def home2(request):
    return render(request,'home.html')



def home(request):
    if not request.user.is_superuser and request.user.is_authenticated:
        context = dict()
        cuser = profile.objects.get(user=request.user)
        jobs_recommended = recommended_jobs(cuser)
        posted_projects = Task.objects.filter(
            leader=cuser).order_by('-postedOn')
        if len(posted_projects) == 0:
            context['current_posted_project'] = None
            context['current_added_task'] = None
            context['percentCompleted'] = None
        else:
            current_posted_project = posted_projects[0]
            context['current_posted_project'] = current_posted_project
            total_tasks = float(
                len(Task.objects.filter(project=current_posted_project)))
            completed_tasks = float(len(Task.objects.filter(
                project=current_posted_project, isCompleted=True)))
            if total_tasks == 0 or completed_tasks == 0:
                percentCompleted = 0
            else:
                percentCompleted = int((completed_tasks / total_tasks) * 100)
                if percentCompleted != 100:
                    percentCompleted = int(round(percentCompleted / 10)) * 10
            current_posted_project_tasks = Task.objects.filter(
                project=current_posted_project).order_by('-addedOn')
            if len(current_posted_project_tasks) == 0:
                context['current_added_task'] = None
            else:
                current_added_task = current_posted_project_tasks[0]
                context['current_added_task'] = current_added_task
            context['percentCompleted'] = percentCompleted
        task_obj_list = profile.objects.filter(user=cuser)
        if len(task_obj_list) == 0:
            context['current_working_task'] = None
        else:
            working_task_list = [obj.task for obj in task_obj_list if obj.task.isCompleted is False]
            if working_task_list:
                current_working_task = sorted(working_task_list, key=lambda x: x.addedOn, reverse=True)[0]
                context['current_working_task'] = current_working_task
        context['jobs_recommended'] = jobs_recommended
        return render(request, 'dashboard.html', context)
    elif request.user.is_superuser:
        return HttpResponseRedirect(reverse('Portal:admin'))
    else:
        return HttpResponseRedirect(reverse('Portal:index'))



def browse_jobs(request):
    # context = dict()
    # cuser = None
    # if request.user.is_authenticated:
    #     cuser = NGO.objects.get(user=request.user)
    # context['jobs'] = Task()
    # skill_list = Skill.objects.all()
    # context['skill_list'] = skill_list
    # if(request.method=='GET'):
    #     context['skill_check']=request.GET.get('skill',None)
        
    return render(request, 'browse_jobs.html')


def loginUser(request):
    page = 'login'

    #if request.user.is_authenticated:
        #return redirect('profiles')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'home2')

        else:
            messages.error(request, 'Username OR password is incorrect')

    return render(request, 'login.html')


def logoutUser(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')



def registerUser(request):
     form = NGOSignUpForm

     if request.method == 'POST':
        form = NGOSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'An error occurred during registration')


     return render(request, 'NGO_signup.html', {'form': form})
    
@login_required
def dashboard(request):

    return render(request,'dashboard.html')


#
#@method_decorator([login_required, NGO_required], name='dispatch')
@login_required
def editAccountForNGO(request):
    ngo = request.user.ngo  
    form = NGOform(instance=ngo)

    if request.method == 'POST':
        form = NGOform(request.POST, request.FILES, instance=ngo)
        if form.is_valid():
            form.save()

            #return redirect('add_skill')

    context = {'form': form}
    return render(request, 'edit.html', context)








@login_required
def createSkill(request):
    ngo = request.user.ngo
    form = SkillForm()

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.save()
            skill.Need.add(ngo)

            #skill.save()
            messages.success(request, 'Skill was added successfully!')
            #return redirect('account')

    context = {'form': form}
    return render(request, 'skill_form.html', context)


@login_required
def updateSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill was updated successfully!')
            return redirect('account')

    context = {'form': form}
    return render(request, 'skill_form.html', context)


@login_required
def deleteSkill(request, pk):
    ngo = request.user.ngo
    skill = ngo.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill was deleted successfully!')
        return redirect('account')

    context = {'object': skill}
    return render(request, 'delete_template.html', context)


#@method_decorator([login_required, Donor_required], name='dispatch')
#@login_required(login_url='login')
def editAccountForDonor(request):
    profile = request.user.profile
    form = Donor(instance=profile)

    if request.method == 'POST':
        form = Donor(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            #return redirect('account')

    context = {'form': form}
    return render(request, 'users/profile_form.html', context)

@login_required
def post_project(request):

    ngo = request.user.ngo
    form = taskofrm()

    if request.method == 'POST':
        form = taskofrm(request.POST)
        if form.is_valid():
            Task = form.save(commit=False)
            Task.save()
            Task.PostedBy.add(ngo)

            #skill.save()
            messages.success(request, 'Skill was added successfully!')
            #return redirect('account')

    context = {'form': form}
    return render(request, 'post_project.html', context)


def taskdesc(request,task_id):

     task = Task.objects.get(id=task_id)

     return render(request,'task_description.html')


def apply_for_task(request, task):
    applicant = Applicant()
    applicant.task = Task.objects.get(id=task.id)
    applicant.user = User.objects.get(user=request.user.id)
    applicant.save()


def submit_task(request, task):
        #need to recheck
    submit_file = request.POST.get("file",None)
    if(submit_file!=None):
        if (not task.isCompleted):
            task.file = submit_file
            task.save()

def send_simple_message(reciever,subject,text):
    print(">>",reciever)
    print(">>",subject)
    print(">>",text)
    fromaddr = "admin@gmail.com"
    toaddr = reciever
    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    body = text
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "freelancingportal")
    text = msg.as_string()
    x=server.sendmail(fromaddr, toaddr, text)
    print(x,"sent mail")
    server.quit()
    
def select_user(request, task, context):
    user_id = request.POST["user_id"]
    is_applicant = False
    print(user_id)
    for i in context['applicants']:
        if i.user.user.id == int(user_id):
            is_applicant = True
    if is_applicant:
        if task.contributor_set.count() == 0:
            contributor = Applicant()
            contributor.user = profile.objects.get(user=int(user_id))
            contributor.task = Task.objects.get(id=task.id)
            contributor.save()
            send_simple_message(str(contributor.user.user.email),"Selection for the Task"+str(),"You have been selected for the task "+str(contributor.task.task_name)+" of project "+str(contributor.task.project.project_name)+"\n\n -"+str(contributor.task.project.leader.user.username)) 
            for i in context['applicants']:
                if i.user!=contributor.user:
                    send_simple_message(str(i.user.user.email),"Non-Selection for the Task"+str(),"You have not been selected for the task "+str(contributor.task.task_name)+" of project "+str(contributor.task.project.project_name)+"\n\n -"+str(contributor.task.project.leader.user.username))
        else:
            print("we already have a contributor")
    else:
        print("Not an applicant")


def applicants(request, task_id):
    task = Task.objects.get(id=task_id)
    if (not request.user.is_authenticated or (request.user != task.project.leader.user)):
        return redirect("Portal:task_description", task.project.id, task_id)
    context = dict()
    context['task'] = task
    context['is_leader'] = (task.project.leader.user == request.user)
    context['applicants'] = task.applicant_set.all().order_by("-time_of_application")
    context['has_contributor'] = (task.contributor_set.count() > 0)
    if (context['has_contributor']):
        context['contributor'] = task.contributor_set.get()
    if request.method == 'POST':
        if request.user.is_authenticated and request.POST[
                "work"] == "select" and request.user == task.project.leader.user:
            select_user(request, task, context)
        return redirect("Portal:applicants", task_id)
    return render(request, "applicants.html", context)

def user_profile(request, username):
    context = dict()
    user = User.objects.get(username=username)
    cuser = profile.objects.get(user=user)
    context['cuser'] = cuser
    if request.user.is_authenticated:
        if request.method == "POST":
            bio = request.POST['bio']
            cuser.bio = bio
            if request.FILES.get('image', None) is not None:
                image = request.FILES['image']
                cuser.image = image
            cuser.save()
            skills = request.POST.getlist('skills[]')
            UsersSkill.objects.filter(user=cuser).all().delete()
            
            for skill in skills:
                skillreq = Skill.objects.get(skill_name=skill)
                uskill = UsersSkill(skill=skillreq, user=cuser,
                                    level_of_proficiency=int(request.POST[skill]))
                uskill.save()
            
            return HttpResponseRedirect(reverse('Portal:profile', args=(username,)))
    skills = UsersSkill.objects.filter(user=cuser)
    context['uskills'] = [obj.skill.skill_name for obj in skills]
    
    skill_list = Skill.objects.all()
    
    context['skill_list'] = skill_list
    context['erating'], context['frating'] = give_rating(cuser)
    return render(request, 'profile.html', context)


def give_rating(cuser):
    etasks = cuser.rating_by.all()
    ftasks = cuser.rating_to.all()
    elist = [task.e_rating for task in etasks]
    flist = [task.f_rating for task in ftasks]
    erating = None 
    frating = None
    if len(elist)>0:
        erating = int(round(sum(elist)/len(elist)))
        erating = [[1] * erating, [1] * (5 - erating)]
    if len(flist)>0:
        frating = int(round(sum(flist)/len(flist)))
        frating = [[1] * frating, [1] * (5 - frating)]
    return erating, frating

def myprojects(request):
    if request.user.is_authenticated:
        context={}
        cuser=profile.objects.get(user=request.user)
        posted_tasks = [j for i in cuser.project_set.all() for j in i.task_set.all()]
        contributor_tasks=[i.task for i in cuser.contributor_set.all()]
        context['current_projects']=[i for i in cuser.project_set.all() if i.task_set.count()==0]
        context['completed']=[i for i in posted_tasks if i.isCompleted==True]+[i for i in contributor_tasks if i.isCompleted==True]
        context['active']=[i for i in posted_tasks if i.isCompleted==False]+[i for i in contributor_tasks if i.isCompleted==False]
        return render(request, 'myprojects.html',context)
    return render(request, 'login.html')
    
