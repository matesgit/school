from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login,logout
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def home(request):
    return render (request,'home.html',{'now': timezone.now()})


def lector_register(request):
    if request.method == 'POST':
        form = LectorRegisterForm(request.POST)
        if form.is_valid():
            lector=form.save()
            request.session['lector_email'] = lector.email
            messages.success(request, "Lector registered successfully.")
            return redirect('lector_dashboard') 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LectorRegisterForm()
    
    return render(request, 'lector_register.html', {'form': form})


# Student Registration View
def student_register(request):
    if request.method=="POST":
        form=StudentRegisterForm(request.POST)
        if form.is_valid():
            student=form.save()
            request.session['student_email'] = student.email     
            messages.success(request, "student registered successfully.")
            return redirect('student_dashboard')
        else:
            messages.error(request,"Please correct the errors below.")
    else:
        form = StudentRegisterForm  
    return render(request,'student_registration.html',{'form':form})


def lector_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            lector = Lector.objects.get(email=email)
        except Lector.DoesNotExist:
            messages.error(request, "Email not found.")
            return render(request, 'lector_login.html')

        if check_password(password, lector.password):
            # Save email and ID in session for identification
            request.session['lector_email'] = lector.email
            request.session['lector_id'] = lector.id  
            messages.success(request, f"Welcome back, {lector.name}!")
            return redirect('lector_dashboard')
        else:
            messages.error(request, "Incorrect password.")
    
    return render(request, 'lector_login.html')



def student_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get("password")

        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            messages.error(request, "Email not found.")
            return render(request, 'student_login.html')

        if check_password(password, student.password):
            # Save email in session for identification
            request.session['student_email'] = student.email
            request.session['student_id'] = student.id 
            messages.success(request, f"Welcome back, {student.name}!")
            return redirect('student_dashboard')  
        else:
            messages.error(request, "Incorrect password.")
    
    return render(request, 'student_login.html')


def logout_view(request):
    logout(request)
    return redirect('dashboard') 


def lector_dashboard(request):
    lector_email = request.session.get('lector_email')

    if not lector_email:
        return redirect('lector-login')

    try:
        lector = Lector.objects.get(email=lector_email)
    except Lector.DoesNotExist:
        messages.error(request, "Lector not found.")
        return redirect('lector-login')

    # Handle profile image upload
    if request.method == 'POST' and request.FILES.get('profile_image'):
        profile_image = request.FILES['profile_image']
        lector.profile_image = profile_image
        lector.save()
        messages.success(request, "Profile image updated successfully.")
        return redirect('lector_dashboard')

    return render(request, 'lector_dashboard.html', {
        'lector': lector,
      
    })
    
def student_dashboard(request):
    student_email=request.session.get('student_email')
    
    if not student_email:
        return redirect('student-login')
    
    try:
        student=Student.objects.get(email=student_email)
    except Student.DoesNotExist:
        messages.error(request,' student not found.')
        return redirect ('student-login')
    
    # Handle profile image upload
    if request.method == 'POST' and request.FILES.get('profile_image'):
        student.profile_image = request.FILES['profile_image']
        student.save()
        messages.success(request, "Profile image updated successfully!")
        return redirect('student_dashboard')  
    
    groups = student.groups.all()

    return render(request, 'student_dashboard.html', {'student': student, 'groups': groups})
   


def manage_students(request):
    lector_email = request.session.get('lector_email')

    if not lector_email:
        return redirect('lector-login')

    try:
        lector = Lector.objects.get(email=lector_email)
    except Lector.DoesNotExist:
        messages.error(request, "Lector not found.")
        return redirect('lector-login')

    if request.method == 'POST':
        form = AddStudentForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            lector.students.add(student)
            messages.success(request, f"{student.name} has been added to your student list.")
            return redirect('manage_students')
    else:
        form = AddStudentForm()

    student_list = lector.students.all()
    return render(request, 'manage_students.html', {
        'form': form,
        'student_list': student_list,
        'name': lector.name
    })
from django.shortcuts import get_object_or_404


def remove_student(request, student_id):
    lector_email = request.session.get('lector_email')
    if not lector_email:
        return redirect('lector-login')

    lector = get_object_or_404(Lector, email=lector_email)
    student = get_object_or_404(Student, id=student_id)

    # Remove the student from this lector’s list (not from database)
    lector.students.remove(student)
    messages.success(request, f"{student.name} {student.surname} was removed from your list.")
    return redirect('manage_students')
    
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------

