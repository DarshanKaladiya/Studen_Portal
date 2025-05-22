import os
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile, UploadedFile, Resource
from django.conf import settings

# Home Page
def home(request):
    return render(request, "authentication/index.html")

# Student Dashboard: Upload and View Files
def student_home(request):
    if request.method == "POST":
        topic = request.POST["topic"]
        description = request.POST["description"]
        file = request.FILES.get("file")

        if file:
            UploadedFile.objects.create(user=request.user, topic=topic, description=description, file=file)
            messages.success(request, "File uploaded successfully!")

        return redirect("student_home")

    files = UploadedFile.objects.filter(user=request.user)
    return render(request, "authentication/student_home.html", {"files": files})

# Delete Uploaded File
def delete_file(request, file_id):
    file_obj = get_object_or_404(UploadedFile, id=file_id, user=request.user)

    # Get the file path
    file_path = os.path.join(settings.MEDIA_ROOT, str(file_obj.file))

    # Delete the file from the folder
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete the record from the database
    file_obj.delete()
    messages.success(request, "File deleted successfully!")

    return redirect("student_home")

# Mentor Dashboard: View Student Files
def mentor_home(request):
    if not request.user.is_authenticated:
        return redirect("signin")

    try:
        if request.user.userprofile.role != "mentor":
            return redirect("student_home")
    except AttributeError:
        messages.error(request, "User profile is missing!")
        return redirect("signin")

    files = UploadedFile.objects.all()
    return render(request, "authentication/mentor_home.html", {"files": files})

def update_file_status(request, file_id, action):
    file_obj = get_object_or_404(UploadedFile, id=file_id)

    if action == "approve":
        file_obj.status = "approved"
        messages.success(request, "File approved successfully!")
    elif action == "reject":
        file_obj.status = "rejected"
        messages.error(request, "File rejected!")
    elif action == "delete":
        file_obj.delete()
        messages.success(request, "File deleted successfully!")
        return redirect("mentor_home")

    file_obj.save()
    return redirect("mentor_home")

# Approve Student File
def approve_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    file.status = 'Approved'
    file.save()
    messages.success(request, "File approved successfully!")
    return redirect('mentor_home')


def reject_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    file.status = 'Rejected'
    file.save()
    messages.success(request, "File rejected successfully!")
    return redirect('mentor_home')

# User Signup
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        role = request.POST['role']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username")
            return redirect('student_home')

        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!")
            return redirect('student_home')

        if len(username) > 10:
            messages.error(request, 'Username must be under 10 characters')

        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('student_home') 

        # Create user
        user = User.objects.create_user(username=username, email=email, password=pass1)
        user.first_name = fname
        user.last_name = lname
        user.save()

        # Create UserProfile for role
        UserProfile.objects.create(user=user, role=role)  # Save role in UserProfile

        messages.success(request, "Your account has been created! Please sign in.")
        return redirect('signin')

    return render(request, "authentication/signup.html")

# User Signin
def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            try:
                # Fetch user role from UserProfile model
                user_profile = UserProfile.objects.get(user=user)
                user_role = user_profile.role  

                # Redirect based on role
                if user_role == "student":
                    return redirect("student_home")
                elif user_role == "mentor":
                    return redirect("mentor_home")

            except UserProfile.DoesNotExist:
                messages.error(request, "User profile not found. Please contact support.")
                return redirect("signin")

        else:
            return render(request, "authentication/signin.html", {"error": "Invalid username or password!"})

    return render(request, "authentication/signin.html")

# User Signout
def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect('home')
