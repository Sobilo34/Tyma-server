import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import EmailValidator
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model for TYMA administrators."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # Add these to avoid clashes with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="home_user_groups",
        related_query_name="home_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="home_user_permissions",
        related_query_name="home_user",
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Zone(models.Model):
    """Model for TYMA zones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ['name']

    def __str__(self):
        return f"{self.name}"

class Official(models.Model):
    """Model for TYMA Official"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='official_profile', null=True, blank=True)
    official_id = models.CharField(max_length=50, editable=False)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='officials')
    OFFICIAL_TYPE_CHOICES = [
        ('BOARD', 'Board Member'),
        ('STAFF', 'Staff Member'),
        ('VOLUNTEER', 'Volunteer'),
        ('ADVISOR', 'Advisor'),
        ('ADMIN', 'Admin'),
    ]
    POSITION_CHOICES = [
        ('CHAIRMAN', 'Chairman'),
        ('VICE_CHAIRMAN', 'Vice Chairman'),
        ('COORDINATOR', 'Zonal Coordinator'),
    ]
    
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    official_type = models.CharField(max_length=20, choices=OFFICIAL_TYPE_CHOICES)
    bio = models.TextField(blank=True)
    profile_image = models.ForeignKey(
        'TYMAImage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='official_profiles'
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Official"
        verbose_name_plural = "Officials"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.position} - {self.zone.name}"

    def save(self, *args, **kwargs):
        # Ensure the zone name is properly capitalized
        
        self.zone.name = self.zone.name.title()
        self.zone.save()
        super().save(*args, **kwargs)

class NewsCategory(models.Model):
    """Model for news categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "News Category"
        verbose_name_plural = "News Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class NewsEvent(models.Model):
    """Model for TYMA news and events."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    NEWS_TYPE_CHOICES = [
        ('NEWS', 'News Article'),
        ('EVENT', 'Upcoming Event'),
        ('ANNOUNCEMENT', 'Announcement'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    author = models.ForeignKey(Official, on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_news', verbose_name="Author (Official)")
    news_type = models.CharField(max_length=20, choices=NEWS_TYPE_CHOICES)
    categories = models.ManyToManyField('NewsCategory', blank=True)
    short_description = models.CharField(max_length=300)
    content = models.TextField()
    featured_image = models.ForeignKey(
        'TYMAImage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_featured_images'
    )
    is_featured = models.BooleanField(default=False)
    event_date = models.DateTimeField(null=True, blank=True)  # For events
    event_location = models.CharField(max_length=200, blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "News & Event"
        verbose_name_plural = "News & Events"
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        self.views += 1
        self.save()
    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it's empty
            self.slug = slugify(self.title)
            
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while NewsEvent.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)

class TYMAImage(models.Model):
    """Model for storing uploaded images for TYMA"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='tyma_images/')
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    
    # Generic foreign key for linking to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Field to specify the image type/context
    IMAGE_TYPE_CHOICES = [
        ('PROFILE', 'Profile Image'),
        ('FEATURED', 'Featured Image'),
        ('GALLERY', 'Gallery Image'),
        ('THUMBNAIL', 'Thumbnail'),
        ('LOGO', 'Logo'),
        ('OTHER', 'Other'),
    ]
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES, default='OTHER')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "TYMA Image"
        verbose_name_plural = "TYMA Images"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['image_type']),
        ]

    def __str__(self):
        return self.title or f"TYMA Image - {self.id}"

    def get_image_url(self):
        if self.image:
            return self.image.url
        return ""

class ContactSubmission(models.Model):
    """Model for Contact Us form submissions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    SUBJECT_CHOICES = [
        ('GENERAL', 'General Inquiry'),
        ('PROGRAM', 'Program Information'),
        ('VOLUNTEER', 'Volunteer Opportunity'),
        ('DONATION', 'Donation Question'),
        ('FEEDBACK', 'Feedback/Suggestion'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField(db_index=True)  # Add index for faster filtering
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, db_index=True)  # Add index
    message = models.TextField(max_length=5000)  # Add max length constraint
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Add index for sorting
    is_responded = models.BooleanField(default=False, db_index=True)  # Add index for filtering
    response_notes = models.TextField(blank=True, max_length=2000)  # Add max length
    
    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['email', 'subject']),  # Composite index for common queries
            models.Index(fields=['submitted_at', 'is_responded']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"

    def clean(self):
        """Add model-level validation"""
        from django.core.exceptions import ValidationError
        from django.core.validators import validate_email
        
        # Validate name length
        if len(self.name.strip()) < 2:
            raise ValidationError({'name': 'Name must be at least 2 characters long'})
        
        # Validate message length
        if len(self.message.strip()) < 10:
            raise ValidationError({'message': 'Message must be at least 10 characters long'})
        
        # Validate email
        try:
            validate_email(self.email)
        except ValidationError:
            raise ValidationError({'email': 'Enter a valid email address'})


class NewsletterSubscriber(models.Model):
    """Model for Newsletter subscribers"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)  # Ensure uniqueness and indexing
    is_active = models.BooleanField(default=True, db_index=True)  # Add index for filtering
    subscribed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),  # Composite index for lookups
        ]
    
    def __str__(self):
        return f"{self.email} - {'Active' if self.is_active else 'Inactive'}"
    
    def unsubscribe(self):
        """Unsubscribe the user"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()

    def clean(self):
        """Add model-level validation"""
        from django.core.exceptions import ValidationError
        from django.core.validators import validate_email
        
        # Validate email
        try:
            validate_email(self.email)
        except ValidationError:
            raise ValidationError({'email': 'Enter a valid email address'})


# Temporary models to resolve migration conflicts
class Camp(models.Model):
    """Model for Camps"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    total_participants_count = models.PositiveIntegerField(default=0)
    featured_image = models.ForeignKey(
        'TYMAImage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='camp_featured_images'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Camp"
        verbose_name_plural = "Camps"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date})"


class CampZone(models.Model):
    """Model for Camp Zones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name='camp_zones')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='camp_zones')
    location = models.CharField(max_length=200)
    zonal_participants_count = models.PositiveIntegerField(default=0)
    gallery = models.ManyToManyField(TYMAImage, blank=True, related_name='camp_zones')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Camp Zone"
        verbose_name_plural = "Camp Zones"
        unique_together = ('camp', 'zone')

    def __str__(self):
        return f"{self.camp.name} - {self.zone.name}"