def manage_groups(request):
    lector_email = request.session.get('lector_email')
    if not lector_email:
        return redirect('lector-login')

    lector = get_object_or_404(Lector, email=lector_email)
    students = lector.students.all()

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.lector = lector 
            group.save()

            # Get selected students from the form and add them to the group
            selected_students = request.POST.getlist('students') 
            for student_id in selected_students:
                student = Student.objects.get(id=student_id)
                group.students.add(student)  

            form.save_m2m()  # Ensure many-to-many relationships are saved
            messages.success(request, f"Group '{group.name}' created.")
            return redirect('manage_groups')
    else:
        form = GroupForm()

    groups = Group.objects.filter(lector=lector)
    return render(request, 'manage_groups.html', {
        'form': form,
        'groups': groups,
        'lector': lector,
        'students': students,  # Pass the filtered students here
    })

def add_student_to_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    lector_email = request.session.get('lector_email')

    if not lector_email or group.lector.email != lector_email:
        return redirect('lector-login')

    lector = get_object_or_404(Lector, email=lector_email)

    # Exclude students already in the group
    available_students = lector.students.exclude(id__in=group.students.values_list('id', flat=True))

    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        for sid in student_ids:
            student = get_object_or_404(Student, id=sid)
            group.students.add(student)
        messages.success(request, f"Added {len(student_ids)} student(s) to {group.name}.")
        return redirect('manage_groups')

    return render(request, 'add_student_to_group.html', {
        'group': group,
        'available_students': available_students,
    })



def remove_student_from_group(request, group_id, student_id):
    lector_email = request.session.get('lector_email')
    if not lector_email:
        return redirect('lector-login')

    group = get_object_or_404(Group, id=group_id)
    student = get_object_or_404(Student, id=student_id)
    group.students.remove(student)
    messages.success(request, f"{student.name} removed from {group.name}.")
    return redirect('manage_groups')


def delete_group(request, group_id):
    lector_email = request.session.get('lector_email')
    if not lector_email:
        return redirect('lector-login')

    group = get_object_or_404(Group, id=group_id)
    group.delete()
    messages.success(request, "Group deleted successfully.")
    return redirect('manage_groups')


# def group_page(request, group_id):
#     group = get_object_or_404(Group, id=group_id)
#     students = group.students.all()
#     posts = Post.objects.filter(group=group).order_by('-created_at')

#     lector_email = request.session.get('lector_email')
#     lector_id = request.session.get('lector_id')
#     student_email = request.session.get('student_email')
#     student_id = request.session.get('student_id')

#     # Always get lector from the group for display purposes
#     group_lector = group.lector

#     # Validate access
#     if lector_email:
#         if group_lector.email != lector_email:
#             return redirect('lector-login')
#     elif student_email:
#         if not students.filter(email=student_email).exists():
#             return redirect('student-login')
#     else:
#         return redirect('login')

#     # Define lector (logged-in lector) for posting if applicable
#     lector = None
#     if lector_email and lector_id:
#         lector = get_object_or_404(Lector, id=lector_id)

#     if request.method == 'POST':
#         if lector:
#             content = request.POST.get('group_post', '').strip()
#             image = request.FILES.get('image')
#             file = request.FILES.get('file')

#             if content or image or file:
#                 Post.objects.create(
#                     group=group,
#                     author=lector,
#                     content=content,
#                     image=image,
#                     file=file
#                 )
#                 return redirect('group_page', group_id=group.id)
#             else:
#                 messages.error(request, "You must write something or upload an image/file.")
#         else:
#             messages.error(request, "Only lectors can post messages.")

#     return render(request, 'group_page.html', {
#         'group': group,
#         'students': students,
#         'posts': posts,
#         'lector_email': lector_email,
#         'student_email': student_email,
#         'lector': lector,           # logged-in lector (for posting)
#         'group_lector': group_lector,  # lector of the group (for display)
#     })

def lector_group_page(request, group_id):
    lector_email = request.session.get('lector_email')
    if not lector_email:
        return redirect('lector-login')

    try:
        lector = Lector.objects.get(email=lector_email)
    except Lector.DoesNotExist:
        return redirect('lector-login')

    group = get_object_or_404(Group, id=group_id)

    if group.lector.id != lector.id:
        return HttpResponseForbidden("You are not the lector of this group.")

    posts = Post.objects.filter(group=group).order_by('-created_at')

    if request.method == 'POST':
        content = request.POST.get('group_post', '').strip()
        image = request.FILES.get('image')
        file = request.FILES.get('file')

        if content or image or file:
            Post.objects.create(
                group=group,
                author=lector,
                content=content,
                image=image,
                file=file
            )
            return redirect('lector_group_page', group_id=group.id)
        else:
            messages.error(request, "You must write something or upload an image/file.")
    
    return render(request, 'group_page.html', {
        'group': group,
        'posts': posts,
        'user_role': 'lector',
        'lector': lector,
        'user': lector,
    })

