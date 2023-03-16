from django.urls import path
from .views import (
	agents_view,
    resources_view,
    column_relation_view,
    import_all_files_view,

    get_files_download_view,

    test_view
)


app_name = 'imports'


urlpatterns = [
	path('agents', agents_view, name='agents'),
    path('resources/<str:more_recent>', resources_view, name = 'resources'),
    path('column_relation/<str:col_relation>/<str:more_recent>', column_relation_view, name = 'column_relation'),
    path('all_files/<str:col_relation>/<str:more_recent>', import_all_files_view, name = 'all_files'),
    path('files_download', get_files_download_view, name = 'files_download'),
    path('test', test_view, name = 'test'),
]
