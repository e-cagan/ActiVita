from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Sum, Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.contrib.auth import update_session_auth_hash
from django.utils.dateparse import parse_datetime
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from .models import User, Category, Donation, Event, Participation, Notification

# Create your views here
def index(request):
    # Checking if the user is authenticated or not
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    # Fetching all events
    events = Event.objects.all()

    # Creating a list to store event and participation information
    event_list = []

    for event in events:
        # Checking if the user has participated in each event
        is_participated = Participation.objects.filter(user=request.user, event=event).exists()
        
        # Adding the event and participation info to the list
        event_list.append({
            "event": event,
            "is_participated": is_participated
        })

    # Calculating top contributors based on total donation
    contributors = User.objects.annotate(total_donation=Sum('donations__amount')).order_by('-total_donation')[:5]

    # Calculating top participators based on participation count
    participators = User.objects.annotate(participation_count=Count('event_participations')).order_by('-participation_count')[:5]

    return render(request, "app/index.html", {
        "event_list": event_list,
        "contributors": contributors,
        "participators": participators
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "app/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        # Ensure password matches confirmation
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        # Ensure all credentials fulfilled successfully.
        if not username or not email or not password or not confirmation:
            return render(request, "app/register.html", {
                "message": "Please fulfill all the credentials."
            })
        
        if password != confirmation:
            return render(request, "app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "app/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "app/register.html")
    

@login_required
def change_password(request):
    if request.method == "POST":
        # Taking passwords
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirmation = request.POST.get("confirmation")

        # Checking some error cases
        if not old_password or not new_password or not confirmation:
            return render(request, "app/change_password.html", {
                "message": "Please fullfill all the credentials."
            })
        if not request.user.check_password(old_password):
            return render(request, "app/register.html", {
                "message": "Please enter your old password correctly."
            })
        if new_password != confirmation:
            return render(request, "app/register.html", {
                "message": "Please make sure your new password and confirmation match."
            })

        # Trying to change the password
        try:
            request.user.set_password(new_password)
            request.user.save()
            
            # Keeps the user logged in after password change
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your password has been successfully updated.")
            return HttpResponseRedirect(reverse("index"))
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            return HttpResponseRedirect(reverse("change_password"))

    return render(request, "app/change_password.html")
    

@login_required
def create_event(request):
    if request.method == "POST":
        # Taking neccessary credentials
        title = request.POST.get("title")
        description = request.POST.get("description")
        category_id = request.POST.get("categories")
        date = request.POST.get("date")
        location = request.POST.get("location")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        target_donation = request.POST.get("target_donation")

        # Set default value for category
        category = None

        # Get category from db
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                category = None
                messages.error(request, "Selected category does not exist.")

        # Validating date
        try:
            date = parse_datetime(date)
            if not date:
                raise ValueError("Invalid date format.")
            date = timezone.make_aware(date)
        except ValueError as e:
            messages.error(request, "Please enter a valid date.")
            return HttpResponseRedirect(reverse("create_event"))

        # Making sure the target donation is a number
        try:
            target_donation = float(target_donation)
            if target_donation <= 0:
                raise ValueError("Please enter a postitve amount.")
        except ValueError:
            messages.error(request, "Please enter a valid target donation amount.")
            return HttpResponseRedirect(reverse("create_event"))

        # Checking neccessary credentials
        if not title or not description or not location:
            messages.error(request, "All fields are required.")
            return HttpResponseRedirect(reverse("create_event"))

        # Create event and save it
        try:
            event = Event.objects.create(
                title=title,
                description=description,
                date=date,
                location=location,
                latitude=latitude,
                longitude=longitude,
                target_donation=target_donation,
                category=category,
                organizer=request.user
            )
            event.save()
            messages.success(request, "Event has been created successfully.")
            return HttpResponseRedirect(reverse("index"))
        except IntegrityError:
            messages.error(request, "An error occurred. Please try again.")
            return HttpResponseRedirect(reverse("create_event"))

    # Sending categories to the form
    categories = Category.objects.all()
    return render(request, "app/create_event.html", {
        "categories": categories
    })


@login_required
def edit_event(request, event_id):
    # Taking the post that is desired to be edited
    event = get_object_or_404(Event, id=event_id)

    # Ensuring user cannot edit posts except those belonging to themselfs
    if event.organizer != request.user:
        messages.error(request, "Unauthorized")
        return JsonResponse({"error": "Unauthorized"}, status=403)

    if request.method == "POST":
        # Taking credentials that can be editable
        new_title = request.POST.get("new_title")
        new_description = request.POST.get("new_description")
        new_category_id = request.POST.get("new_categories")
        new_date = request.POST.get("new_date")
        new_location = request.POST.get("new_location")
        new_target_donation = request.POST.get("new_target_donation")

        # Verifying category
        if new_category_id:
            try:
                category = Category.objects.get(id=new_category_id)
                event.category = category
            except Category.DoesNotExist:
                messages.error(request, "Selected category does not exist.")
                return JsonResponse({"error": "Selected category does not exist."}, status=400)
        
        # Validating date
        if timezone.is_naive(event.date):
            try:
                event.date = timezone.make_aware(event.date)
                if not event.date:
                    raise ValueError("Invalid date format.")
            except ValueError:
                messages.error(request, "Please enter a valid date.")
                return JsonResponse({"error": "Please enter a valid date."}, status=400)
        
        # Validating target donation
        if new_target_donation:
            try:
                new_target_donation = float(new_target_donation)
                if new_target_donation <= 0:
                    raise ValueError("Please enter a positive amount.")
                event.target_donation = new_target_donation
            except ValueError:
                messages.error(request, "Please enter a valid target donation amount.")
                return JsonResponse({"error": "Please enter a valid target donation amount."}, status=400)
        
        # Save changes
        try:
            event.title = new_title
            event.description = new_description
            event.location = new_location
            event.save()
            messages.success(request, "Event editted successfully.")
            return JsonResponse({"success": True, "message": "Event editted successfully."}, status=200)
        except IntegrityError:
            messages.error(request, "An error occured while updating the event")
            return JsonResponse({"error": "An error occurred while updating the event."}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def delete_event(request, event_id):
    # Taking the event
    event = get_object_or_404(Event, id=event_id)

    # Ensuring user cannot delete posts except those belonging to themselves
    if event.organizer != request.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    if request.method == "POST":
        # Trying to delete event
        try:
            event.delete()
            messages.success(request, "Event deleted successfully.")
            return JsonResponse({"success": True}, status=200)
        except IntegrityError as e:
            messages.error(request, "An error occurred. Please try again.")
            return JsonResponse({"error": str(e)}, status=403)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def event_details(request, event_id):
    # Fetch the event
    event = get_object_or_404(Event, id=event_id)

    # Fetch participators for the event
    participators = Participation.objects.filter(event=event)

    # Checking if the user is authenticated and has participated in the event
    if request.user.is_authenticated:
        is_participated = Participation.objects.filter(user=request.user, event=event).exists()
    else:
        is_participated = False

    # Render the event details template
    return render(request, "app/details.html", {
        "event": event,
        "participators": participators,
        "is_participated": is_participated
    })


@login_required
def participate_event(request, event_id):
    """Allows user to participate events. """
    
    if request.method == "POST":
        # Taking event
        event = get_object_or_404(Event, id=event_id)

        # Ensuring users can't participate their own events
        if event.organizer == request.user:
            messages.error(request, "You can't participate your own event")
            return HttpResponseRedirect(reverse("index"))
        
        # Creating participation object
        Participation.objects.create(user=request.user, event=event)
        messages.success(request, "Participated successfully.")
        
        return HttpResponseRedirect(reverse('index'))
    

@login_required
def departicipate_event(request, event_id):
    """ Allows user to departicipate events. """

    if request.method == "POST":
        # Taking event
        event = get_object_or_404(Event, id=event_id)

        # Ensuring users can't departicipate their own events
        if event.organizer == request.user:
            messages.error(request, "You can't departicipate your own event")
            return HttpResponseRedirect(reverse("index"))
        
        # Deleting participation if exists
        participation = Participation.objects.filter(user=request.user, event=event)
        if participation.exists():
            participation.delete()
        messages.success(request, "Departicipated successfully.")
        
        return HttpResponseRedirect(reverse('index'))


@login_required
def make_donation(request, event_id):
    # Taking the event
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        # Ensuring user can donate other user's events not themselfs.
        if event.organizer == request.user:
            messages.error(request, "You can't donate yourself.")
            return HttpResponseRedirect(reverse("make_donation", args=[event_id]))
        
        # Ensuring amount is not empty
        amount = request.POST.get("amount")
        if not amount:
            messages.error(request, "Please enter your amount.")
            return HttpResponseRedirect(reverse("make_donation", args=[event_id]))

        # Ensuring the amount is positive
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, "Please enter valid amount.")
                return HttpResponseRedirect(reverse("make_donation", args=[event_id]))
        except ValueError:
            messages.error(request, "Please enter valid amount.")
            return HttpResponseRedirect(reverse("make_donation", args=[event_id]))

        # Creating donation
        try:
            Donation.objects.create(
                event=event,
                user=request.user,
                amount=amount
            )
            messages.success(request, "Your donation made successfully.")
        except IntegrityError:
            messages.error(request, "An error occured. Please try again.")

        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "app/make_donation.html", {
        "event": event
    })


@login_required
def profile_page(request):
    # Rendering template
    return render(request, "app/profile.html", {
        "user": request.user
    })


@login_required
def edit_profile(request):
    if request.method == "POST":
        # Taking profile image in files
        new_profile_image = request.FILES.get("new_profile_image")

        # Trying to edit profile image
        try:
            request.user.profile_image = new_profile_image
            request.user.save()
            
            response_data = {
                "status": "success",
                "message": "Profile image editted successfully."
            }
            messages.success(request, "Profile image editted successfully.")
            return JsonResponse(response_data)

        except IntegrityError:
            response_data = {
                "status": "error",
                "message": "An error occurred. Please try again."
            }
            messages.error(request, "An error occured. Please try again.")
            return JsonResponse(response_data, status=500)

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method."
    }, status=400)