def student_group_page(request, group_id):
    student_email = request.session.get('student_email')
    if not student_email:
        return redirect('student-login')

    try:
        student = Student.objects.get(email=student_email)
    except Student.DoesNotExist:
        return redirect('student-login')

    group = get_object_or_404(Group, id=group_id)

    if not group.students.filter(id=student.id).exists():
        return HttpResponseForbidden("You are not a member of this group.")

    posts = Post.objects.filter(group=group).order_by('-created_at')
    current_student = Student.objects.get(email=request.session.get('student_email'))
     
    lector = group.lector
    
    return render(request, 'group_page.html', {
        'group': group,
        'posts': posts,
        'user_role': 'student',
        'student': student,
        'current_student': current_student,
        'lector':lector,
        'user': student,  # Add this
    })


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    lector_email = request.session.get('lector_email')
    if not lector_email or post.author.email != lector_email:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('lector_group_page', group_id=post.group.id)

    return redirect('lector_group_page', group_id=post.group.id)



from django.utils.timezone import localtime

def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('comment_content')
        image = request.FILES.get('comment_image')

        if not content:
            return JsonResponse({'success': False, 'error': 'Empty content'})

        if 'student_id' in request.session:
            author = get_object_or_404(Student, id=request.session['student_id'])
        elif 'lector_id' in request.session:
            author = get_object_or_404(Lector, id=request.session['lector_id'])
        else:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})

        comment = Comment.objects.create(
            post=post,
            content=content,
            image=image,
            author_content_type=ContentType.objects.get_for_model(author),
            author_object_id=author.id
        )

        return JsonResponse({
            'success': True,
            'author_name': f'{author.name} {author.surname}',
            'author_image': author.profile_image.url if author.profile_image else '/static/images/default-profile.png',
            'content': comment.content,
            'image': comment.image.url if comment.image else '',
            'created_at': localtime(comment.created_at).strftime('%b %d, %Y %H:%M'),
            'comment_id': comment.id
        })



def add_point(request, group_id):
    lector_email = request.session.get('lector_email')
    if not lector_email:
        messages.error(request, "You must be logged in as a lector.")
        return redirect('lector-login')

    try:
        lector = Lector.objects.get(email=lector_email)
    except Lector.DoesNotExist:
        messages.error(request, "Lector not found.")
        return redirect('lector-login')

    group = get_object_or_404(Group, id=group_id)

    # Only students in the group
    form = PointForm(request.POST or None)
    form.fields['student'].queryset = group.students.all()

    if request.method == 'POST' and form.is_valid():
        point = form.save(commit=False)
        point.group = group
        point.lector = lector
        point.save()
        messages.success(request, "Point added successfully.")
        
        

    return render(request, 'add_point.html', {
        'form': form,
        'group': group,
    })


from django.db.models import Sum

def view_points(request, group_id):
    student_email = request.session.get('student_email')
    if not student_email:
        messages.error(request, "You must be logged in as a student.")
        return redirect('student-login') 

    try:
        student = Student.objects.get(email=student_email)
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('student-login')

    group = get_object_or_404(Group, id=group_id)

    points = Point.objects.filter(group=group, student=student).order_by('-created_at')

    total_points = points.aggregate(total=Sum('value'))['total'] or 0  # sum points here

    return render(request, 'points.html', {
        'group': group,
        'points': points,
        'total_points': total_points,  # pass total points here
    })



def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post

    user = None

    if 'student_id' in request.session:
        user = get_object_or_404(Student, id=request.session['student_id'])
    elif 'lector_id' in request.session:
        user = get_object_or_404(Lector, id=request.session['lector_id'])
    else:
        return redirect('lector-login')
