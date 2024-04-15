import os
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from .models import Subject, UserProfile, Project, Vitals, File, FileClaim
from .forms import FileForm, UserRegistrationForm  
from monklib import get_header, convert_to_csv, Data
from plotly.subplots import make_subplots
from plotly.offline import plot

@login_required
def homePage(request):
    files = File.objects.all()
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = FileForm()
    context = {'files': files, 'form': form}
    return render(request, 'base/home.html', context)


def subject(request, pk):
    subject = Subject.objects.get(subject_id=pk)
    context = {'subject':subject}
    return render(request, 'base/subject.html', context)

def user(request, pk):
    user = UserProfile.objects.get(id=pk)
    context = {'user':user}
    return render(request, 'base/user.html', context)

def project(request, pk):
    project = Project.objects.get(id=pk)
    context = {'project':project}
    return render(request, 'base/project.html', context)

def aboutPage(request):
    return render(request, "base/about.html")

def contactPage(request):
    return render(request, "base/contact.html")


@login_required
def file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    user_profile = request.user.userprofile

    # Retrieve all subjects linked to this file
    subjects = Subject.objects.filter(file=file)

    # Find projects that include these subjects
    projects = Project.objects.filter(subjects__in=subjects)
    
     # Check if the user is part of any of these projects or has claimed the file
    user_in_project = projects.filter(users=user_profile).exists()
    user_has_claimed = FileClaim.objects.filter(file=file, user=user_profile).exists()

    if not (user_in_project or user_has_claimed):
        return HttpResponseForbidden("You do not have permission to view this file.")

    is_MFER_file = file.file.name.lower().endswith('.mwf')
    is_text_file = file.file.name.lower().endswith('.txt')
    content = None

    if is_MFER_file:
        try:
            content = get_header(file.file.path)  
        except Exception as e:
            content = f"Error reading file: {e}"
    elif is_text_file:
        try:
            with open(file.file.path, 'r') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"

    context = {'file': file, 'content': content, 'is_text_file': is_text_file, 'is_MFER_file': is_MFER_file}
    return render(request, 'base/file.html', context)


# Function for logging in a user
def loginPage(request):
    
    # sets the variable page to specify that this is a login page, it is passed into the context variable, and used in the html to run the correct code.
    page = 'login'
    
    # If the user is already logged in and tries to click on the login button again, they will just get redirected to home instead. 
    if request.user.is_authenticated:
        return redirect('home')
    
    # Checks if a POST request was sent. 
    if request.method == 'POST':
        # Get the username and password from the data sent in the POST request. 
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        # Checks if the user exists with a try catch block. 
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        # Gets user object based on username and password.
        # Authenticate method will either give us an error or return back a user that matches the credentials (username and password).
        user = authenticate(request, username=username, password=password)
        
        # Logs the user in if there is one, and returns home. 
        if user is not None:
            login(request, user)
            messages.success(request, f'Logged in successfully as {user.username}.') 
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')
                
    
    context = {'page' : page}
    return render(request, 'base/login_register.html', context)    

# Function for logging out a user. 
def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    # else is used in the html, so no need for a page variable here. 
    #form = UserCreationForm()
    form = UserRegistrationForm()

    # Check if method is a POST request
    if request.method == 'POST':
        #form = UserCreationForm(request.POST) # passes in the data: username and password into user creation form
        form = UserRegistrationForm(request.POST)

        # Checks if the form is valid
        if form.is_valid():
            user = form.save(commit=False) # saving the form, freezing it in time. If the form is valid, the user is created and we want to be able to access it right away. This is why we set commit = False
            user.username = user.username.lower() # Now that the user is created, we can access their credentials, like username and password. We lowercase the username of the user. 
            user.save() # saves the user. 
            
            # Now, use the extra fields to create a user instance
            UserProfile.objects.create(
                user=user,
                name=form.cleaned_data.get('name'),
                mobile=form.cleaned_data.get('mobile'),
                specialization=form.cleaned_data.get('specialization'),
            ) 
            
            login(request, user) # logs the user in.
            return redirect('home') # sends the user back to the home page.
        else: 
            messages.error(request, 'An error occurred during registration')
            
    context = {'form' : form}
    return render(request,'base/login_register.html', context)

