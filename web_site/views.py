import json

import operator
import random
import sphinxapi
from django.conf import settings
from django.db import transaction
from django.db.models import Avg
from django.http import HttpResponse
from django.views import generic
from lsa.search.machine import SearchMachine
from web_site import models


class SearchView(generic.TemplateView):
    template_name = "web_site/search.html"

    def get_context_data(self, **kwargs):
        cd = super(SearchView, self).get_context_data(**kwargs)

        query = self.request.GET.get('q', '')
        cd['query'] = query
        if query:
            semantic_results = self.search_by_lsa(query)
            sphinx_results = self.search_by_sphinx(query)
            results = [{"records": semantic_results, "engine": models.SearchResult.LSA},
                       {"records": sphinx_results, "engine": models.SearchResult.SPHINX}]
            random.shuffle(results)
            cd["results"] = results
        cd["relevance_levels"] = models.SearchResult.RELEVANCE_CHOICES
        return cd

    def sort_by_given_order(self, values, order, getter):
        results = []
        ignored = []
        for pos_value in order:
            for v in values:
                if v not in ignored and getter(v) == pos_value:
                    results.append(v)
                    ignored.append(v)
                    break
        return results

    def get_documents(self, pks):
        documents = models.Document.objects.filter(pk__in=pks)
        return self.sort_by_given_order(documents, pks, operator.attrgetter('id'))

    def search_by_lsa(self, query):
        sm = SearchMachine(**settings.INDEX_SETTINGS)
        search_results = sm.search(query, with_distances=True, limit=10)
        pks = []
        if search_results:
            pks = [r[0] for r in search_results]
        print(len(pks), "LSA")
        return self.get_documents(pks)

    def search_by_sphinx(self, query):
        client = sphinxapi.SphinxClient()
        client.SetServer(settings.SPHINX_HOST, settings.SPHINX_PORT)
        response = client.Query(query, index=settings.SPHINX_INDEX_NAME)
        pks = []
        if response:
            matches = response['matches']
            pks = [m['id'] for m in matches]
        print(len(pks), "Sphinx")
        return self.get_documents(pks)


class SaveAccessorMarks(generic.View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        marks = data.get("marks")
        marks = json.loads(marks)
        new_query = models.SearchQuery.objects.create(query=data.get("query"), ip=request.META.get('REMOTE_ADDR'))
        new_results = []
        for mark in marks:
            new_r = models.SearchResult(search_query=new_query, document_id=int(mark['document']),
                                        engine=int(mark['engine']), relevance=int(mark['relevance']),
                                        position=int(mark['position']))
            new_results.append(new_r)
        models.SearchResult.objects.bulk_create(new_results)
        return HttpResponse()


class DocumentView(generic.DetailView):
    template_name = 'web_site/document.html'
    context_object_name = "document"
    model = models.Document


class ResultPage(generic.TemplateView):
    template_name = 'web_site/results.html'

    def get_context_data(self, **kwargs):
        cd = super(ResultPage, self).get_context_data(**kwargs)
        queries = models.SearchQuery.objects.all()

        # precision
        cd['avg_lsa_weak_precision'] = queries.aggregate(v=Avg('lsa_weak_precision'))['v']
        cd['avg_lsa_strong_precision'] = queries.aggregate(v=Avg('lsa_strong_precision'))['v']
        cd['avg_ideal_weak_precision'] = queries.aggregate(v=Avg('ideal_weak_precision'))['v']
        cd['avg_ideal_strong_precision'] = queries.aggregate(v=Avg('ideal_strong_precision'))['v']
        avg_week_prec_delta = abs(cd["avg_lsa_weak_precision"] - cd["avg_ideal_weak_precision"])
        cd['avg_week_prec_delta'] = avg_week_prec_delta
        cd['avg_week_prec_delta_percent'] = avg_week_prec_delta / cd["avg_ideal_weak_precision"] * 100
        avg_strong_prec_delta = abs(cd['avg_lsa_strong_precision'] - cd['avg_ideal_strong_precision'])
        cd['avg_strong_prec_delta'] = avg_strong_prec_delta
        cd['avg_strong_prec_delta_percent'] = avg_strong_prec_delta / cd['avg_ideal_strong_precision'] * 100

        # MAP
        cd['lsa_weak_map'] = queries.aggregate(v=Avg('lsa_weak_avg_prec'))['v']
        cd['lsa_strong_map'] = queries.aggregate(v=Avg('lsa_strong_avg_prec'))['v']
        cd['ideal_weak_map'] = queries.aggregate(v=Avg('ideal_weak_avg_prec'))['v']
        cd['ideal_strong_map'] = queries.aggregate(v=Avg('ideal_strong_avg_prec'))['v']
        lsa_weak_map_delta = abs(cd['lsa_weak_map'] - cd['ideal_weak_map'])
        cd['lsa_weak_map_delta'] = lsa_weak_map_delta
        cd['lsa_weak_map_delta_percent'] = lsa_weak_map_delta / cd['ideal_weak_map'] * 100
        lsa_strong_map_delta = abs(cd['lsa_strong_map'] - cd['ideal_strong_map'])
        cd['lsa_strong_map_delta'] = lsa_strong_map_delta
        cd['lsa_strong_map_delta_percent'] = lsa_strong_map_delta / cd['ideal_strong_map'] * 100

        # NDCG
        cd['avg_lsa_ndcg'] = queries.aggregate(v=Avg("lsa_ndcg"))['v']
        cd['avg_ideal_ndcg'] = queries.aggregate(v=Avg("ideal_ndcg"))['v']
        avg_ndcg_delta = abs(cd['avg_lsa_ndcg'] - cd['avg_ideal_ndcg'])
        cd['avg_ndcg_delta'] = avg_ndcg_delta
        cd['avg_ndcg_delta_percent'] = avg_ndcg_delta / cd['avg_ideal_ndcg'] * 100

        # MRR
        cd['avg_lsa_weak_mrr'] = queries.aggregate(v=Avg("lsa_weak_reciprocal_rank"))['v']
        cd['avg_lsa_strong_mrr'] = queries.aggregate(v=Avg("lsa_strong_reciprocal_rank"))['v']
        cd['avg_ideal_weak_mrr'] = queries.aggregate(v=Avg("ideal_weak_reciprocal_rank"))['v']
        cd['avg_ideal_strong_mrr'] = queries.aggregate(v=Avg("ideal_strong_reciprocal_rank"))['v']
        lsa_weak_mrr_delta = abs(cd['avg_lsa_weak_mrr'] - cd['avg_ideal_weak_mrr'])
        cd['lsa_weak_mrr_delta'] = lsa_weak_mrr_delta
        cd['lsa_weak_mrr_delta_percent'] = lsa_weak_mrr_delta / cd['avg_ideal_weak_mrr'] * 100
        lsa_strong_mrr_delta = abs(cd['avg_lsa_strong_mrr'] - cd['avg_ideal_strong_mrr'])
        cd['lsa_strong_mrr_delta'] = lsa_strong_mrr_delta
        cd['lsa_strong_mrr_delta_percent'] = lsa_strong_mrr_delta / cd['avg_ideal_strong_mrr'] * 100

        return cd
