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
# Forms for handling file upload and user registration
from .forms import FileForm, UserRegistrationForm  
# Importing functionalities from monklib for handling medical data
from monklib import get_header, convert_to_csv, Data
# Plotly import for creating subplots in graphs
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
    
    files = File.objects.all()
    
    context = {'files' : files}
    return render(request,'base/view_file.html', context)


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


# Ensure user must be logged in to access this function.
@login_required
def uploadFile(request):
    # Initialize an empty file form
    form = FileForm()
    # Check if the request to upload a file is a POST request
    if request.method == 'POST' and 'submitted' in request.POST:
        # Populate the form with POST data and files sent through the form
        form = FileForm(request.POST, request.FILES)
        # Check if form data is valid (file complies with expected format, title isn't empty, etc.)
        if form.is_valid():
            # Save the uploaded file data to the database
            form.save()
            # Display a success message to the user
            messages.success(request, "File uploaded successfully.")
            # Redirect to the file view page
            return redirect('viewFile')
        else:
            # If form is not valid, check for specific issues such as empty fields
            if not request.FILES.get('file') or not request.POST.get('title'):
                messages.error(request, "Both title and file are required.")
            else:
                # Handle other form errors
                messages.error(request, "Please correct the error below.")
    # Render and return the upload file form page with the form instance
    return render(request, 'base/import_file.html', {'form': form})


# Function to import ownership of a file for processing
@login_required
def importFile(request, file_id):
    # Retrieve the file object from the database; if it doesn't exist, a 404 error page is shown
    file_to_import = get_object_or_404(File, id=file_id)
    
    # Check if this file has already been imported by another user in the database
    if FileImport.objects.filter(file=file_to_import).exists():
        # Inform the user that the file has already been imported
        messages.error(request, "This file has already been imported.")
        # Redirect to the file viewing page
        return redirect('viewFile')
    
    # Try to retrieve the user profile associated with the logged-in user
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # If the user profile does not exist, inform the user and redirect
        messages.error(request, "You are not registered as a user profile.")
        return redirect('viewFile')
    
    # Create a new record in the FileImport model, linking the user and the file
    FileImport.objects.create(user=user_profile, file=file_to_import)
    # Inform the user of successful file import
    messages.success(request, "File imported successfully.")

    # Additional processing if the file is a .mwf (Medical Waveform) file
    if file_to_import.file.name.lower().endswith('.mwf'):
        try:
            # Retrieve header information from the file using monklib's get_header function
            header = get_header(file_to_import.file.path)
            # Extract specific pieces of patient information from the header
            subject_id = getattr(header, 'patientID', None)
            time_stamp = getattr(header, 'measurementTimeISO', None)
            subject_name = getattr(header, 'patientName', "Unknown")
            subject_sex = getattr(header, 'patientSex', "Unknown")
            birth_date_str = getattr(header, 'birthDateISO', None)

            # Convert the birth date string to a date object, if available and valid
            birth_date = None
            if birth_date_str and birth_date_str != 'N/A':
                try:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
        
            # Create a new subject record using the extracted data
            new_subject = Subject.objects.create(
                subject_id=time_stamp + " " + subject_id, 
                name=subject_name,
                gender=subject_sex,
                birth_date=birth_date,
                file=file_to_import
            )
            # Inform the user of successful subject creation
            messages.success(request, f"Subject created with ID: {new_subject.subject_id}")
        except IntegrityError:
                # Handle cases where a subject with the same ID already exists
                messages.info(request, "This patient already exists.")
                return redirect('viewFile')
            
        except Exception as e:
            # Handle other exceptions during file processing
            messages.error(request, f"An error occurred while processing the file: {str(e)}")
    else:
        # Handle unsupported file formats
        messages.error(request, "Unsupported file format. Only .MWF files are accepted.")
    # Redirect to the file viewing page after processing
    return redirect('viewFile')

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


