from django.urls import path

from . import views

urlpatterns = [
    path('', views.problem_set, name='problemSets'),
    path('import', views.importing, name='import'),
    path('import/fromSubtitles', views.from_subtitles, name='fromSubtitles'),
    path('message', views.success_import, name='successImport'),
    path('training/<int:set_id>/<int:repeat>', views.training, name='training'),
    path('eval/<int:set_id>/<int:problem_number>', views.evaluate, name='eval'),
    path('queue/create', views.create_queue, name='createQueue'),
    path('bookmark/create', views.create_bookmark, name='bookmark'),
]
