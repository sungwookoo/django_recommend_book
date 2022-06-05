from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect


# Create your views here.
def home(request):
    # user = request.user.is_authenticated
    # if user:
    #     return redirect('/home')
    # else:
    #     return redirect('/sign-in')
    return redirect('/book')


def get_book(request):
    if request.method == 'GET':
        book_list = []
        for i in range(1, 100001):
            book_list.append(
                {'title': '제목' + str(i), 'author': '저자' + str(i), 'publishar': '출판사' + str(i), 'desc': '내용' + str(i)})

        search_text = request.GET.get('search_text', '')

        if search_text != '':
            if len(search_text) < 2:
                messages.warning(request, "검색어는 최소 2자 이상이여야 합니다.")
                return redirect('/book')
                # page = request.GET.get('page', 1)
                # paginator = Paginator(book_list, 20)
                # try:
                #     book_list = paginator.page(page)
                # except PageNotAnInteger:
                #     book_list = paginator.page(1)
                # except EmptyPage:
                #     book_list = paginator.page(paginator.num_pages)
                # return render(request, 'home.html', {'error': '검색어는 최소 2자 이상이여야 합니다.', 'tweet': book_list})

            result_list = []
            for book in book_list:
                if search_text in book['author'] or search_text in book['title'] or search_text in book['publishar']:
                    result_list.append(book)
            return render(request, 'home.html', {'all_book': result_list})

        else:
            page = request.GET.get('page', 1)
            paginator = Paginator(book_list, 20)
            try:
                book_list = paginator.page(page)
            except PageNotAnInteger:
                book_list = paginator.page(1)
            except EmptyPage:
                book_list = paginator.page(paginator.num_pages)
            return render(request, 'home.html', {'all_book': book_list})
