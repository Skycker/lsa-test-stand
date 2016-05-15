from django.conf import settings
from django.core.management.base import BaseCommand
from lsa.search.machine import SearchMachine


class Command(BaseCommand):
    help = 'Make search index by LSA algorithm'

    def handle(self, *args, **options):
        kwargs = settings.INDEX_SETTINGS
        sm = SearchMachine(**kwargs)
        sm.build_index()
        # sm.draw_space()
