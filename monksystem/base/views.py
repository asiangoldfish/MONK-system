# Standard library imports for various functionalities
import os
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
# Django-specific imports for handling web requests and database operations
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
# Importing models for the database schema related to the application
from .models import Subject, UserProfile, Project, File, FileImport
# Forms for handling file import and user registration
from .forms import FileForm, UserRegistrationForm, FileFieldForm
# Importing functionalities from monklib for handling medical data
from monklib import get_header, convert_to_csv, Data
# Plotly import for creating subplots in graphs
from plotly.subplots import make_subplots
from plotly.offline import plot

@login_required
def homePage(request):
    return render(request, 'base/home.html')


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


@login_required
def file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    user_profile = request.user.userprofile
    # Retrieve all subjects linked to this file
    subjects = Subject.objects.filter(file=file)
    # Find projects that include these subjects
    projects = Project.objects.filter(subjects__in=subjects)
     # Check if the user is part of any of these projects or has imported the file
    user_in_project = projects.filter(users=user_profile).exists()
    user_has_imported = FileImport.objects.filter(file=file, user=user_profile).exists()

    if not (user_in_project or user_has_imported):
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

    context = {'file': file, 
               'content': content, 
               'is_text_file': is_text_file,
               'is_MFER_file': is_MFER_file}
    
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
            ) 
            
            login(request, user) # logs the user in.
            return redirect('home') # sends the user back to the home page.
        else: 
            messages.error(request, 'An error occurred during registration')
            
    context = {'form' : form}
    return render(request,'base/login_register.html', context)
    
@login_required
def viewSubject(request):
    subjects = Subject.objects.all()
    context = {'subjects' : subjects}
    return render(request,'base/view_subject.html', context)


@login_required
def viewProject(request):
    # Check if the logged-in user is associated with a user instance
    try:
        user_profile = request.user.userprofile
        # Filter projects where the current user's instance is in the project's users
        projects = Project.objects.filter(users=user_profile)
    except UserProfile.DoesNotExist:
        # If the user does not have an associate instance, return an empty project list
        projects = Project.objects.none()
    
    context = {'projects': projects}
    return render(request, 'base/view_project.html', context)
    

