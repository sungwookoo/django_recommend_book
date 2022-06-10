import MeCab
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

df = pd.read_table('book/doc2vec/book.csv', sep=',')
# df = pd.DataFrame(list(BookData.objects.all().values()))
mecab = MeCab.Tagger()

df['token'] = 0
for i in range(0, len(df['title'])):
    tmp = mecab.parse(df['title'][i]).split()
    tmp2 = mecab.parse(str(df['description'][i])).split()
    tmp3 = tmp + tmp2
    tokens = []
    for k in range(0, len(tmp3) - 2, 2):
        if '*' not in tmp3[k] and len(tmp3[k]) > 1:
            tokens.append(tmp3[k])

    df['token'][i] = tokens

documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(df['token'])]
model = Doc2Vec(documents, vector_size=100, window=3, epochs=10, min_count=0, workers=4)
model.save('./model.doc2vec')

# inferred_doc_vec = model.infer_vector(df['token'][100])
# most_similar_docs = model.docvecs.most_similar([inferred_doc_vec], topn=10)
#
# book_data=[]
# for index, similarity in most_similar_docs:
#     # print(f"{index}, similarity: {similarity}")
#     book_data.append({'master_seq': df['master_seq'][index], 'title': df['title'][index], 'img': df['img_url'][index],
#                       'description': df['description'][index], 'author': df['author'][index],
#                       'price': df['price'][index], 'pub_date': df['pub_date_2'][index],
#                       'publisher': df['publisher'][index]})