@login_required
def delete_profile(request):
    if request.method == "POST":
        # Taking current user
        user = request.user

        # Ensuring user has an image different than default, then changing profile image to default
        if user.profile_image and user.profile_image.url != 'default_profile.jpg':
            user.profile_image.delete(save=False)  # If you want to physically remove the file
            user.profile_image = 'default_profile.jpg'
            user.save()

            # Returning success response
            messages.success(request, "Profile image has been deleted successfully.")
            return JsonResponse({"success": True}, status=200)

        else:
            # If the image is already the default one
            messages.error(request, "Profile image is already the default one.")
            return JsonResponse({"success": False}, status=400)
    
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)


@login_required
def search(request):
    if request.method == "POST":
        # Ensuring query is not empty
        query = request.POST.get("query")
        if not query:
            return JsonResponse({"error": "Please enter your query."}, status=400)

        # Taking the query and check if query is kind of similar with several event fields
        results = list(Event.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(category__name__icontains=query)  # ForeignKey alanında `name` alanına gidiyoruz
        ).values('title', 'description', 'category__name', 'location'))

        return JsonResponse({"results": results})
    
    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def view_notifications(request):
    # Filtering notification
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    
    # Inserting data inside of a notification
    notifications_data = [
        {
            "id": notification.id,
            "message": notification.message,
            "timestamp": notification.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "is_read": notification.is_read
        }
        for notification in notifications
    ]
    
    return JsonResponse({"notifications": notifications_data})


