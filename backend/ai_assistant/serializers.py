from rest_framework import serializers

from .models import TranscriptSegment, MeetingSummary


class TranscriptSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranscriptSegment
        fields = ['id', 'meeting', 'speaker', 'text', 'start_time_ms', 'end_time_ms', 'created_at']
        read_only_fields = ['created_at']


class MeetingSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingSummary
        fields = [
            'id', 'meeting', 'summary_text', 'key_points',
            'decisions', 'generated_action_items', 'generated_at',
        ]
