"""
SynapseMeet AI Assistant service layer.

This module is the single place responsible for talking to a large language
model provider. Everything above it (views, serializers) only ever calls
`AIMeetingAssistant`, so swapping providers or models later means editing
this file alone.

--------------------------------------------------------------------------
HOW TO PLUG IN A REAL AI PROVIDER
--------------------------------------------------------------------------
1. `pip install anthropic` (or `openai`, depending on AI_PROVIDER).
2. Set AI_API_KEY in your .env file (see backend/.env.example).
3. Replace the body of `_call_llm()` below with a real API call, e.g.:

    import anthropic
    client = anthropic.Anthropic(api_key=settings.AI_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text

Until that's done, `_call_llm()` returns clearly-labelled placeholder text
so the rest of the app (frontend included) can be built and tested end to
end without a live API key.
--------------------------------------------------------------------------
"""
from django.conf import settings

from .models import TranscriptSegment, MeetingSummary


class AIMeetingAssistant:
    """High-level AI operations used by the meetings API."""

    def __init__(self, meeting):
        self.meeting = meeting

    # ------------------------------------------------------------------
    # Live transcription
    # ------------------------------------------------------------------
    def save_transcript_segment(self, speaker, text, start_time_ms, end_time_ms):
        """Persist one chunk of live speech-to-text output."""
        return TranscriptSegment.objects.create(
            meeting=self.meeting,
            speaker=speaker,
            text=text,
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
        )

    def get_transcript_text(self):
        segments = self.meeting.transcript_segments.select_related('speaker').order_by('start_time_ms')
        lines = []
        for seg in segments:
            speaker_name = seg.speaker.get_username() if seg.speaker else 'Unknown speaker'
            lines.append(f"{speaker_name}: {seg.text}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Summarization / action items
    # ------------------------------------------------------------------
    def generate_summary(self):
        """Summarize the meeting transcript into a short recap, key points,
        decisions, and action items. Persists a MeetingSummary row."""
        transcript = self.get_transcript_text()

        if not transcript.strip():
            summary_text = (
                "No transcript is available yet for this meeting. Once live "
                "captions have captured some conversation, SynapseMeet AI "
                "will summarize it here."
            )
            key_points, decisions, action_items = [], [], []
        else:
            prompt = self._build_summary_prompt(transcript)
            raw_output = self._call_llm(prompt)
            summary_text, key_points, decisions, action_items = self._parse_summary_output(raw_output)

        summary, _created = MeetingSummary.objects.update_or_create(
            meeting=self.meeting,
            defaults={
                'summary_text': summary_text,
                'key_points': key_points,
                'decisions': decisions,
                'generated_action_items': action_items,
            },
        )
        return summary

    def _build_summary_prompt(self, transcript):
        return (
            "You are SynapseMeet's meeting assistant. Read the transcript "
            "below and return: a 3-sentence recap, a bullet list of key "
            "points, a bullet list of decisions made, and a bullet list of "
            "action items with an owner if mentioned.\n\n"
            f"TRANSCRIPT:\n{transcript}"
        )

    def _call_llm(self, prompt):
        """Placeholder LLM call. Replace with a real provider call (see the
        module docstring above) once AI_API_KEY is configured."""
        if not settings.AI_API_KEY:
            return (
                "[SynapseMeet AI placeholder response - configure AI_API_KEY "
                "in backend/.env to generate a real summary]"
            )
        # Real integration point would go here.
        return "[AI provider configured but integration code not yet wired up]"

    def _parse_summary_output(self, raw_output):
        """Very small heuristic parser for the placeholder output above.
        Once a real LLM call is wired in, prompt it to return JSON and
        replace this with `json.loads(raw_output)`."""
        summary_text = raw_output
        key_points = []
        decisions = []
        action_items = []
        return summary_text, key_points, decisions, action_items

    # ------------------------------------------------------------------
    # Live nudges (used by the meeting room UI while a call is active)
    # ------------------------------------------------------------------
    def suggest_agenda_nudge(self, elapsed_minutes, scheduled_minutes):
        """Return a short, friendly time-check nudge shown in the AI panel."""
        if scheduled_minutes and elapsed_minutes >= scheduled_minutes:
            return "You're past the scheduled end time. Consider wrapping up."
        if scheduled_minutes and elapsed_minutes >= scheduled_minutes * 0.8:
            return "About 20% of your scheduled time remains."
        return None
