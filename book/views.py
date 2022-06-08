import gensim.models
from django.contrib import messages
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import MeCab
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import re

# Create your views here.
from book.models import BookData,Like,Review
from django.views.decorators.http import require_POST


def home(request):
    # user = request.user.is_authenticated
    # if user:
    #     return redirect('/home')
    # else:
    #     return redirect('/sign-in')
    return redirect('/book')


def get_book(request):
    if request.method == 'GET':
        # book_list = []
        # for i in range(1, 100001):
        #     book_list.append(
        #         {'title': '제목' + str(i), 'author': '저자' + str(i), 'publisher': '출판사' + str(i), 'desc': '내용' + str(i)}
        #     )

        # df = pd.read_table('book/doc2vec/book.csv', sep=',')
        #
        # for index in range(0, len(df['title'])):
        #     book_list.append(
        #         {'master_seq': df['master_seq'][index], 'title': df['title'][index], 'img': df['img_url'][index],
        #          'description': df['description'][index], 'author': df['author'][index], 'price': df['price'][index],
        #          'pub_date': df['pub_date_2'][index],
        #          'publisher': df['publisher'][index]})

        # df = pd.read_table('book/doc2vec/book.csv', sep=',')
        # mecab = MeCab.Tagger()
        # df['token'] = 0
        # for i in range(0, len(df['title'])):
        #     tmp = mecab.parse(df['title'][i]).split()
        #     # tmp2 = mecab.parse(str(df['description'][i])).split()
        #
        #     # tmp3 = tmp + tmp2
        #
        #     tokens = []
        #     for k in range(0, len(tmp) - 2, 2):
        #         tokens.append(tmp[k])
        #     df['token'][i] = tokens
        # documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(df['token'])]
        # model = Doc2Vec(documents, vector_size=100, window=3, epochs=1, min_count=3, workers=4)
        # model = gensim.models.Doc2Vec.load('book/doc2vec/model.doc2vec')
        # inferred_doc_vec = model.infer_vector(df['token'])
        # print(inferred_doc_vec)
        # most_similar_docs = model.docvecs.most_similar([inferred_doc_vec], topn=10)
        # print(df['title'][100])
        # book_list = []
        # for index, similarity in most_similar_docs:
        #     book_list.append(
        #         {'master_seq': df['master_seq'][index], 'title': df['title'][index], 'img': df['img_url'][index],
        #          'description': df['description'][index], 'author': df['author'][index], 'price': df['price'][index],
        #          'pub_date': df['pub_date_2'][index],
        #          'publisher': df['publisher'][index]})

        book_list = BookData.objects.all()
        search_text = request.GET.get('search_text', '')
        page = request.GET.get('page', 1)

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

            return render(request, 'home.html', {'all_book': result_list, 'search_text': search_text})

        else:
            paginator = Paginator(book_list, 20)
            try:
                book_list = paginator.page(page)
            except PageNotAnInteger:
                book_list = paginator.page(1)
            except EmptyPage:
                book_list = paginator.page(paginator.num_pages)
            return render(request, 'home.html', {'all_book': book_list})


# def detail_book(request, id):
#     # book = (bookDB).objects.get(id=id)
#     book = {'title': '제목' + str(id), 'author': '저자' + str(id), 'publisher': '출판사' + str(id), 'desc': '내용' + str(id)}
#     return render(request, 'detail.html', {'book': book})
def detail_book(request, id):
    book = BookData.objects.get(id=id)
    book_review = Review.objects.filter(book_master_seq=book).order_by('-created_at')
    return render(request,'detail.html',{'book':book,'reviews':book_review})

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

def write_review(request,id):
    if request.method == 'POST':
        review = request.POST.get("my-review","")
        current_Book = BookData.objects.get(id=id)
        RV = Review()
        RV.content = review
        RV.writer = request.user
        RV.book_master_seq = current_Book
        RV.save()

        if RV:
            messages.warning(request, "리뷰 작성 성공")

        return redirect('/book/'+str(current_Book.id))


@login_required
def delete_review(request,id):
    rv = Review.objects.get(id=id)
    page = rv.book_master_seq
    idx = re.sub(r'[^0-9]', '', page)
    rv.delete()
    messages.warning(request,"리뷰를 삭제했습니다")
    return redirect('/book/'+str(idx))

@login_required
def edit_review(request,id):
    rv = Review.objects.get(id=id)
    context = {
        'review':rv,
    }
    return render(request,'edit.html',context)

def update(request,id):
    review = Review.objects.get(id=id)
    page = review.book_master_seq
    idx = re.sub(r'[^0-9]', '', page)
    review.content = request.POST.get('my-review')
    review.save()
    messages.warning(request, "리뷰를 수정했습니다")
    return redirect('/book/'+str(idx))

def likes(request,book_id):
    like = Like.objects.values()

    if request.user.is_authenticated:
        book = BookData.objects.get(id=book_id)
        if len(like) < 1 :
            like = Like(book=book, user=request.user)
            like.save()
            messages.warning(request, "관심 등록 되었습니다")
            return redirect('/book/'+str(book.id))
        else:
            like = Like.objects.filter(
                user = request.user,
                book = book
            )
            like.delete()
            messages.warning(request,"관심 취소 되었습니다")
            return redirect('/book/'+str(book.id))

    return redirect('/sign-in')