#           i found out problem with this prnts <3 
    print("== Deletion attempt ==")
    print("User:", user)
    print("User ContentType:", ContentType.objects.get_for_model(user))
    print("Comment Author ContentType:", comment.author_content_type)
    print("Comment Author Object ID:", comment.author_object_id)
    print("Post Author ContentType:", post.author_content_type)
    print("Post Author Object ID:", post.author_object_id)

    is_comment_author = (
        comment.author_content_type == ContentType.objects.get_for_model(user) and
        comment.author_object_id == user.id
    )

    is_post_author = (
        post.author_content_type == ContentType.objects.get_for_model(user) and
        post.author_object_id == user.id
    )

    print("is_comment_author:", is_comment_author)
    print("is_post_author:", is_post_author)

    if is_comment_author or is_post_author:
        comment.delete()
    else:
        return HttpResponseForbidden("You are not allowed to delete this comment.")

    return redirect(request.META.get('HTTP_REFERER'))


def private_chat(request, receiver_type, receiver_id):
    sender_type = None
    sender_id = None
    sender_name = None

    # Identify the logged-in sender
    if request.session.get('lector_id'):
        sender_type = 'lector'
        sender_id = str(request.session['lector_id'])
        sender = get_object_or_404(Lector, id=sender_id)
    elif request.session.get('student_id'):
        sender_type = 'student'
        sender_id = str(request.session['student_id'])
        sender = get_object_or_404(Student, id=sender_id)
    else:
        return render(request, "privatechat.html", {
            "error": "Sender info missing. Please log in."
        })

    # Get receiver instance
    if receiver_type == 'lector':
        receiver = get_object_or_404(Lector, id=receiver_id)
    elif receiver_type == 'student':
        receiver = get_object_or_404(Student, id=receiver_id)
    else:
        return render(request, "privatechat.html", {
            "error": "Invalid receiver type."
        })

    # Load past messages between these two users
    messages = PrivateChat.objects.filter(
        sender_content_type=ContentType.objects.get_for_model(sender.__class__),
        sender_object_id=sender.id,
        receiver_content_type=ContentType.objects.get_for_model(receiver.__class__),
        receiver_object_id=receiver.id
    ) | PrivateChat.objects.filter(
        sender_content_type=ContentType.objects.get_for_model(receiver.__class__),
        sender_object_id=receiver.id,
        receiver_content_type=ContentType.objects.get_for_model(sender.__class__),
        receiver_object_id=sender.id
    )

    messages = messages.order_by("timestamp")

    formatted_messages = [{
        "id": msg.id,  
        "message": msg.message,
        "sender_name": str(msg.sender),
        "sender_type": msg.sender_content_type.model,
        "sender_id": msg.sender_object_id,
        "timestamp": msg.timestamp.isoformat(),
    } for msg in messages]

    return render(request, "privatechat.html", {
        "sender_type": sender_type,
        "sender_id": sender_id,
        "receiver_type": receiver_type,
        "receiver_id": receiver.id,
        "receiver_name": str(receiver),
        "past_messages": formatted_messages,
    })


def chat_room(request, room_name):
    sender_type = None
    sender_id = None
    sender_name = None

    # Determine sender info from session
    if request.session.get('lector_id'):
        sender_type = 'lector'
        sender_id = str(request.session['lector_id'])
        sender_name = str(get_object_or_404(Lector, id=sender_id))
    elif request.session.get('student_id'):
        sender_type = 'student'
        sender_id = str(request.session['student_id'])
        sender_name = str(get_object_or_404(Student, id=sender_id))
    else:
        return render(request, "groupchat.html", {
            "room_name": room_name,
            "error": "Sender info missing. Please log in properly."
        })

    group = get_object_or_404(Group, pk=room_name)
    messages = GroupChatMessage.objects.filter(group=group).order_by("timestamp")

    formatted_messages = []
    for msg in messages:
        sender = msg.sender_content_type.get_object_for_this_type(id=msg.sender_object_id)
        formatted_messages.append({
            "message": msg.message,
            "sender_id": str(sender.id),
            "sender_type": msg.sender_content_type.model,
            "sender_name": str(sender),
            "timestamp": msg.timestamp.isoformat(),
            # Add file info (if any)
            "file_url": msg.file_url if hasattr(msg, 'file_url') else None,
            "filename": msg.filename if hasattr(msg, 'filename') else None,
        })

    return render(request, "groupchat.html", {
        "room_name": room_name,
        "sender_type": sender_type,
        "sender_id": sender_id,
        "sender_name": sender_name,
        "past_messages": formatted_messages,
    })


