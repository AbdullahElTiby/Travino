from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def resize_image(image, size=(1600, 900)):
    img = Image.open(image)

    # Ensure the image has a format
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img = img.resize(size, Image.Resampling.LANCZOS)

    thumb_io = BytesIO()
    img.save(thumb_io, format='JPEG', quality=85)  # Default format set to JPEG

    new_image = ContentFile(thumb_io.getvalue(), name=image.name)
    return new_image

class CustomUser(AbstractUser):
    name = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='profile_pics', default='profile_pics/default.png')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, default='defaultpassword')
    nationality = models.CharField(max_length=100, default='Not specified')
    starter_plan = models.BooleanField(default=True)
    premium_plan = models.BooleanField(default=False) 
    all_stars_plan = models.BooleanField(default=False)
    def __str__(self):
        return self.username
    
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField()
    # suggestion = models.TextField(default='suggestions.')
    image = models.ImageField(upload_to='category_pics', default='default.png')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.image:
            self.image = resize_image(self.image)
        super(Category, self).save(*args, **kwargs)

class Place(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='place_pics', default='default.png')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='places')
    location = models.CharField(max_length=100, default='Not located')
    visits = models.IntegerField(default=0)
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.image:
            self.image = resize_image(self.image)
        super(Place, self).save(*args, **kwargs)
    
    
class Description(models.Model):
    name = models.CharField(max_length=100,null=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='descriptions')
    descriptionheader = models.TextField(default='Description')
    text = models.TextField()
    audio = models.FileField(upload_to='audio_files', blank=True, null=True)
    def __str__(self):
        return self.name

    

class FavoriteHotel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_hotels')
    hotel_id = models.CharField(max_length=100)  # Store the hotel ID from the Amadeus API
    hotel_name = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ('user', 'hotel_id')  # Ensure each hotel is only saved once per user

    def __str__(self):
        return f"{self.user.username}'s favorite hotel: {self.hotel_name}"