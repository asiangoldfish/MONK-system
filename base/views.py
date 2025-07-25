# Standard library imports for various functionalities
import os
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Django-specific imports for handling web requests and database operations
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.contrib.auth import authenticate, login, logout

# Importing functionalities from monklib for handling medical data
from monklib import get_header, convert_to_csv, Data

# Importing models for the database schema related to the application
from .models import Subject, UserProfile, Project, File, FileImport

# Forms for handling file import and user registration
from .forms import FileForm, UserRegistrationForm, FileFieldForm

from .utils import (
    process_and_create_subject,
    anonymize_data,
    download_format_csv,
    download_mfer_header,
    download_mwf,
    plot_graph,
)

# Function for rendering the home.html template, which displays the home screen of the website.
@login_required
@require_GET
def home_page(request):
    return render(request, "base/home.html")


# Function for rendering the subject.html template, which displays details about a subject.
@login_required
@require_GET
def subject(request, pk):
    subject = Subject.objects.get(subject_id=pk)
    context = {"subject": subject}
    return render(request, "base/subject.html", context)


# Function for rendering the user.html template, which displays details about a user.
@login_required
@require_GET
def user(request, pk):
    user = UserProfile.objects.get(id=pk)
    context = {"user": user}
    return render(request, "base/user.html", context)


# Function for rendering the project.html template, which displays the details of a project.
@login_required
@require_GET
def project(request, pk):
    project = Project.objects.get(id=pk)
    context = {"project": project}
    return render(request, "base/project.html", context)


# Function for handling the rendering of the file.html template, which displays all the details about a file.
@login_required
def file(request, file_id):
    # Retrieves the file or throws a 404 error if not found.
    file = get_object_or_404(File, id=file_id)
    # Fetches the user profile from the request; UserProfile is linked to the standard User model.
    user_profile = request.user.userprofile
    # Retrieve all subjects linked to this file
    subjects = Subject.objects.filter(file=file)
    # Find projects that include these subjects
    projects = Project.objects.filter(subjects__in=subjects)
    # Check if the user is part of any of these projects or has imported the file
    user_in_project = projects.filter(users=user_profile).exists()
    user_has_imported = FileImport.objects.filter(file=file, user=user_profile).exists()

    # Deny access if the user does not have proper associations with the file.
    if not (user_in_project or user_has_imported):
        return HttpResponseForbidden("You do not have permission to view this file.")

    # Determine the file type to decide on the display method.
    is_MFER_file = file.file.name.lower().endswith(".mwf")
    is_text_file = file.file.name.lower().endswith(".txt")
    content = None

    # Process file content if it is a medical waveform (MFER) file.
    if is_MFER_file:
        try:
            content = get_header(file.file.path)
        except Exception as e:
            content = f"Error reading file: {e}"
    # Read the content directly if it's a text file.
    elif is_text_file:
        try:
            with open(file.file.path, "r") as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"

    # Build the context with file details and content for rendering.
    context = {
        "file": file,
        "content": content,
        "is_text_file": is_text_file,
        "is_MFER_file": is_MFER_file,
    }

    # Render the file view template with the context.
    return render(request, "base/file.html", context)


# Function for rendering the login_register.html template, which handles logging in of users.
def login_page(request):
    # sets the variable page to specify that this is a login page, it is passed into the context variable,
    # and used in the html to run the correct code.
    page = "login"
    # If the user is already logged in and tries to click on the login button again, they will just get redirected to home instead.
    if request.user.is_authenticated:
        return redirect("home")

    # Checks if a POST request was sent.
    if request.method == "POST":
        # Get the username and password from the data sent in the POST request.
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        # Checks if the user exists with a try catch block.
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")
        # Gets user object based on username and password.
        # Authenticate method will either give us an error or return back a user that matches the credentials (username and password).
        user = authenticate(request, username=username, password=password)
        # Logs the user in if there is one, and returns home.
        if user is not None:
            login(request, user)
            messages.success(request, f"Logged in successfully as {user.username}.")
            return redirect("home")
        else:
            messages.error(request, "Username or password does not exist")

    context = {"page": page}
    return render(request, "base/login_register.html", context)


# Function for logging out a user.
def logout_user(request):
    logout(request)
    return redirect("home")


