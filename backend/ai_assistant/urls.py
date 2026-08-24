from django.urls import path

from .views import TranscriptSegmentUploadView, MeetingSummaryView

urlpatterns = [
    path('meetings/<int:meeting_id>/transcript/', TranscriptSegmentUploadView.as_view(), name='ai-transcript'),
    path('meetings/<int:meeting_id>/summary/', MeetingSummaryView.as_view(), name='ai-summary'),
]
