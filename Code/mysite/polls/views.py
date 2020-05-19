# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Choice, Question
from django.shortcuts import get_object_or_404,render
from django.views import generic
import json
import numpy as np
import gensim
import csv
import smart_open

from django.urls import reverse

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    
def buildWordsTree(root_word, model):
    root = {'name': root_word, 'children': []}
    topn_words = 10
    root_simiWords = list(map(lambda X: X[0], model.wv.most_similar(root_word, topn=topn_words)))
    for i in range(len(root_simiWords)):
        son_simiWords = list(map(lambda X: X[0], model.wv.most_similar(root_simiWords[i], topn=topn_words)))
        son = {}
        son['name']=root_simiWords[i]
        son['children'] = []
        # for j in range(len(son_simiWords)):
        for j in range(7):
            # grandson_simiWords = list(map(lambda X: X[0], model.wv.most_similar(son_simiWords[j], topn=topn_words)))
            son['children'].append({'name': son_simiWords[j]})
        root['children'].append(son)
    return root

def dashboard(request):
    with smart_open.open('/Users/hiphone/Downloads/ads-100,000.csv') as f:
        ads_csv = csv.reader(f, delimiter = ',')
        headers = next(ads_csv)
        documents = list(map(lambda x: x[1], ads_csv))

    model = gensim.models.doc2vec.Doc2Vec.load('/Users/hiphone/fb_10w_d100_e10.d2v')
    indexOfSelectedDoc = 30858
    topn_doc = 10
    similar_docs = model.docvecs.most_similar(indexOfSelectedDoc, topn=topn_doc)
    vectors = []
    docs = {}
    vectors.append(model.docvecs[indexOfSelectedDoc].tolist())
    doc = documents[indexOfSelectedDoc].replace('\'', ' ')
    docs[str(indexOfSelectedDoc)] = doc
    for i in range(topn_doc):
        vectors.append(model.docvecs[similar_docs[i][0]].tolist())
        doc = documents[similar_docs[i][0]].replace('\'', ' ')
        docs[str(similar_docs[i][0])] = doc
    # print(docs)
    wordsTree = buildWordsTree('coronavirus', model)
    return render(request, 'polls/dashboard.html', {'vectors': json.dumps(vectors), 'docs': json.dumps(docs), 'wordsTree': json.dumps(wordsTree)})
    # return render(request, 'polls/dashboard.html', {'vectors': json.dumps(vectors)})