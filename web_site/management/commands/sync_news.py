import pymysql
from django.core.management.base import BaseCommand
from web_site import models

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '1'
DB_NAME = 'news'
CHARSET = 'utf8'


class Command(BaseCommand):
    help = 'Make search index by LSA algorithm'

    def handle(self, *args, **options):
        CONNECTION = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME,
                                     charset=CHARSET, cursorclass=pymysql.cursors.Cursor)
        query = "SELECT id, title, text FROM news_news;"

        documents = []
        models.Document.objects.all().delete()
        with CONNECTION.cursor() as cursor:
            cursor.execute(query)
            response = cursor.fetchall()
            for r in response:
                documents.append(models.Document(pk=r[0], title=r[1], content=r[2]))
        models.Document.objects.bulk_create(documents, batch_size=700)
