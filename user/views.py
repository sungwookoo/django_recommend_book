# user/views.py
from django.shortcuts import render, redirect

from book.models import Book, Review
from .models import UserModel
from django.http import HttpResponse
# user/views.py
from django.contrib.auth import get_user_model  # 사용자가 있는지 검사하는 함수
# user/views.py
from django.contrib import auth  # 사용자 auth 기능
from django.contrib.auth.decorators import login_required


def sign_up_view(request):
    if request.method == 'GET':
        user = request.user.is_authenticated  # 로그인 된 사용자가 요청하는지 검사
        if user:  # 로그인이 되어있다면
            return redirect('/')
        else:  # 로그인이 되어있지 않다면
            return render(request, 'signup.html')
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if password != password2:
            # 패스워드가 다르다는 에러가 필요합니다. {'error':'에러문구'} 를 만들어서 전달합니다.
            return render(request, 'signup.html', {'error': '패스워드를 확인 해 주세요!'})
        else:
            if username == '' or password == '':
                # 사용자 저장을 위한 username과 password가 필수라는 것을 얘기 해 줍니다.
                return render(request, 'signup.html', {'error': '사용자 이름과 패스워드는 필수 값 입니다'})

            exist_user = get_user_model().objects.filter(username=username)
            if exist_user:
                return render(request, 'signup.html',
                              {'error': '사용자가 존재합니다.'})  # 사용자가 존재하기 때문에 사용자를 저장하지 않고 회원가입 페이지를 다시 띄움
            else:
                UserModel.objects.create_user(username=username, password=password)
                return redirect('/sign-in')  # 회원가입이 완료되었으므로 로그인 페이지로 이동


# user/views.py

def sign_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', "")
        password = request.POST.get('password', "")

        me = auth.authenticate(request, username=username, password=password)  # 사용자 불러오기
        if me is not None:  # 저장된 사용자의 패스워드와 입력받은 패스워드 비교
            auth.login(request, me)
            return redirect('/')
        else:
            return render(request, 'signin.html', {'error': '유저이름 혹은 패스워드를 확인 해 주세요'})  # 로그인 실패
    elif request.method == 'GET':
        user = request.user.is_authenticated
        if user:
            return redirect('/')
        else:
            return render(request, 'signin.html')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required
def user_follow(request, id):
    me = request.user
    click_user = UserModel.objects.get(id=id)
    if me in click_user.followee.all():
        click_user.followee.remove(request.user)
    else:
        click_user.followee.add(request.user)
    return redirect('/')


# 프로필

# def profile_view(request, id):
#     if id is None:
#         me = request.user
#         books = BookModel.objects.filter(user_id=me.id)
#         reviews = ReviewModel.objects.filter(author=me.id)
#
#     else:
#         books = BookModel.objects.filter(user_id=id)
#         reviews = ReviewModel.objects.filter(author=id)
#
#     return render(request, 'profile.html', {'books':books, 'reviews':reviews})


# def profile_view(request):
#     return render(request, 'profile.html')


def profile_view(request):
    if request.method == 'GET':
        profile_book_list = Book.objects.all()
        profile_img_list = Book.objects.all()
        profile_review_list = Review.objects.all()
        profile_name_list = ['[청하]']
        profile_follow_list = ['132']
        profile_following_list = ['124']

        return render(request, 'profile.html', {'profile_book': profile_book_list,
                                                'profile_review': profile_review_list,
                                                'profile_name': profile_name_list,
                                                'profile_follow': profile_follow_list,
                                                'profile_following': profile_following_list,
                                                'profile_img': profile_img_list
                                                })


    #     id = request.GET['주소']
    #     data = {
    #        'html' : id,
    #     }
    # return render(request, 'profile.html', data)