def student_detail(request, student_id):
    student = Student.objects.get(id=student_id)
    groups = student.groups.all()  # or however you access groups
    groups_with_lectors_and_points = []

    for group in groups:
        lector = group.lector  # adjust if field name is different
        points_for_group = Point.objects.filter(student=student, group=group)
        total_points = points_for_group.aggregate(total=Sum('value'))['total'] or 0  # add this

        groups_with_lectors_and_points.append({
            'group': group,
            'lector': lector,
            'points': points_for_group,
            'total_points': total_points,  # include total in context
        })

    context = {
        'student': student,
        'groups_with_lectors_and_points': groups_with_lectors_and_points,
    }
    return render(request, 'student_detail.html', context)


                     ################## n8n ai agent#####
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import requests
def chat_page(request):
    return render(request, 'aichat.html')

# Handles sending message to AI agent webhook and returning reply
@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            print(f"User Message: {user_message}")
        except json.JSONDecodeError:
            return JsonResponse({'reply': 'Invalid request format'}, status=400)

        webhook_url = 'https://automation-test-123.app.n8n.cloud/webhook/50ab2956-3a9f-44a9-8f0c-422c97a15323'

        try:
            response = requests.post(
                webhook_url,
                json={
                    'message': user_message,
                    'sessionId': 'user123'
                },
                timeout=30
            )

            print(f"\n--- Webhook Response ---")
            print(f"Status Code: {response.status_code}")
            print(f"Content-Length: {response.headers.get('Content-Length', 'Not specified')}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
            print(f"Raw Response Text: '{response.text}'")
            print(f"Response Text Length: {len(response.text)}")
            print(f"Response Text Stripped: '{response.text.strip()}'")

            if response.status_code == 200:
                # Check if response has content
                if not response.text or response.text.strip() == '':
                    ai_reply = "AI response is empty. Workflow may not be configured to return data."
                    print("ERROR: Empty response from n8n webhook")
                else:
                    try:
                        json_data = response.json()
                        print(f"Parsed JSON: {json_data}")
                        ai_reply = json_data.get('output', 'No output field in response')
                        print(f"AI Reply: {ai_reply}")
                    except json.JSONDecodeError as e:
                        ai_reply = f"Invalid JSON in response: {response.text}"
                        print(f"JSON Parse Error: {e}")
            else:
                ai_reply = f"Error: Status {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            ai_reply = f"Error contacting AI: {str(e)}"
            print(f"Request Exception: {e}")

        return JsonResponse({'reply': ai_reply})

    return JsonResponse({'error': 'Only POST allowed'}, status=405)

    #############################################



from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Private Chat Message Functions
require_http_methods(["POST"])
def delete_private_message(request, message_id):
    try:
        message = get_object_or_404(PrivateChat, id=message_id)

        if request.session.get('lector_id'):
            current_user = get_object_or_404(Lector, id=request.session['lector_id'])
        elif request.session.get('student_id'):
            current_user = get_object_or_404(Student, id=request.session['student_id'])
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        sender_content_type = ContentType.objects.get_for_model(current_user.__class__)
        if message.sender_content_type != sender_content_type or str(message.sender_object_id) != str(current_user.id):
            return JsonResponse({'error': 'You can only delete your own messages'}, status=403)

        message_id = message.id

        # Prepare group name before deleting
        participants = sorted([(message.sender_content_type.model, str(message.sender_object_id)),
                               (message.receiver_content_type.model, str(message.receiver_object_id))])
        group_name = f'privatechat_{participants[0][0]}_{participants[0][1]}_{participants[1][0]}_{participants[1][1]}'

        message.delete()

        # Notify WebSocket group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'message_deleted',
                'message_id': message_id
            }
        )

        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def update_private_message(request, message_id):
    try:
        message = get_object_or_404(PrivateChat, id=message_id)
        
        if request.session.get('lector_id'):
            current_user = get_object_or_404(Lector, id=request.session['lector_id'])
        elif request.session.get('student_id'):
            current_user = get_object_or_404(Student, id=request.session['student_id'])
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        sender_content_type = ContentType.objects.get_for_model(current_user.__class__)
        if message.sender_content_type != sender_content_type or str(message.sender_object_id) != str(current_user.id):
            return JsonResponse({'error': 'You can only update your own messages'}, status=403)

        new_message = json.loads(request.body).get('message', '').strip()
        if not new_message:
            return JsonResponse({'error': 'Message content cannot be empty'}, status=400)

        message.message = new_message
        message.save()

        # Broadcast to WebSocket
        participants = sorted([(message.sender_content_type.model, str(message.sender_object_id)),
                               (message.receiver_content_type.model, str(message.receiver_object_id))])
        group_name = f'privatechat_{participants[0][0]}_{participants[0][1]}_{participants[1][0]}_{participants[1][1]}'

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'message_updated',
                'message_id': message.id,
                'new_message': new_message,
                'timestamp': message.timestamp.isoformat()
            }
        )

        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Group Chat Message Functions