@login_required
def viewUser(request):
    
    users = UserProfile.objects.all()
    
    context = {'users' : users}
    return render(request,'base/view_user.html', context)
    
@login_required
def viewSubject(request):
    
    subjects = Subject.objects.all()
    
    context = {'subjects' : subjects}
    return render(request,'base/view_subject.html', context)


@login_required
def viewProject(request):
    # Check if the logged-in user is associated with a Doctor instance
    try:
        user_profile = request.user.userprofile
        # Filter projects where the current user's doctor instance is in the project's doctors
        projects = Project.objects.filter(users=user_profile)
    except UserProfile.DoesNotExist:
        # If the user does not have an associated Doctor instance, return an empty project list
        projects = Project.objects.none()
    
    context = {'projects': projects}
    return render(request, 'base/view_project.html', context)
    

@login_required
def viewFile(request):
    
    files = File.objects.all()
    
    context = {'files' : files}
    return render(request,'base/view_file.html', context)


@login_required
def viewVitals(request):
    
    vitals = Vitals.objects.all()

    context = {'vitals' : vitals}
    return render(request,'base/view_vitals.html', context)

@login_required
def addSubject(request):
    if request.method == "POST":
        subject_id = request.POST.get('subject_id')
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        birth_date = request.POST.get('birth_date')
        file_id = request.POST.get('file_id') or None

        # Handle the optional file association
        file_instance = None
        if file_id:
            file_instance = File.objects.get(id=file_id)

        try:
            Subject.objects.create(
                subject_id=subject_id,
                name=name,
                gender=gender,
                birth_date=birth_date if birth_date else None,  # Handle empty birth_date
                file=file_instance
            )
            messages.success(request, "Subject added successfully.")
            return redirect("viewSubject")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    # If GET request or form not valid, render the form page again
    files = File.objects.all()  # Provide list of files for the form
    return render(request, 'base/add_subject.html', {'files': files})

@login_required
def addProject(request):
    if request.method == "POST":
        rekNummer = request.POST.get('rekNummer')
        description = request.POST.get('description')
        users_ids = request.POST.getlist('users')  
        subjects_ids = request.POST.getlist('subjects')  

        # Create project instance
        project = Project.objects.create(rekNummer=rekNummer, description=description)

        # Set doctors and subjects for the project
        project.users.set(UserProfile.objects.filter(id__in=users_ids))
        project.subjects.set(Subject.objects.filter(id__in=subjects_ids))

        messages.success(request, "Project added successfully.")
        return redirect("viewProject")
    
    users = UserProfile.objects.all()
    subjects = Subject.objects.all()
    context = {'users' : users, 'subjects' : subjects}
    return render(request, 'base/add_project.html', context)



@login_required
def importFile(request):
    form = FileForm()
    if request.method == 'POST' and 'submitted' in request.POST:
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "File uploaded successfully.")
            return redirect('viewFile')
        else:
            # Check explicitly for empty title or file when the form is submitted
            if not request.FILES.get('file') or not request.POST.get('title'):
                messages.error(request, "Both title and file are required.")
            else:
                # Handle other form errors
                messages.error(request, "Please correct the error below.")

    return render(request, 'base/import_file.html', {'form': form})


