# Step 1: Base Image
FROM python:3.10.6

# Step 2: Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Step 3: Set the working directory in the container
WORKDIR /SOCIAL-MEDIA-APP

# Step 4: Copy the requirements file and install dependencies
COPY requirements.txt /SOCIAL-MEDIA-APP/
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application code to the container
COPY . /SOCIAL-MEDIA-APP/

# Step 6: Change to the SocialMedia directory before running migrate
WORKDIR /SOCIAL-MEDIA-APP/SocialMedia/

# Step 7: Run Django migrations (if necessary)
RUN python manage.py migrate

# Step 9: Expose the port for the application
EXPOSE 8000

# Step 10: Command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
