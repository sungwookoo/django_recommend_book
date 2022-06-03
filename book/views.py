from django.shortcuts import render, redirect


# Create your views here.
def home(request):
    # user = request.user.is_authenticated
    # if user:
    #     return redirect('/home')
    # else:
    #     return redirect('/sign-in')
    return render(request, 'home.html')


