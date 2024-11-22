from django.conf import settings
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .models import CustomUser,Category,Place,Description,FavoriteHotel
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import logging
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from huggingface_hub import InferenceClient

client = InferenceClient(api_key="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")


def get_amadeus_token():
    """Retrieve access token from Amadeus API"""
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': 'SefT1ACk9xUutkcwZOnjsoL5eep49D5A',  # Replace with your Amadeus API key
        'client_secret': 'V79rIY1nNAzKGrl1'  # Replace with your Amadeus API secret
    }

    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Failed to retrieve access token")

def home(request):
    return render(request, 'index.html')

@login_required(login_url='login')
def aitg(request):
    return render(request, 'aitg.html')

def pricing(request):
    return render(request, 'pricing.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not all([username, name, email, password, confirm_password]):
            messages.error(request, 'Please fill in all fields.')
            return redirect('signup')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken.')
            return redirect('signup')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        user = CustomUser.objects.create_user(username=username, email=email, password=password, name=name)
        messages.success(request, "Your account has been created. You can now login.")
        

        # login_user(request, user)
        # return redirect('home')

    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Check for "Remember Me"

        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return redirect('login')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login_user(request, user)

            # Set session expiry based on "Remember Me" checkbox
            if not remember_me:
                request.session.set_expiry(0)  # Session expires on browser close
            else:
                request.session.set_expiry(1209600)  # Session expires in 2 weeks

            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
    
    return render(request, 'login.html')

def logout_view(request):
    logout_user(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

@login_required(login_url='login')
def settings(request):
    user = request.user

    if request.method == 'POST':
        # Update the user fields with the form data
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.name = request.POST.get('name')
        
        # Save the user data
        user.save()

        # Send success message to user
        messages.success(request, "Your information has been updated successfully.")
        return redirect('settings')  # Redirect to the settings page to avoid re-posting on refresh
    
    # If it's a GET request, render the settings page
    return render(request, 'settings_page.html')

def tr_in_blocks(request):
    categorys = Category.objects.all()
    places = Place.objects.all()
    return render(request, 'tr_in_blocks.html',
    {
     'categorys':categorys,
     'places':places,
     
     })
    
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    places = Place.objects.filter(category=category)
    context = {
        'category': category,
        'places': places,
    }
    return render(request, 'category_detail.html', context)

def place_detail(request, pk):
    place = get_object_or_404(Place, pk=pk)
    descriptions = Description.objects.filter(place=place)
    audio = Description.objects.filter(place=place).values_list('audio', flat=True)
    
    response_text = ""
    if request.method == "POST":
        user_input = request.POST.get("user_input")  # Get input from the HTML form
        
        # Prepare the API payload
        messages = [{"role": "user", "content": user_input}]
        
        # Call Hugging Face Chat API
        try:
            stream = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                messages=messages,
                max_tokens=2000,  # Limit the token count as needed
                stream=False      # Non-streaming mode for simplicity
            )
            response_text = stream.choices[0].message["content"]
        except Exception as e:
            response_text = f"An error occurred: {str(e)}"
    
    
    
    context = {
        'place': place,
        'descriptions': descriptions,
        'audios': audio,
        "response_text": response_text,
    }
    return render(request, 'place_detail.html', context)

@login_required(login_url='login')
def delete_profile_picture(request):
    if request.method == 'POST':
        user = request.user  # Assuming you're using Django's built-in User model
        
        if user.image:  # Check if the image field is not empty
            # user.image.delete()  # Delete the image file
            user.image = 'profile_pics/default.png'  # Set the image field to default.png
            user.save()
            messages.success(request, 'Profile picture deleted successfully.')
        else:
            messages.info(request, 'No profile picture to delete.')

        return redirect('settings')  # Redirect to the settings page or wherever you want

    # Handle GET requests or other cases
    return redirect('settings')

@login_required(login_url='login')
def change_profile_picture(request):
    if request.method == 'POST':
        user = request.user  # Assuming you're using Django's built-in User model
        new_image = request.FILES.get('new_image')  # Assuming the file input name is 'new_image'

        # Check if a new image was uploaded
        if new_image:
            # Delete the current image if it exists
            if user.image:
                # user.image.delete()

                user.image = new_image
            user.save()
            messages.success(request, 'Profile picture updated successfully.')
        else:
            messages.error(request, 'No image selected.')

        return redirect('settings')  # Redirect to the settings page or wherever you want

    # Handle GET requests or other cases
    return redirect('settings')  # Redirect to the settings page if not a POST request

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f"New Message from {name}"
        email_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                email_message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'default@example.com'),  # Use getattr for safety
                ['tibyz._@outlook.com'],
            )
            messages.success(request, "Thank you! Your message has been sent.")
            return redirect('contact')
        except Exception as e:
            logging.error(f"Email sending failed: {e}")  # Log specific error
            messages.error(request, "An error occurred while sending your message. Please try again later.")

    return render(request, 'contact.html')

