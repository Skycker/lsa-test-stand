from django.contrib import admin
from web_site import models


@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "group")
    list_filter = ("group",)
    search_fields = ("title", "content")


class SearchResultInline(admin.TabularInline):
    model = models.SearchResult
    ordering = ("engine", "position",)
    extra = 0


@admin.register(models.SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("query", "ip", "created_at")
    search_fields = ("query", "ip")
    list_filter = ("created_at",)
    inlines = [SearchResultInline]


@admin.register(models.SearchResult)
class SearchResult(admin.ModelAdmin):
    list_display = ("search_query", "document", "engine", "relevance")
    list_filter = ("engine", "relevance")


admin.site.register(models.DocumentGroup)
