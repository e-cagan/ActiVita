from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    profile_image = models.ImageField(upload_to='img/', default='img/default_profile.jpg')
    event_participations = models.ManyToManyField('Event', through='Participation')

    def total_participations(self):
        return self.event_participations.count()
    
    def total_donations(self):
        return Donation.objects.filter(user=self).aggregate(total=models.Sum('amount'))['total'] or 0


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    date = models.DateTimeField(null=False, blank=False)
    location = models.CharField(max_length=255, null=False, blank=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=False, blank=False, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=False, blank=False, default=0)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    participants = models.ManyToManyField(User, related_name='participated_events', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    target_donation = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    total_donations = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)

    def __str__(self):
        return f"{self.title} by {self.organizer.username} ID: {self.id}"

    def donation_progress(self):
        """ Calculates the donation progress by percentage. """
        if self.target_donation and self.total_donations:
            return round((self.total_donations / self.target_donation) * 100, 2)
        return 0
    

class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='user_participations')
    is_participated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} in {self.event.title}"


class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ Updates the total donation when donation is saved. """
        super().save(*args, **kwargs)
        self.event.total_donations += self.amount
        self.event.save()

    def __str__(self):
        return f"{self.user.username} donated {self.amount} to {self.event.title}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}"
