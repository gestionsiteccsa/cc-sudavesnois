from django.contrib import admin

from search.models import SearchConfigModel


@admin.register(SearchConfigModel)
class SearchConfigModelAdmin(admin.ModelAdmin):
    list_display = (
        "min_query_length",
        "max_query_length",
        "results_per_page",
        "highlight_search_terms",
    )

    def has_add_permission(self, request):
        return not SearchConfigModel.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
