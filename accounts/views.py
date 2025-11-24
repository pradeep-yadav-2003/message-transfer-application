from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()   # IMPORTANT

@api_view(["POST"])
def register(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email & password required"}, status=400)

    # Check duplicate
    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=400)

    # Generate unique username from email  
    base_username = email.split("@")[0]
    username = base_username
    counter = 1

    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    # CREATE USER
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    # Generate Token
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "status": "success",
        "token": token.key,
        "user": {"id": user.id, "email": user.email}
    }, status=201)


@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid email or password"}, status=400)

    user = authenticate(username=user.username, password=password)

    if not user:
        return Response({"error": "Invalid email or password"}, status=400)

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "status": "success",
        "token": token.key,
        "user": {"id": user.id, "email": user.email}
    })
