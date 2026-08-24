from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Meeting, Participant, ChatMessage, ActionItem
from .serializers import (
    MeetingListSerializer, MeetingDetailSerializer, MeetingCreateSerializer,
    ParticipantSerializer, ChatMessageSerializer, ActionItemSerializer,
)


class MeetingViewSet(viewsets.ModelViewSet):
    """
    /api/meetings/                 list + create
    /api/meetings/{id}/             retrieve/update/delete
    /api/meetings/{id}/join/        POST  - join by id (host or invited)
    /api/meetings/join_by_code/     POST  {room_code} - join via room code
    /api/meetings/{id}/leave/       POST
    /api/meetings/{id}/start/       POST  - host starts the live session
    /api/meetings/{id}/end/         POST  - host ends the live session
    /api/meetings/{id}/chat/        GET/POST
    /api/meetings/{id}/action_items/ GET/POST
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Meeting.objects.filter(
            participants__user=user
        ).distinct().order_by('-scheduled_start')

    def get_serializer_class(self):
        if self.action == 'list':
            return MeetingListSerializer
        if self.action == 'create':
            return MeetingCreateSerializer
        return MeetingDetailSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        meeting = self.get_object()
        participant, _created = Participant.objects.get_or_create(
            meeting=meeting, user=request.user,
            defaults={'role': 'guest', 'joined_at': timezone.now()},
        )
        if participant.joined_at is None:
            participant.joined_at = timezone.now()
            participant.save(update_fields=['joined_at'])
        return Response(ParticipantSerializer(participant).data)

    @action(detail=False, methods=['post'], url_path='join_by_code')
    def join_by_code(self, request):
        code = request.data.get('room_code', '').strip().lower()
        meeting = get_object_or_404(Meeting, room_code=code)
        participant, _created = Participant.objects.get_or_create(
            meeting=meeting, user=request.user,
            defaults={'role': 'guest', 'joined_at': timezone.now()},
        )
        return Response(MeetingDetailSerializer(meeting).data)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        meeting = self.get_object()
        Participant.objects.filter(meeting=meeting, user=request.user).update(
            left_at=timezone.now()
        )
        return Response({'detail': 'left meeting'})

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        meeting = self.get_object()
        meeting.status = 'live'
        meeting.actual_start = timezone.now()
        meeting.save(update_fields=['status', 'actual_start'])
        return Response(MeetingDetailSerializer(meeting).data)

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        meeting = self.get_object()
        meeting.status = 'ended'
        meeting.actual_end = timezone.now()
        meeting.save(update_fields=['status', 'actual_end'])
        return Response(MeetingDetailSerializer(meeting).data)

    @action(detail=True, methods=['get', 'post'])
    def chat(self, request, pk=None):
        meeting = self.get_object()
        if request.method == 'POST':
            serializer = ChatMessageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(meeting=meeting, sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        messages = meeting.chat_messages.select_related('sender', 'sender__profile')
        return Response(ChatMessageSerializer(messages, many=True).data)

    @action(detail=True, methods=['get', 'post'], url_path='action-items')
    def action_items(self, request, pk=None):
        meeting = self.get_object()
        if request.method == 'POST':
            serializer = ActionItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(meeting=meeting)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        items = meeting.action_items.all()
        return Response(ActionItemSerializer(items, many=True).data)
