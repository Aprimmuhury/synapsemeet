from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Meeting, Participant, ChatMessage, ActionItem

User = get_user_model()


class MiniUserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='profile.display_name', read_only=True)
    avatar_color = serializers.CharField(source='profile.avatar_color', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'avatar_color']


class ParticipantSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)

    class Meta:
        model = Participant
        fields = [
            'id', 'user', 'role', 'joined_at', 'left_at',
            'is_muted', 'is_camera_on', 'is_speaking',
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = MiniUserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'content', 'sent_at']
        read_only_fields = ['sender', 'sent_at']


class ActionItemSerializer(serializers.ModelSerializer):
    assigned_to = MiniUserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_to', write_only=True,
        required=False, allow_null=True,
    )

    class Meta:
        model = ActionItem
        fields = [
            'id', 'description', 'assigned_to', 'assigned_to_id',
            'is_done', 'created_by_ai', 'created_at',
        ]


class MeetingListSerializer(serializers.ModelSerializer):
    host = MiniUserSerializer(read_only=True)
    participant_count = serializers.IntegerField(source='participants.count', read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'room_code', 'host', 'scheduled_start', 'scheduled_end',
            'status', 'is_ai_enabled', 'participant_count',
        ]


class MeetingDetailSerializer(serializers.ModelSerializer):
    host = MiniUserSerializer(read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    action_items = ActionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'description', 'room_code', 'host',
            'scheduled_start', 'scheduled_end', 'actual_start', 'actual_end',
            'status', 'is_ai_enabled', 'participants', 'action_items', 'created_at',
        ]


class MeetingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'description', 'scheduled_start', 'scheduled_end',
            'is_ai_enabled', 'room_code', 'status',
        ]
        read_only_fields = ['room_code', 'status']

    def create(self, validated_data):
        request = self.context['request']
        meeting = Meeting.objects.create(host=request.user, **validated_data)
        Participant.objects.create(meeting=meeting, user=request.user, role='host')
        return meeting
