import gensim.models
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import MeCab
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import re
from datetime import datetime

# Create your views here.
from book.models import BookData, Like, Review
from django.views.decorators.http import require_POST
import requests
from bs4 import BeautifulSoup

from user.models import UserModel

df = pd.DataFrame(list(BookData.objects.all().values()))
mecab = MeCab.Tagger()


def loading(request):
    user = request.user.is_authenticated
    if user:
        return render(request, 'loading.html')
    else:
        return redirect('/sign-in')


@csrf_exempt
def loading_proc(request):
    if request.method == 'POST':

        response = {
            'url': 'home'
        }
        return JsonResponse(response)


def home(request):
    user = request.user.is_authenticated
    if user:
        return redirect('/book')
    else:
        return redirect('/sign-in')


def get_recommend_list(request, id):
    user_id = UserModel.objects.get(id=request.user.id)
    selected_book = BookData.objects.get(id=id)
    page = request.GET.get('page', 1)
    profile_book = Like.objects.filter(user_id=user_id)

    model = gensim.models.Doc2Vec.load('book/doc2vec/model.doc2vec')

    # 선택한 도서 토큰화
    tmp = mecab.parse(selected_book.title).split()
    tmp2 = mecab.parse(str(selected_book.description)).split()
    tmp3 = tmp + tmp2
    tokens = []
    for k in range(0, len(tmp3) - 2, 2):
        tokens.append(tmp3[k])

    inferred_doc_vec = model.infer_vector(tokens)
    most_similar_docs = model.docvecs.most_similar([inferred_doc_vec], topn=101)
    recommend_list = []
    for index, similarity in most_similar_docs:

        # 자기 자신은 추천 도서에서 제외
        if df['master_seq'][index] == selected_book.master_seq:
            continue

        recommend_list.append(
            {'id': df['id'][index], 'master_seq': df['master_seq'][index], 'title': df['title'][index], 'img_url': df['img_url'][index],
             'description': df['description'][index], 'author': df['author'][index], 'price': df['price'][index],
             'pub_date_2': df['pub_date_2'][index],
             'publisher': df['publisher'][index]})

    paginator = Paginator(recommend_list, 20)
    try:
        recommend_list = paginator.page(page)
    except PageNotAnInteger:
        recommend_list = paginator.page(1)
    except EmptyPage:
        recommend_list = paginator.page(paginator.num_pages)

    return render(request, 'home.html',
                  {'all_book': recommend_list, 'profile_book': profile_book, 'selected_book': selected_book.title})


def get_book(request):
    if request.method == 'GET':
        user_id = UserModel.objects.get(id=request.user.id)
        book_list = BookData.objects.all()
        total_book = book_list.count()
        search_text = request.GET.get('search_text', '')
        page = request.GET.get('page', 1)
        profile_book = Like.objects.filter(user_id=user_id)

        if search_text != '':
            if len(search_text) < 2:
                messages.warning(request, "검색어는 최소 2자 이상이여야 합니다.")
                return redirect('/book')

            result_list = book_list.filter(
                Q(title__icontains=search_text) |
                Q(author__icontains=search_text) |
                Q(publisher__icontains=search_text)
            )

            # for book in book_list:
            #     if search_text in book['author'] or search_text in book['title'] or search_text in book['publisher']:
            #         result_list.append(book)

            paginator = Paginator(result_list, 20)
            try:
                result_list = paginator.page(page)
            except PageNotAnInteger:
                result_list = paginator.page(1)
            except EmptyPage:
                result_list = paginator.page(paginator.num_pages)

            return render(request, 'home.html',
                          {'all_book': result_list, 'search_text': search_text, 'profile_book': profile_book,
                           'total_book': total_book})

        else:
            paginator = Paginator(book_list, 20)
            try:
                book_list = paginator.page(page)
            except PageNotAnInteger:
                book_list = paginator.page(1)
            except EmptyPage:
                book_list = paginator.page(paginator.num_pages)
            return render(request, 'home.html',
                          {'all_book': book_list, 'profile_book': profile_book, 'total_book': total_book})


# def detail_book(request, id):
#     # book = (bookDB).objects.get(id=id)
#     book = {'title': '제목' + str(id), 'author': '저자' + str(id), 'publisher': '출판사' + str(id), 'desc': '내용' + str(id)}
#     return render(request, 'detail.html', {'book': book})
def detail_book(request, id):
    book = BookData.objects.get(id=id)
    book_review = Review.objects.filter(book_master_seq=book).order_by('-created_at')
    if request.user.is_authenticated:
        like_exist = (Like.objects.filter(user=request.user, book=book)).exists()
        return render(request, 'detail.html', {'book': book, 'reviews': book_review, 'like_exist': like_exist})
    else:
        return render(request, 'detail.html', {'book': book, 'reviews': book_review, 'like_exist': False})