@login_required
def congratulate(request, congratulator_id, user_id):
    if request.method == "POST":
        try:
            user_to_congratulate = User.objects.get(id=user_id)
            congratulator = User.objects.get(id=congratulator_id)
            
            # Burada tebrik mesajı oluşturabilir veya bir Notification kaydı ekleyebilirsiniz
            Notification.objects.create(
                user=user_to_congratulate,
                message=f"{congratulator.username} congratulated you!",
                timestamp=timezone.now(),
            )

            messages.success(request, "Notification sent!")
            return JsonResponse({'success': True ,'message': f"{congratulator.username} congratulated you!"})
        except User.DoesNotExist:
            pass

    
@login_required
def notify_participation(request, event_id, participator_id):
    if request.method == "POST":
        try:
            event = Event.objects.get(id=event_id)
            organizer = event.organizer
            participator = User.objects.get(id=participator_id)
            
            Notification.objects.create(
                user=organizer,
                message=f"{participator.username} has participated in your event '{event.title}'.",
                timestamp=timezone.now(),
            )

            messages.success(request, "Notification sent!")
            return JsonResponse({'success': True, 'message': "Notification sended successfully."})
        except Event.DoesNotExist:
            # Event bulunamazsa yapılacak işlemler
            pass
        except User.DoesNotExist:
            # User bulunamazsa yapılacak işlemler
            pass


@login_required
def mark_as_read(request, notification_id):
    """
    Mark a single notification as read.
    """
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
        # Mark the notification as read
        notification.is_read = True
        notification.save()

        return JsonResponse({"status": "success", "message": "Notification marked as read."})
    
    return JsonResponse({"error": "An error occured. Please try again."})


@login_required
def read_all(request):
    """
    Mark all notifications as read for the current user.
    """
    if request.method == "POST":
        # Update all unread notifications to read for the user
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

        return JsonResponse({"status": "success", "message": "All notifications marked as read."})

    return JsonResponse({"error": "An error occured. Please try again."})
