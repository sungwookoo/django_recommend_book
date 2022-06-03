from django.shortcuts import render

# Create your views here.
def profile_view(request):
    if request.method == 'GET':
        return render(request, 'profile.html')