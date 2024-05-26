import os
from datetime import datetime
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from monklib import get_header, convert_to_csv, Data
from .models import Subject, File, FileImport
from django.views.decorators.http import require_GET, require_POST

# Function for processing and creating a subject from file upload.
def process_and_create_subject(file, request):
    # Check if the uploaded file is a .MWF file, which is required for this process.
    if file.file.name.lower().endswith(".mwf"):
        try:
            # Use monklib's get_header function to extract header information from the file.
            header = get_header(file.file.path)
            # Extract necessary details from the header for creating a Subject.
            subject_id = getattr(header, "patientID", None)
            time_stamp = getattr(header, "measurementTimeISO", None)
            subject_name = getattr(header, "patientName", "Unknown")
            subject_sex = getattr(header, "patientSex", "Unknown")
            birth_date_str = getattr(header, "birthDateISO", None)
            birth_date = None
            # Convert the birth date string to a date object, handling cases where the date might be 'N/A' or malformed.
            if birth_date_str and birth_date_str != "N/A":
                try:
                    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
                except ValueError:
                    # Handle the case where the birth date string is not a valid date.
                    pass

            # Create a new Subject instance and save it to the database.
            Subject.objects.create(
                subject_id=time_stamp + " " + subject_id,
                name=subject_name,
                gender=subject_sex,
                birth_date=birth_date,
                file=file,
            )
            # Send a success message back to the user.
            messages.success(request, f"Subject created for file {file.title}")
        except IntegrityError:
            # Handle the case where the subject might already exist in the database, preventing duplicate entries.
            messages.info(
                request,
                f"This subject already exists. No duplicate created for file {file.title}.",
            )
        except Exception as e:
            # General error handling if something goes wrong during the subject creation process.
            messages.error(
                request,
                f"Failed to process file {file.title} for subject creation: {str(e)}",
            )
    else:
        # If the file is not an .MWF file, inform the user that no subject will be created.
        messages.info(
            request,
            f"File {file.title} imported but no subject created due to file type.",
        )


# Function to download a file in CSV format
@require_POST
def download_format_csv(request, file_id):
    # Check for POST request to ensure that the request is a result of form submission
    if request.method == "POST":
        # Retrieve the list of channels selected by the user from the form
        selected_channels = request.POST.getlist("channels")
        # Retrieve start and end times from the form, converting to float or defaulting to 0
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")
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
        output_path = file.file.path.rsplit(".", 1)[0] + ".csv"
        data.writeToCsv(output_path)

        # Open the CSV file, read its content and prepare a HTTP response to send the file to the user
        with open(output_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(output_path)}"'
            )
            return response
    # If the request is not POST, return a forbidden error response
    else:
        return HttpResponseForbidden("Invalid request")


# Function to download the header information of an MFER file
def download_mfer_header(request, file_id):
    # Retrieve the file object, or return a 404 error if it doesn't exist
    file_instance = get_object_or_404(File, id=file_id)
    # Get the path of the file on the server
    file_path = file_instance.file.path

    try:
        # Check if anonymization is requested via POST parameters
        if "anonymize" in request.POST and request.POST["anonymize"] == "true":
            # Anonymize the data if requested
            anonymized_file_path = anonymize_data(file_path)
            # Get the header information from the anonymized file using function from monklib
            header_info = get_header(anonymized_file_path)
        else:
            # Get the header information from the original file using function from monklib
            header_info = get_header(file_path)

        # Prepare a response with the header information as plain text
        response = HttpResponse(header_info, content_type="text/plain")
        # Suggest a filename for the header info when downloaded
        response["Content-Disposition"] = (
            f'attachment; filename="{file_instance.title}_header.txt"'
        )
        return response
    # Return an error message if something goes wrong
    except Exception as e:
        return HttpResponse(
            f"An error occurred while retrieving the header: {str(e)}", status=500
        )


# Function for downloading the .MWF file
def download_mwf(request, file_id):
    # Retrieve the file object, or return a 404 error if it doesn't exist
    file_instance = get_object_or_404(File, id=file_id)

    # Verify that the file is of the .mwf format, otherwise return an error
    if not file_instance.file.name.lower().endswith(".mwf"):
        return HttpResponseBadRequest("Unsupported file format.")

    try:
        # Get the path of the file on the server
        file_path = file_instance.file.path
        # Check if anonymization is requested via GET parameters
        if request.GET.get("anonymize") == "true":
            # Anonymize the data if requested
            file_path = anonymize_data(file_path)

        # Open and read the content of the file
        with open(file_path, "rb") as file:
            content = file.read()
            # Prepare a response with the file content as plain text
            response = HttpResponse(content, content_type="application/octet-stream")
            # Suggest a filename for the raw data when downloaded, ensuring it uses the .mwf extension
            response["Content-Disposition"] = (
                f'attachment; filename="{file_instance.title}.mwf"'
            )
            return response
    # Return an error message if something goes wrong
    except Exception as e:
        return HttpResponse(
            f"An error occurred while reading the file: {str(e)}", status=500
        )


# Function to anonymize data within an MFER file
def anonymize_data(file_path):
    try:
        # Load the data using monklib's Data class
        data = Data(file_path)
        # Anonymize the data using the provided method from monklib's anonymization script
        data.anonymize()
        # Define the path for the anonymized data
        anonymized_path = file_path.rsplit(".", 1)[0] + "_anonymized.mwf"
        # Write the anonymized data to binary in a new file, using monklibs functionality
        data.writeToBinary(anonymized_path)
        # Return the path to the anonymized file
        return anonymized_path
    # Raise an exception if anonymization fails
    except Exception as e:
        raise Exception(f"Failed to anonymize and save the file: {str(e)}")


# Function to plot graphs based on CSV data
def plot_graph(request, file_id):
    try:
        # Retrieve parameters from the GET request
        # Determine if a combined graph is requested
        combined = request.GET.get("combined", "false").lower() == "true"
        # Set the maximum number of rows to read from the CSV
        rows = int(request.GET.get("rows", 10000))
        # Retrieve and handle the file object
        file_instance = get_object_or_404(File, id=file_id)
        # Define the CSV path for the data file
        csv_path = file_instance.file.path.rsplit(".", 1)[0] + ".csv"
        # Convert the data file to CSV format using monklib's functionality
        convert_to_csv(file_instance.file.path, csv_path)
        # Load and prepare the data from the CSV
        df = pd.read_csv(csv_path, nrows=rows)
        df = df.apply(pd.to_numeric, errors="coerce").interpolate().dropna()
        # Generate the plot
        if combined:
            # Initialize a figure for plotting
            fig = go.Figure()
            for column in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[column], mode="lines", name=column)
                )
            fig.update_layout(
                title="Combined Graph", xaxis_title="Index", yaxis_title="Values"
            )
        else:
            fig = make_subplots(rows=len(df.columns), cols=1, shared_xaxes=True)
            # Add traces to the figure based on the CSV columns
            for i, column in enumerate(df.columns):
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[column], mode="lines", name=column),
                    row=i + 1,
                    col=1,
                )
            fig.update_layout(title="Multiple Subplots Graph")

        # Convert the plot to HTML and send it back
        graph_html = fig.to_html(full_html=False, include_plotlyjs=True)
        return JsonResponse({"graph_html": graph_html})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
