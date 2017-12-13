import math

from ckeditor.fields import RichTextField
from django.db import models


class DocumentGroup(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return str(self.title)


class Document(models.Model):
    title = models.CharField(max_length=250)
    group = models.ForeignKey(DocumentGroup, related_name='documents', blank=True, null=True)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)


def get_bool_map(rates, is_strong=False):
    """ Array of boolean query map. True if answer is relevant and False other way """

    threshold = SearchResult.RELEVANT_PLUS if is_strong else SearchResult.RELEVANT_MINUS
    return [True if r >= threshold else False for r in rates]


def precision_at_k(map, k):
    """ Precision@K """

    assert (k > 0)
    map_slice = map[:k]
    return sum(map_slice) / k


def avg_precision(map):
    """ Average Precision metric (AP) """

    prec = []
    for index, rate in enumerate(map):
        if rate:
            prec.append(precision_at_k(map, index + 1))
    return sum(prec) / (len(prec) or 1)


def dcg(rates):
    """ DCG metric """

    values = [(2 ** r - 1) / (math.log2(index + 2)) for index, r in enumerate(rates)]
    return sum(values)


def reciprocal_rank(map):
    """ Reciprocal rank metric """

    for index, item in enumerate(map):
        if item is True:
            return 1 / (index + 1)


class SearchQuery(models.Model):
    query = models.CharField(max_length=128)
    ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    # precision
    lsa_weak_precision = models.FloatField(blank=True, null=True)
    lsa_strong_precision = models.FloatField(blank=True, null=True)
    ideal_weak_precision = models.FloatField(blank=True, null=True)
    ideal_strong_precision = models.FloatField(blank=True, null=True)

    # avg precision
    lsa_weak_avg_prec = models.FloatField(blank=True, null=True)
    lsa_strong_avg_prec = models.FloatField(blank=True, null=True)
    ideal_weak_avg_prec = models.FloatField(blank=True, null=True)
    ideal_strong_avg_prec = models.FloatField(blank=True, null=True)

    # reciprocal rank
    lsa_weak_reciprocal_rank = models.FloatField(blank=True, null=True)
    lsa_strong_reciprocal_rank = models.FloatField(blank=True, null=True)
    ideal_weak_reciprocal_rank = models.FloatField(blank=True, null=True)
    ideal_strong_reciprocal_rank = models.FloatField(blank=True, null=True)

    # discounted cumulative gain
    lsa_ndcg = models.FloatField(blank=True, null=True)
    ideal_ndcg = models.FloatField(blank=True, null=True)

    def get_rates(self, engine):
        return self.searchresult_set.filter(engine=engine).order_by('position').values_list('relevance', flat=True)

    def calc_metrics(self):
        lsa_rates = self.get_rates(SearchResult.LSA)
        ideal_rates = self.get_rates(SearchResult.SPHINX)

        weak_lsa_map = get_bool_map(lsa_rates)
        strong_lsa_map = get_bool_map(lsa_rates, is_strong=True)
        weak_ideal_map = get_bool_map(ideal_rates)
        strong_ideal_map = get_bool_map(ideal_rates, is_strong=True)

        self.lsa_weak_precision = sum(weak_lsa_map) / (len(weak_lsa_map) or 1)
        self.lsa_strong_precision = sum(strong_lsa_map) / (len(strong_lsa_map) or 1)
        self.ideal_weak_precision = sum(weak_ideal_map) / (len(weak_ideal_map) or 1)
        self.ideal_strong_precision = sum(strong_ideal_map) / (len(strong_ideal_map) or 1)

        self.lsa_weak_avg_prec = avg_precision(weak_lsa_map)
        self.lsa_strong_avg_prec = avg_precision(strong_lsa_map)
        self.ideal_weak_avg_prec = avg_precision(weak_ideal_map)
        self.ideal_strong_avg_prec = avg_precision(strong_ideal_map)

        self.lsa_ndcg = dcg(lsa_rates) / (dcg(sorted(lsa_rates, reverse=True)) or 1)
        self.ideal_ndcg = dcg(ideal_rates) / (dcg(sorted(ideal_rates, reverse=True)) or 1)

        self.lsa_weak_reciprocal_rank = reciprocal_rank(weak_lsa_map)
        self.lsa_strong_reciprocal_rank = reciprocal_rank(strong_lsa_map)
        self.ideal_weak_reciprocal_rank = reciprocal_rank(weak_ideal_map)
        self.ideal_strong_reciprocal_rank = reciprocal_rank(strong_ideal_map)

        self.save()

    def __str__(self):
        return str(self.query)


class SearchResult(models.Model):
    LSA, SPHINX = 1, 2
    ENGINES = (
        (LSA, "LSA"),
        (SPHINX, "Sphinx")
    )

    NOT_RELEVANT, RELEVANT_MINUS, RELEVANT_PLUS, RELEVANT = 0, 1, 2, 3
    RELEVANCE_CHOICES = (
        (NOT_RELEVANT, "Не релевантный"),
        (RELEVANT_MINUS, "Немного соответсвует запросу"),
        (RELEVANT_PLUS, "По большей степени соответствует запросу"),
        (RELEVANT, "Совершенно релевантный"),
    )

    document = models.ForeignKey(Document)
    search_query = models.ForeignKey(SearchQuery)
    engine = models.SmallIntegerField(choices=ENGINES)
    relevance = models.SmallIntegerField(choices=RELEVANCE_CHOICES)
    position = models.SmallIntegerField()

    def __str__(self):
        return str(self.relevance)
