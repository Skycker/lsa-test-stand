from django.core.management.base import BaseCommand
from django.db.models import Count
from web_site import models


class Command(BaseCommand):
    help = 'Make search index by LSA algorithm'

    def handle(self, *args, **options):
        qs = models.SearchQuery.objects.annotate(results=Count("searchresult")).filter(results=0)
        print("{} deleted".format(qs.count()))
        qs.delete()