# @login_required(login_url='login')
# def hotel_booking_page(request):
#     """Render the hotel booking page"""
#     return render(request, 'hotel_booking.html')    

# @login_required(login_url='login')
# def search_hotels(request):
#     """Search for hotels using Amadeus API"""
#     try:
#         access_token = get_amadeus_token()
#         city_code = request.GET.get('city', 'IST')  # Default to Istanbul (IST)
#         check_in_date = request.GET.get('check_in', '2024-11-20')
#         check_out_date = request.GET.get('check_out', '2024-11-25')

#         url = f"https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city?cityCode={city_code}"

#         headers = {
#             "Authorization": f"Bearer {access_token}"
#         }

#         # Make the API request
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()  # Raise an exception for HTTP errors

#         data = response.json()

#         if response.status_code == 200:
#             hotels = data.get('data', [])
#             if isinstance(hotels, list) and hotels:
#                 # Add is_favorite property to each hotel based on user's favorites
#                 user_favorite_hotels = FavoriteHotel.objects.filter(user=request.user).values_list('hotel_id', flat=True)
#                 for hotel in hotels:
#                     hotel['is_favorite'] = hotel['hotelId'] in user_favorite_hotels
#                 return JsonResponse({"hotels": hotels})
#             else:
#                 return JsonResponse({"error": "No hotels found or unexpected data format"}, status=404)
#         else:
#             return JsonResponse({"error": "Failed to fetch hotels", "details": data}, status=500)

#     except requests.exceptions.RequestException as e:
#         # Log the specific error
#         return JsonResponse({"error": "Error while contacting the Amadeus API", "details": str(e)}, status=500)

#     except Exception as e:
#         # Log other exceptions
#         return JsonResponse({"error": "An unexpected error occurred", "details": str(e)}, status=500)
    
# @login_required(login_url='login')
# def add_favorite_hotel(request):
#     """Add a hotel to the user's favorites."""
#     hotel_id = request.POST.get('hotel_id')
#     hotel_name = request.POST.get('hotel_name')
    
#     favorite, created = FavoriteHotel.objects.get_or_create(
#         user=request.user,
#         hotel_id=hotel_id,
#         defaults={'hotel_name': hotel_name}
#     )
    
#     if created:
#         return JsonResponse({"message": "Hotel added to favorites"}, status=201)
#     else:
#         return JsonResponse({"message": "Hotel is already in favorites"}, status=200)

# @login_required(login_url='login')
# def remove_favorite_hotel(request):
#     """Remove a hotel from the user's favorites."""
#     hotel_id = request.POST.get('hotel_id')
#     favorite = FavoriteHotel.objects.filter(user=request.user, hotel_id=hotel_id).first()
    
#     if favorite:
#         favorite.delete()
#         return JsonResponse({"message": "Hotel removed from favorites"}, status=200)
#     else:
#         return JsonResponse({"error": "Hotel not found in favorites"}, status=404)

# @login_required(login_url='login')
# @csrf_exempt
# def toggle_favorite_hotel(request):
#     if request.method == 'POST':
#         user = request.user
#         data = json.loads(request.body)
#         hotel_id = data.get('hotel_id')
#         hotel_name = data.get('hotel_name')

#         # Try to find the favorite hotel entry
#         favorite = FavoriteHotel.objects.filter(user=user, hotel_id=hotel_id).first()

#         if favorite:
#             # If it exists, remove the hotel from favorites
#             favorite.delete()
#             return JsonResponse({"message": "Hotel removed from favorites"})
#         else:
#             # If it does not exist, create a new favorite entry
#             FavoriteHotel.objects.create(user=user, hotel_id=hotel_id, hotel_name=hotel_name)
#             return JsonResponse({"message": "Hotel added to favorites"})

#     return JsonResponse({"error": "Invalid request method"}, status=405)

# @login_required(login_url='login')
# def favorites_page(request):
#     """Render the page with the user's favorite hotels."""
#     user = request.user
#     favorite_hotels = FavoriteHotel.objects.filter(user=user)  # Get all favorites for the logged-in user
    
#     return render(request, 'favorites.html', {'favorite_hotels': favorite_hotels})
     
def nobetci_eczaneler(request):
    return render(request, 'nobetci_eczaneler.html')

     