@login_required
def claimFile(request, file_id):
    file_to_claim = get_object_or_404(File, id=file_id)

    if FileClaim.objects.filter(file=file_to_claim).exists():
        messages.error(request, "This file has already been claimed.")
        return redirect('viewFile')

    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, "You are not registered as a user profile.")
        return redirect('viewFile')

    FileClaim.objects.create(user=user_profile, file=file_to_claim)
    messages.success(request, "File claimed successfully.")

    if file_to_claim.file.name.lower().endswith('.mwf'):
        try:
            header = get_header(file_to_claim.file.path)
            subject_id = getattr(header, 'patientID', None)
            time_stamp = getattr(header, 'measurementTimeISO', None)
            subject_name = getattr(header, 'patientName', "Unknown")
            subject_sex = getattr(header, 'patientSex', "Unknown")
            birth_date_str = getattr(header, 'birthDateISO', None)

            birth_date = None
            if birth_date_str and birth_date_str != 'N/A':
                try:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
        
            new_subject = Subject.objects.create(
                subject_id=time_stamp + " " + subject_id, 
                name=subject_name,
                gender=subject_sex,
                birth_date=birth_date,
                file=file_to_claim
            )
            messages.success(request, f"Subject created with ID: {new_subject.subject_id}")
        except IntegrityError:
                messages.info(request, "This patient already exists.")
                return redirect('viewFile')
            
        except Exception as e:
            messages.error(request, f"An error occurred while processing the file: {str(e)}")
    else:
        messages.error(request, "Unsupported file format. Only .MWF files are accepted.")

    return redirect('viewFile')


def downloadCSV(request, file_id):
    file_instance = get_object_or_404(File, id=file_id)
    file_path = file_instance.file.path
    output_csv_path = file_path.rsplit('.', 1)[0] + '.csv'

    # Convert the file to CSV format
    convert_to_csv(file_path, output_csv_path)

    # Serve the CSV file
    with open(output_csv_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(output_csv_path)}"'
        return response

def printMFERheader(request, file_id):
    file_instance = get_object_or_404(File, id=file_id)
    file_path = file_instance.file.path
    
    try:
        # Check if the file needs to be anonymized before printing the header
        if 'anonymize' in request.POST and request.POST['anonymize'] == 'true':
            anonymized_file_path = anonymizeData(file_path)
            header_info = get_header(anonymized_file_path)
        else:
            header_info = get_header(file_path)
        
        response = HttpResponse(header_info, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file_instance.title}_header.txt"'
        return response
    except Exception as e:
        return HttpResponse(f"An error occurred while retrieving the header: {str(e)}", status=500)


def anonymizeData(file_path):
    try:
        data = Data(file_path)
        data.anonymize()
        anonymized_path = file_path.rsplit('.', 1)[0] + '_anonymized.mwf'
        data.writeToBinary(anonymized_path)
        return anonymized_path
    except Exception as e:
        raise Exception(f"Failed to anonymize and save the file: {str(e)}")


def plotGraph(request, file_id):
    try:
        file_instance = get_object_or_404(File, id=file_id)
        file_path = file_instance.file.path

        if file_path.lower().endswith('.mwf'):
            csv_path = file_path.rsplit('.', 1)[0] + '.csv'
            convert_to_csv(file_path, csv_path)
            file_path = csv_path  # Update file path to the new CSV file

        df = pd.read_csv(file_path, nrows=int(request.GET.get('rows', 10000)))
        df = df.apply(pd.to_numeric, errors='coerce').interpolate().dropna()

        combined = request.GET.get('combined', 'false') == 'true'
        if combined:
            fig = go.Figure()
            for column in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines', name=column))
            fig.update_layout(title='Combined Graph', xaxis_title='Index', yaxis_title='Values')
        else:
            fig = make_subplots(rows=len(df.columns), cols=1, shared_xaxes=True)
            for i, column in enumerate(df.columns):
                fig.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines', name=column), row=i+1, col=1)
            fig.update_layout(title='Multiple Subplots Graph')

        graph_html = plot(fig, output_type='div', include_plotlyjs=False)
        
        # Print the generated HTML for debugging
        print(graph_html)

        return JsonResponse({'graph_html': graph_html})
    except ValueError as e:
        return HttpResponseBadRequest(f"Invalid 'rows' parameter: {e}")
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
