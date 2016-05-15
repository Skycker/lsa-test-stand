import json

import operator
import random
import sphinxapi
from django.conf import settings
from django.db import transaction
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
        return self.get_documents(pks)

    def search_by_sphinx(self, query):
        client = sphinxapi.SphinxClient()
        client.SetServer(settings.SPHINX_HOST, settings.SPHINX_PORT)
        response = client.Query(query, index=settings.SPHINX_INDEX_NAME)
        pks = []
        if response:
            matches = response['matches']
            pks = [m['id'] for m in matches]
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