# Function for rendering the login_register.html template, handling the registration of a new user
def register_page(request):
    # else is used in the html, so no need for a page variable here.
    # form = UserCreationForm()
    form = UserRegistrationForm()

    # Check if method is a POST request
    if request.method == "POST":
        # form = UserCreationForm(request.POST) # passes in the data: username and password into user creation form
        form = UserRegistrationForm(request.POST)

        # Checks if the form is valid
        if form.is_valid():
            user = form.save(commit=False)  # saving the form, freezing it in time.
            # If the form is valid, the user is created and we want to be able to access it right away. This is why we set commit = False
            user.username = (
                user.username.lower()
            )  # Now that the user is created, we can access their credentials, like username and password.
            # We lowercase the username of the user.
            user.save()  # saves the user.

            # Now, use the extra fields to create a user instance
            UserProfile.objects.create(
                user=user,
                name=form.cleaned_data.get("name"),
                mobile=form.cleaned_data.get("mobile"),
            )

            login(request, user)  # logs the user in.
            return redirect("home")  # sends the user back to the home page.
        else:
            messages.error(request, "An error occurred during registration")

    context = {"form": form}
    return render(request, "base/login_register.html", context)


# Function for rendering the view_subjects.html template, which displays all the subjects in the system.
@login_required
@require_GET
def view_subjects(request):
    subjects = Subject.objects.all()
    context = {"subjects": subjects}
    return render(request, "base/view_subjects.html", context)


# Function for rendering the view_projects.html template,
# which displays all the projects in the system that the current user is apart of.
@login_required
@require_GET
def view_projects(request):
    # Check if the logged-in user is associated with a user instance
    try:
        user_profile = request.user.userprofile
        # Filter projects where the current user's instance is in the project's users
        projects = Project.objects.filter(users=user_profile)
    except UserProfile.DoesNotExist:
        # If the user does not have an associate instance, return an empty project list
        projects = Project.objects.none()

    context = {"projects": projects}
    return render(request, "base/view_projects.html", context)


# Function for rendering the view_files.html template, which displays all the files imported by user.
@login_required
@require_GET
def view_files(request):
    try:
        user_profile = request.user.userprofile
        # Only include files with successful subject creation or another success indicator
        files = File.objects.filter(
            fileimport__user=user_profile, subjects__isnull=False
        )
    except UserProfile.DoesNotExist:
        files = File.objects.none()
    context = {"files": files}
    return render(request, "base/view_files.html", context)


# Function for rendering the add_project.html template,
# which handles creation of new projects with specified users and subjects.
@login_required  # Decorator to ensure only authenticated users can access this function.
def add_project(request):
    # Check if the request method is POST, indicating form submission.
    if request.method == "POST":
        # Retrieve data from the POST request for new project creation.
        rekNummer = request.POST.get("rekNummer")
        description = request.POST.get("description")
        user_ids = request.POST.getlist("users")
        subject_ids = request.POST.getlist("subjects")

        # Create a new project instance with the provided rekNummer and description.
        project = Project.objects.create(rekNummer=rekNummer, description=description)
        # Set the users for the project by filtering UserProfile instances based on submitted IDs.
        project.users.set(UserProfile.objects.filter(id__in=user_ids))

        # Filter subjects that have been linked to the specified users and set these subjects for the project.
        valid_subjects = Subject.objects.filter(
            id__in=subject_ids, file__fileimport__user__id__in=user_ids
        )
        project.subjects.set(valid_subjects)

        # Notify the user of successful project creation.
        messages.success(request, "Project added successfully.")
        # Redirect to the project view page.
        return redirect("view_projects")
    # If the request is not POST (i.e., a GET request), prepare data for the form.
    else:
        # Retrieve all users to display in the user selection part of the form.
        users = UserProfile.objects.all()
        # Retrieve only those subjects that are linked to files imported by the logged-in user.
        subjects = Subject.objects.filter(
            file__fileimport__user=request.user.userprofile
        )
        # Render the add project page with lists of users and subjects for the form.
        return render(
            request, "base/add_project.html", {"users": users, "subjects": subjects}
        )


# Function for rendering the edit_project.html template,
# handles editing a project, allowing the user to add/remove other users and subjects.
@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    user_profile = request.user.userprofile

    if request.method == "POST":
        user_ids = request.POST.getlist("users")
        new_subject_ids = set(map(int, request.POST.getlist("subjects")))

        # Fetch existing subjects in the project
        existing_subject_ids = set(project.subjects.values_list("id", flat=True))

        # Get IDs of subjects the current user is allowed to modify
        allowed_subject_ids = set(
            Subject.objects.filter(file__fileimport__user=user_profile).values_list(
                "id", flat=True
            )
        )

        # Determine which new subjects are valid (must be allowed and new)
        valid_new_subject_ids = new_subject_ids.intersection(allowed_subject_ids)

        # Combine existing subjects with valid new ones
        updated_subject_ids = existing_subject_ids.union(valid_new_subject_ids)

        # Remove any unselected subjects that the user is allowed to remove
        subjects_to_remove = allowed_subject_ids.intersection(
            existing_subject_ids.difference(new_subject_ids)
        )
        final_subject_ids = updated_subject_ids.difference(subjects_to_remove)

        project.users.set(UserProfile.objects.filter(id__in=user_ids))
        project.subjects.set(Subject.objects.filter(id__in=final_subject_ids))

        project.save()
        messages.success(request, "Project updated successfully.")
        return redirect("view_projects")
    else:
        # Show all users and subjects for admin or relevant subjects for regular users
        users = (
            UserProfile.objects.all()
        )  # or filter based on some admin role if needed
        subjects = Subject.objects.filter(
            id__in=project.subjects.values_list("id", flat=True)
            | Subject.objects.filter(file__fileimport__user=user_profile).values_list(
                "id", flat=True
            )
        )

        context = {"project": project, "users": users, "subjects": subjects}
        return render(request, "base/edit_project.html", context)


