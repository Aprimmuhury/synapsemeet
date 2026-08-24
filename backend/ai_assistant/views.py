from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from meetings.models import Meeting
from .models import MeetingSummary
from .serializers import TranscriptSegmentSerializer, MeetingSummarySerializer
from .services import AIMeetingAssistant


class TranscriptSegmentUploadView(APIView):
    """POST /api/ai/meetings/{meeting_id}/transcript/
    Client streams short speech-to-text chunks here as the meeting happens.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        assistant = AIMeetingAssistant(meeting)
        segment = assistant.save_transcript_segment(
            speaker=request.user,
            text=request.data.get('text', ''),
            start_time_ms=request.data.get('start_time_ms', 0),
            end_time_ms=request.data.get('end_time_ms', 0),
        )
        return Response(TranscriptSegmentSerializer(segment).data, status=status.HTTP_201_CREATED)


class MeetingSummaryView(APIView):
    """
    GET  /api/ai/meetings/{meeting_id}/summary/  - fetch the latest summary
    POST /api/ai/meetings/{meeting_id}/summary/  - (re)generate the summary
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        summary = MeetingSummary.objects.filter(meeting=meeting).first()
        if not summary:
            return Response({'detail': 'No summary generated yet.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MeetingSummarySerializer(summary).data)

    def post(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        assistant = AIMeetingAssistant(meeting)
        summary = assistant.generate_summary()
        return Response(MeetingSummarySerializer(summary).data, status=status.HTTP_201_CREATED)