def insert_book_data(request):
    df = pd.read_table('book/doc2vec/book.csv', sep=',')
    count = 0
    for index in range(0, len(df['title'])):
        try:
            book_data = BookData()
            book_data.master_seq = df['master_seq'][index]
            book_data.title = df['title'][index]
            book_data.img_url = df['img_url'][index]
            book_data.description = df['description'][index]
            book_data.author = df['author'][index]
            book_data.price = df['price'][index]
            book_data.pub_date_2 = df['pub_date_2'][index]
            book_data.publisher = df['publisher'][index]
            book_data.save()
        except:
            count += 1
            continue

    print(count)
    return redirect('/book')


def write_review(request, id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            review = request.POST.get("my-review", "")
            current_Book = BookData.objects.get(id=id)
            RV = Review()
            RV.content = review
            RV.writer = request.user
            RV.book_master_seq = current_Book
            RV.save()

            if RV:
                messages.warning(request, "리뷰 작성 성공")

            return redirect('/book/' + str(current_Book.id))
        else:
            messages.warning(request, "로그인이 필요합니다")
            return redirect('sign-in')


@login_required
def delete_review(request, id):
    rv = Review.objects.get(id=id)
    page = rv.book_master_seq.id
    rv.delete()
    messages.warning(request, "리뷰를 삭제했습니다")
    return redirect('/book/' + str(page))


@login_required
def edit_review(request, id):
    rv = Review.objects.get(id=id)
    context = {
        'review': rv,
    }
    return render(request, 'edit.html', context)


def update(request, id):
    review = Review.objects.get(id=id)
    page = review.book_master_seq.id
    review.content = request.POST.get('my-review')
    review.save()
    messages.warning(request, "리뷰를 수정했습니다")
    return redirect('/book/' + str(page))


def likes(request, book_id):
    if request.user.is_authenticated:
        book = BookData.objects.get(id=book_id)
        like_exist = (Like.objects.filter(user=request.user, book=book)).exists()
        if like_exist:
            like = Like.objects.filter(
                user=request.user,
                book=book
            )
            like.delete()
            messages.warning(request, "관심 취소 되었습니다")
            return redirect('/book/' + str(book.id))
        else:
            like = Like(book=book, user=request.user)
            like.save()
            messages.warning(request, "관심 등록 되었습니다")
            return redirect('/book/' + str(book.id))

    return redirect('/sign-in')


def insert_crawling_data(request):
    bestseller = []
    book_number = 0
    page_ii = ['01', '05', '13', '15', '29', '32', '33']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    for k in page_ii:
        data = requests.get(
            f'http://www.kyobobook.co.kr/categoryRenewal/categoryMain.laf?perPage=20&mallGb=KOR&linkClass={k}&menuCode=002',
            headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')
        books = soup.select('#prd_list_type1 > li')

        for i in range(0, 20, 2):
            book_number += 1
            best_image = \
                books[i].select_one('div.thumb_cont > div.info_area > div.cover_wrap > div.cover > a > span > img')[
                    'src']
            best_title = books[i].select_one(
                'div.thumb_cont > div.info_area > div.detail > div.title > a > strong').text
            best_author = books[i].select_one(
                'div.thumb_cont > div.info_area > div.detail > div.pub_info > span.author').text
            best_publication = books[i].select_one(
                'div.thumb_cont > div.info_area > div.detail > div.pub_info > span.publication').text
            best_pub_day = books[i].select_one(
                'div.thumb_cont > div.info_area > div.detail > div.pub_info > span:nth-child(3)').text
            best_pub_day = best_pub_day.strip().replace('.', '-').replace('\t', '').replace('\r', '').replace('\n', '')
            best_price = books[i].select_one(
                'div.thumb_cont > div.info_area > div.detail > div.price > strong.sell_price').text
            best_price = best_price.replace('원', '').replace(',', '')
            best_description = books[i].select_one('div.thumb_cont > div.info_area > div.detail > div.info > span').text
            bestseller.append(
                {'book_number': book_number, 'img': best_image, 'title': best_title, 'author': best_author,
                 'publication': best_publication,
                 'pub_day': best_pub_day, 'price': best_price, 'description': best_description})
            print(book_number)
    print(len(bestseller))
    for index in range(0, len(bestseller)):
        book_data1 = BookData()
        book_data1.master_seq = bestseller[index]['book_number']
        book_data1.title = bestseller[index]['title']
        book_data1.img_url = bestseller[index]['img']
        book_data1.description = bestseller[index]['description']
        book_data1.author = bestseller[index]['author']
        book_data1.price = bestseller[index]['price']
        book_data1.pub_date_2 = datetime.strptime(bestseller[index]['pub_day'][0:10], "%Y-%m-%d")
        book_data1.publisher = bestseller[index]['publication']
        book_data1.save()
        print(bestseller[index]['book_number'])

    return redirect('/book')
