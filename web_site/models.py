from ckeditor.fields import RichTextField
from django.db import models


class DocumentGroup(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return str(self.title)


class Document(models.Model):
    title = models.CharField(max_length=250)
    group = models.ForeignKey(DocumentGroup, related_name='documents')
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)


class SearchQuery(models.Model):
    query = models.CharField(max_length=128)
    ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

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
