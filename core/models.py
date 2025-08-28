from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class Lector(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    lector_id = models.CharField(max_length=100, unique=True)  # Unique ID for Lector
    password=models.CharField(max_length=150,null=True, blank=True)
    students = models.ManyToManyField('Student', related_name='lectors', blank=True)
    profile_image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)  # Hash the password

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)  # Check if passwords match    
    
    def __str__(self):
        return f"{self.name} {self.surname}"

class Student(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    student_id = models.CharField(max_length=100, unique=True)  # Unique ID for Student
    password=models.CharField(max_length=100,null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)  # Hash the password

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)  # Check if passwords match    
    
    def __str__(self):
        return f"{self.name} {self.surname}"
    
class Group(models.Model):
    name = models.CharField(max_length=100)
    lector = models.ForeignKey(Lector, on_delete=models.CASCADE, related_name='groups')
    students = models.ManyToManyField(Student, blank=True, related_name='groups')

    def __str__(self):
        return self.name
#--------------------------------
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Post(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='posts')

    # Generic relation for author (Student or Lector)
    author_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    author_object_id = models.PositiveIntegerField()
    author = GenericForeignKey('author_content_type', 'author_object_id')

    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    file = models.FileField(upload_to='post_files/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.author} in {self.group.name}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    author_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    author_object_id = models.PositiveIntegerField()
    author = GenericForeignKey('author_content_type', 'author_object_id')

    content = models.TextField()
    image = models.ImageField(upload_to='comment_images/', null=True, blank=True)
    file = models.FileField(upload_to='comment_files/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on post {self.post.id}"

class GroupChatMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='chat_messages')
    sender_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,blank=True,null=True)
    sender_object_id = models.PositiveIntegerField(blank=True,null=True)
    sender = GenericForeignKey('sender_content_type', 'sender_object_id')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.sender} to {self.group.name}: {self.message[:30]}"

class PrivateChat(models.Model):
    sender_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='sent_messages', blank=True, null=True)
    sender_object_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_content_type', 'sender_object_id')

    receiver_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='received_messages', blank=True, null=True)
    receiver_object_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_content_type', 'receiver_object_id')

    message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    #need to updated or change this lines
    read = models.BooleanField(default=False)  # Read receipt
    file_url = models.URLField(blank=True, null=True)  # Optional file sharing

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.message[:30]}"


POINT_TYPE_CHOICES = [
    ('homework', 'Homework'),
    ('participation', 'Participation'),
    ('quiz', 'Quiz'),
    ('exam', 'Exam'),
    ('project', 'Project'),
]

class Point(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    lector = models.ForeignKey('Lector', on_delete=models.CASCADE)
    value = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    point_type = models.CharField(
        max_length=20,
        choices=POINT_TYPE_CHOICES,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.student.name} - {self.value} points"

  