@require_http_methods(["POST"])
def delete_group_message(request, message_id):
    """Delete a group chat message"""
    try:
        message = get_object_or_404(GroupChatMessage, id=message_id)
        
        # Get current user info
        current_user = None
        current_user_type = None
        
        if request.session.get('lector_id'):
            current_user = get_object_or_404(Lector, id=request.session['lector_id'])
            current_user_type = 'lector'
        elif request.session.get('student_id'):
            current_user = get_object_or_404(Student, id=request.session['student_id'])
            current_user_type = 'student'
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Check if current user is the sender of the message
        sender_content_type = ContentType.objects.get_for_model(current_user.__class__)
        if (message.sender_content_type != sender_content_type or 
            str(message.sender_object_id) != str(current_user.id)):
            return JsonResponse({'error': 'You can only delete your own messages'}, status=403)
        
        message.delete()
        return JsonResponse({'success': True, 'message': 'Message deleted successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def update_group_message(request, message_id):
    """Update a group chat message"""
    try:
        message = get_object_or_404(GroupChatMessage, id=message_id)
        
        # Get current user info
        current_user = None
        current_user_type = None
        
        if request.session.get('lector_id'):
            current_user = get_object_or_404(Lector, id=request.session['lector_id'])
            current_user_type = 'lector'
        elif request.session.get('student_id'):
            current_user = get_object_or_404(Student, id=request.session['student_id'])
            current_user_type = 'student'
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Check if current user is the sender of the message
        sender_content_type = ContentType.objects.get_for_model(current_user.__class__)
        if (message.sender_content_type != sender_content_type or 
            str(message.sender_object_id) != str(current_user.id)):
            return JsonResponse({'error': 'You can only update your own messages'}, status=403)
        
        # Get new message content
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            new_message = data.get('message', '').strip()
        else:
            new_message = request.POST.get('message', '').strip()
        
        if not new_message:
            return JsonResponse({'error': 'Message content cannot be empty'}, status=400)
        
        message.message = new_message
        message.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Message updated successfully',
            'updated_message': new_message,
            'timestamp': message.timestamp.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Optional: Bulk delete function for private messages
@require_http_methods(["POST"])
def bulk_delete_private_messages(request):
    """Delete multiple private messages"""
    try:
        # Get current user info
        current_user = None
        if request.session.get('lector_id'):
            current_user = get_object_or_404(Lector, id=request.session['lector_id'])
        elif request.session.get('student_id'):
            current_user = get_object_or_404(Student, id=request.session['student_id'])
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Get message IDs
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            message_ids = data.get('message_ids', [])
        else:
            message_ids = request.POST.getlist('message_ids')
        
        if not message_ids:
            return JsonResponse({'error': 'No messages selected'}, status=400)
        
        # Get messages and verify ownership
        sender_content_type = ContentType.objects.get_for_model(current_user.__class__)
        messages = PrivateChat.objects.filter(
            id__in=message_ids,
            sender_content_type=sender_content_type,
            sender_object_id=current_user.id
        )
        
        deleted_count = messages.count()
        messages.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} messages deleted successfully',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Optional: Bulk delete function for group messages
@require_http_methods(["POST"])
def bulk_delete_group_messages(request):
    """Delete multiple group messages"""
    try:
        # Get current user info
        current_user = None
        if request.session.get('lector_id'):
            current_user = get_object_or_404(Lector, id=request.session['lector_id'])
        elif request.session.get('student_id'):
            current_user = get_object_or_404(Student, id=request.session['student_id'])
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Get message IDs
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            message_ids = data.get('message_ids', [])
        else:
            message_ids = request.POST.getlist('message_ids')
        
        if not message_ids:
            return JsonResponse({'error': 'No messages selected'}, status=400)
        
        # Get messages and verify ownership
        sender_content_type = ContentType.objects.get_for_model(current_user.__class__)
        messages = GroupChatMessage.objects.filter(
            id__in=message_ids,
            sender_content_type=sender_content_type,
            sender_object_id=current_user.id
        )
        
        deleted_count = messages.count()
        messages.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} messages deleted successfully',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)