# Function that allows user to leave a project which they are currently apart of.
def leave_project(request, project_id):
    # Retrieve the project by ID or return a 404 if it does not exist.
    project = get_object_or_404(Project, id=project_id)
    # Access the user's profile from the User model, a one-to-one relationship.
    user_profile = request.user.userprofile

    # Check if the user's profile is in the list of users associated with the project.
    if user_profile in project.users.all():
        # If the user is part of the project, remove them.
        project.users.remove(user_profile)
        # Save changes to the project.
        project.save()
        # Notify the user of success.
        messages.success(request, "You have successfully left the project.")
    else:
        # If the user is not part of the project, send an error message.
        messages.error(request, "You are not a member of this project.")
    # Redirect the user to the project view page, regardless of the outcome.
    return redirect("view_projects")


# Function for importing a file.
@login_required
def import_file(request):
    # Initialize a new form instance for file uploads.
    form = FileForm()
    # Check if the form has been submitted with file data.
    if request.method == "POST" and "submitted" in request.POST:
        # Populate the form with data from the request.
        form = FileForm(request.POST, request.FILES)
        # Validate the form data, specifically checking for the file.
        if form.is_valid():
            # Retrieve the file from the form.
            imported_file = request.FILES["file"]

            # Check if the file is in the required .mwf format.
            if not imported_file.name.lower().endswith(".mwf"):
                messages.error(request, "Only .MWF files are allowed.")
                return render(request, "base/import_file.html", {"form": form})

            # Try to fetch user profile to link the file import.
            try:
                user_profile = request.user.userprofile
            except UserProfile.DoesNotExist:
                messages.error(request, "You are not registered as a regular user.")
                return redirect(
                    "view_files"
                )  # Redirect to a view where users can create/update their profile

            # Save the file instance created from the form.
            new_file = form.save()
            # Create a record of the file import.
            FileImport.objects.create(user=user_profile, file=new_file)
            # Process the file to possibly create additional related records.
            process_and_create_subject(new_file, request)

            messages.success(request, "File imported and processed successfully.")
            return redirect("view_files")
        else:
            messages.error(request, "Please choose title and upload .MWF files only")
    # Render the import file page with the form.
    return render(request, "base/import_file.html", {"form": form})


# Function for importing multiple files
@login_required
def import_multiple_files(request):
    # Initialize the form designed to handle multiple file uploads.
    form = FileFieldForm()
    # Handle the POST request with file data.
    if request.method == "POST":
        # Populate the form with POST data.
        form = FileFieldForm(request.POST, request.FILES)
        # Check if the form is valid.
        if form.is_valid():
            # Retrieve a list of files from the form data.
            files = request.FILES.getlist("file_field")
            valid_files = []
            # Validate each file, checking if they are in the .mwf format.
            for f in files:
                # Check if any file is NOT a .mwf file
                if not f.name.lower().endswith(".mwf"):
                    messages.error(
                        request, "Only .MWF files are allowed. Invalid file: " + f.name
                    )
                    continue  # Skip adding this file to the list
                valid_files.append(f)

            # Process each validated file.
            if valid_files:
                try:
                    user_profile = request.user.userprofile
                except UserProfile.DoesNotExist:
                    messages.error(request, "You are not registered as a regular user.")
                    return redirect(
                        "view_files"
                    )  # Redirect to a view where users can create/update their profile

                for f in valid_files:
                    base_title = os.path.splitext(f.name)[0]
                    new_file = File.objects.create(file=f, title=base_title)
                    FileImport.objects.create(user=user_profile, file=new_file)
                    process_and_create_subject(new_file, request)

                messages.success(
                    request, "All valid .MWF files imported and processed successfully."
                )
            else:
                messages.error(request, "No valid .MWF files provided.")
            return redirect("view_files")
        else:
            messages.error(request, "Only .MWF files allowed.")
    # Render the import multiple files page with the form.
    return render(request, "base/import_file.html", {"form": form})