@login_required
def viewFile(request):
    try: 
        user_profile = request.user.userprofile
        # Only include files with successful subject creation or another success indicator
        files = File.objects.filter(fileimport__user=user_profile, subjects__isnull=False)
    except UserProfile.DoesNotExist:
        files = File.objects.none()
    context = {'files': files}
    return render(request, 'base/view_file.html', context)



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
def editProject(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        user_ids = request.POST.getlist('users')
        subject_ids = request.POST.getlist('subjects')
        if user_ids:
            project.users.set(UserProfile.objects.filter(id__in=user_ids))
        if subject_ids:
            project.subjects.set(Subject.objects.filter(id__in=subject_ids))
        project.save()
        messages.success(request, "Project updated successfully.")
        return redirect('viewProject')
    else:
        users = UserProfile.objects.all()
        subjects = Subject.objects.all()
        context = {'project': project, 'users': users, 'subjects': subjects}
        return render(request, 'base/edit_project.html', context)
    
    
def leaveProject(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    user_profile = request.user.userprofile
    
    if user_profile in project.users.all():
        project.users.remove(user_profile)
        project.save()
        messages.success(request, "You have successfully left the project.")
    else:
        messages.error(request, "You are not a member of this project.")
    
    return redirect('viewProject')


@login_required
def importFile(request):
    form = FileForm()
    if request.method == 'POST' and 'submitted' in request.POST:
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            imported_file = request.FILES['file']
            # Check if the file is NOT a .mwf file
            if not imported_file.name.lower().endswith('.mwf'):
                messages.error(request, "Only .MWF files are allowed.")
                return render(request, 'base/import_file.html', {'form': form})

            try:
                user_profile = request.user.userprofile
            except UserProfile.DoesNotExist:
                messages.error(request, "You are not registered as a regular user.")
                return redirect('viewFile')  # Redirect to a view where users can create/update their profile

            new_file = form.save()
            FileImport.objects.create(user=user_profile, file=new_file)

            process_and_create_subject(new_file, request)

            messages.success(request, "File imported and processed successfully.")
            return redirect('viewFile')
        else:
            messages.error(request, "Please correct the error below.")
    return render(request, 'base/import_file.html', {'form': form})


@login_required
def importMultipleFiles(request):
    form = FileFieldForm()
    if request.method == 'POST':
        form = FileFieldForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('file_field')
            valid_files = []
            for f in files:
                # Check if any file is NOT a .mwf file
                if not f.name.lower().endswith('.mwf'):
                    messages.error(request, "Only .MWF files are allowed. Invalid file: " + f.name)
                    continue  # Skip adding this file to the list
                valid_files.append(f)

            if valid_files:
                try:
                    user_profile = request.user.userprofile
                except UserProfile.DoesNotExist:
                    messages.error(request, "You are not registered as a regular user.")
                    return redirect('viewFile')  # Redirect to a view where users can create/update their profile

                for f in valid_files:
                    new_file = File.objects.create(file=f, title=f.name)
                    FileImport.objects.create(user=user_profile, file=new_file)
                    process_and_create_subject(new_file, request)

                messages.success(request, "All valid .MWF files imported and processed successfully.")
            else:
                messages.error(request, "No valid .MWF files provided.")
            return redirect('viewFile')
        else:
            messages.error(request, "Please correct the error below.")
    return render(request, "base/import_file.html", {"form": form})


def process_and_create_subject(file, request):
    if file.file.name.lower().endswith('.mwf'):
        try:
            header = get_header(file.file.path)
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

            Subject.objects.create(
                subject_id=time_stamp + " " + subject_id, 
                name=subject_name,
                gender=subject_sex,
                birth_date=birth_date,
                file=file
            )
            messages.success(request, f"Subject created for file {file.title}")
        except IntegrityError:
            # Handle the unique constraint failure
            messages.info(request, f"This subject already exists. No duplicate created for file {file.title}.")
        except Exception as e:
            messages.error(request, f"Failed to process file {file.title} for subject creation: {str(e)}")
    else:
        messages.info(request, f"File {file.title} imported but no subject created due to file type.")


# Function to download a file in CSV format
def downloadFormatCSV(request, file_id):
    # Check for POST request to ensure that the request is a result of form submission
    if request.method == 'POST':
        # Retrieve the list of channels selected by the user from the form
        selected_channels = request.POST.getlist('channels')
        # Retrieve start and end times from the form, converting to float or defaulting to 0
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        start_seconds = float(start_time_str) if start_time_str else 0.0
        end_seconds = float(end_time_str) if end_time_str else 0.0

        # Get the file object, ensuring it exists or return a 404 error
        file = get_object_or_404(File, id=file_id)
        # Use monklib to retrieve the header of the file for channel information
        header = get_header(file.file.path)
        # Create a Data object using the monklib for further processing
        data = Data(file.file.path)

        # Filter the data based on the channels selected by the user
        for index, channel in enumerate(header.channels):
            data.setChannelSelection(index, channel.attribute in selected_channels)

        # If times were provided, set the data to only include the specified interval
        if start_time_str or end_time_str:
            data.setIntervalSelection(start_seconds, end_seconds)

        # Define the output path for the CSV and use monklib to write the data to CSV
        output_path = file.file.path.rsplit('.', 1)[0] + '_selected.csv'
        data.writeToCsv(output_path)

        # Open the CSV file, read its content and prepare a HTTP response to send the file to the user
        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(output_path)}"'
            return response
    # If the request is not POST, return a forbidden error response
    else:
        return HttpResponseForbidden("Invalid request")

# Function to download the header information of an MFER file
def downloadHeaderMFER(request, file_id):
    # Retrieve the file object, or return a 404 error if it doesn't exist
    file_instance = get_object_or_404(File, id=file_id)
    # Get the path of the file on the server
    file_path = file_instance.file.path
    
    try:
        # Check if anonymization is requested via POST parameters
        if 'anonymize' in request.POST and request.POST['anonymize'] == 'true':
            # Anonymize the data if requested
            anonymized_file_path = anonymizeData(file_path)
            # Get the header information from the anonymized file using function from monklib
            header_info = get_header(anonymized_file_path)
        else:
            # Get the header information from the original file using function from monklib
            header_info = get_header(file_path)
        
        # Prepare a response with the header information as plain text
        response = HttpResponse(header_info, content_type='text/plain')
        # Suggest a filename for the header info when downloaded
        response['Content-Disposition'] = f'attachment; filename="{file_instance.title}_header.txt"'
        return response
    # Return an error message if something goes wrong
    except Exception as e:
        return HttpResponse(f"An error occurred while retrieving the header: {str(e)}", status=500)


def downloadMWF(request, file_id):
    # Retrieve the file object, or return a 404 error if it doesn't exist
    file_instance = get_object_or_404(File, id=file_id)

    # Verify that the file is of the .mwf format, otherwise return an error
    if not file_instance.file.name.lower().endswith('.mwf'):
        return HttpResponseBadRequest("Unsupported file format.")

    try:
        # Get the path of the file on the server
        file_path = file_instance.file.path
        # Check if anonymization is requested via GET parameters
        if request.GET.get('anonymize') == 'true':
            # Anonymize the data if requested
            file_path = anonymizeData(file_path)

        # Open and read the content of the file
        with open(file_path, 'rb') as file:
            content = file.read()
            # Prepare a response with the file content as plain text
            response = HttpResponse(content, content_type="application/octet-stream")
            # Suggest a filename for the raw data when downloaded, ensuring it uses the .mwf extension
            response['Content-Disposition'] = f'attachment; filename="{file_instance.title}.mwf"'
            return response
    # Return an error message if something goes wrong
    except Exception as e:
        return HttpResponse(f"An error occurred while reading the file: {str(e)}", status=500)



# Function to anonymize data within an MFER file
def anonymizeData(file_path):
    try:
        # Load the data using monklib's Data class
        data = Data(file_path)
        # Anonymize the data using the provided method from monklib's anonymization script
        data.anonymize()
        # Define the path for the anonymized data
        anonymized_path = file_path.rsplit('.', 1)[0] + '_anonymized.mwf'
        # Write the anonymized data to binary in a new file, using monklibs functionality
        data.writeToBinary(anonymized_path)
        # Return the path to the anonymized file        
        return anonymized_path
    # Raise an exception if anonymization fails
    except Exception as e:
        raise Exception(f"Failed to anonymize and save the file: {str(e)}")

# Function to plot graphs based on CSV data
def plotGraph(request, file_id):
    try:
        # Retrieve parameters from the GET request
        # Determine if a combined graph is requested
        combined = request.GET.get('combined', 'false').lower() == 'true'
        # Set the maximum number of rows to read from the CSV
        rows = int(request.GET.get('rows', 10000))        
        # Retrieve and handle the file object
        file_instance = get_object_or_404(File, id=file_id)
        # Define the CSV path for the data file
        csv_path = file_instance.file.path.rsplit('.', 1)[0] + '.csv'
        # Convert the data file to CSV format using monklib's functionality
        convert_to_csv(file_instance.file.path, csv_path)  
        # Load and prepare the data from the CSV
        df = pd.read_csv(csv_path, nrows=rows)
        df = df.apply(pd.to_numeric, errors='coerce').interpolate().dropna()
        # Generate the plot
        if combined:
            # Initialize a figure for plotting
            fig = go.Figure()
            for column in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines', name=column))
            fig.update_layout(title='Combined Graph', xaxis_title='Index', yaxis_title='Values')
        else:
            fig = make_subplots(rows=len(df.columns), cols=1, shared_xaxes=True)
            # Add traces to the figure based on the CSV columns
            for i, column in enumerate(df.columns):
                fig.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines', name=column), row=i + 1, col=1)
            fig.update_layout(title='Multiple Subplots Graph')

        # Convert the plot to HTML and send it back
        graph_html = fig.to_html(full_html=False, include_plotlyjs=True)
        return JsonResponse({'graph_html': graph_html})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


