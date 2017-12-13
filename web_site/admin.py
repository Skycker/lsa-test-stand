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
    readonly_fields = ("position", "document", "relevance", 'engine', )

    def has_add_permission(self, request):
        return False


@admin.register(models.SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("query", "ip", "created_at")
    search_fields = ("query", "ip")
    list_filter = ("created_at",)
    inlines = [SearchResultInline]
    actions = ["calculate_metrics"]

    def calculate_metrics(self, request, queryset):
        for item in queryset:
            item.calc_metrics()
    calculate_metrics.short_description = "Пересчитать метрики качества"


@admin.register(models.SearchResult)
class SearchResult(admin.ModelAdmin):
    list_display = ("search_query", "document", "engine", "relevance")
    list_filter = ("engine", "relevance")

    def get_queryset(self, request):
        return super(SearchResult, self).get_queryset(request).select_related("document")


admin.site.register(models.DocumentGroup)
