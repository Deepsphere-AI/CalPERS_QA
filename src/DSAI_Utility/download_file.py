import os
import urllib
from PyPDF2 import PdfReader
from google.cloud import storage

def download_pdf_file(vAR_URL):
    # Decode the URL to handle any encoded characters like spaces (%20)
    vAR_URL = urllib.parse.unquote(vAR_URL)
    
    # Extract the filename from the URL
    vAR_filename = vAR_URL.split('/')[-1]
    
    # Set the directory where the file will be saved
    vAR_directory = "Result/"
    vAR_filepath = os.path.join(vAR_directory, vAR_filename)

    # Create the Result directory if it doesn't exist
    if not os.path.exists(vAR_directory):
        os.makedirs(vAR_directory)

    # Define your bucket name
    bucket_name = vAR_URL.split('/')[-2]

    # Create a storage client
    storage_client = storage.Client()

    # Get the bucket and blob
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(vAR_filename)
    
    # Download the file
    try:
        blob.download_to_filename(vAR_filepath)
        print(f"File downloaded successfully to {vAR_filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    # Read the PDF file
    try:
        vAR_reader = PdfReader(vAR_filepath)
        vAR_num_pages = len(vAR_reader.pages)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

    return vAR_filepath, vAR_num_pages