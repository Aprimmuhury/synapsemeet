/**
 * SynapseMeet - meeting.js
 * Meeting room screen: participant grid, tabs (AI / chat / action items),
 * controls bar. Media (camera/mic) is left as an integration point for a
 * WebRTC provider - see the comment in initMedia().
 */
let currentMeetingId = null;
let currentMeeting = null;
let micOn = true;
let cameraOn = true;
let screenShareOn = false;
let screenRecordOn = false;

document.addEventListener('DOMContentLoaded', () => {
  if (!SynapseAPI.isAuthenticated()) {
    window.location.href = 'index.html';
    return;
  }
  const params = new URLSearchParams(window.location.search);
  currentMeetingId = params.get('id');
  if (!currentMeetingId) {
    window.location.href = 'dashboard.html';
    return;
  }

  loadMeetingRoom();
  bindTabs();
  bindControls();
  bindChat();
  initMedia();
});

async function loadMeetingRoom() {
  try {
    currentMeeting = await SynapseAPI.getMeeting(currentMeetingId);
    await SynapseAPI.joinMeeting(currentMeetingId);
    document.getElementById('room-title').textContent = currentMeeting.title;
    document.getElementById('room-code').textContent = currentMeeting.room_code;
    renderParticipants(currentMeeting.participants);
    renderActionItems(currentMeeting.action_items);
    loadChat();
    loadSummary();
  } catch (err) {
    alert('Could not load this meeting.');
    window.location.href = 'dashboard.html';
  }
}

function renderParticipants(participants) {
  const grid = document.getElementById('participant-grid');
  grid.innerHTML = participants.map(p => {
    const name = p.user.display_name || p.user.username;
    const speaking = p.is_speaking ? 'is-speaking' : '';
    return `
      <div class="participant-tile">
        <div class="synapse-ring ${speaking}" style="--size:64px; --avatar-color:${p.user.avatar_color || '#7C5CFF'}">
          <div class="avatar">${initialsOf(name)}</div>
        </div>
        <span class="name">${escapeHtml(name)}</span>
        <div class="tile-icons">
          ${p.is_muted ? '<span class="muted">&#128263;</span>' : ''}
          ${!p.is_camera_on ? '<span>&#128248;</span>' : ''}
        </div>
      </div>
    `;
  }).join('');
}

function bindTabs() {
  const tabs = document.querySelectorAll('.room-tabs button');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      document.querySelectorAll('.room-panel').forEach(p => p.hidden = true);
      document.getElementById(tab.dataset.panel).hidden = false;
    });
  });
}

function bindControls() {
  const micBtn = document.getElementById('toggle-mic');
  const camBtn = document.getElementById('toggle-camera');
  const screenShareBtn = document.getElementById('toggle-screen-share');
  const screenRecordBtn = document.getElementById('toggle-screen-record');
  const leaveBtn = document.getElementById('leave-meeting');
  const aiBtn = document.getElementById('toggle-ai');

  micBtn.addEventListener('click', () => {
    micOn = !micOn;
    micBtn.classList.toggle('active-off', !micOn);
    micBtn.textContent = micOn ? '🎙️' : '🔇';
  });

  camBtn.addEventListener('click', () => {
    cameraOn = !cameraOn;
    camBtn.classList.toggle('active-off', !cameraOn);
    camBtn.textContent = cameraOn ? '📷' : '🚫';
  });

  screenShareBtn.addEventListener('click', () => {
    screenShareOn = !screenShareOn;
    screenShareBtn.classList.toggle('active-off', !screenShareOn);
    screenShareBtn.textContent = screenShareOn ? '🖥️' : '🖥️';
  });

  screenRecordBtn.addEventListener('click', () => {
    screenRecordOn = !screenRecordOn;
    screenRecordBtn.classList.toggle('is-recording', screenRecordOn);
    screenRecordBtn.classList.toggle('active-off', !screenRecordOn);
    screenRecordBtn.textContent = screenRecordOn ? '⏹️' : '⏺️';
  });

  aiBtn.addEventListener('click', () => {
    aiBtn.classList.toggle('ai-on');
  });

  leaveBtn.addEventListener('click', async () => {
    await SynapseAPI.leaveMeeting(currentMeetingId);
    window.location.href = 'dashboard.html';
  });
}

async function loadChat() {
  const chatPanel = document.getElementById('panel-chat');
  try {
    const messages = await SynapseAPI.getChat(currentMeetingId);
    chatPanel.querySelector('.chat-messages').innerHTML = messages.map(renderChatMessage).join('');
  } catch (err) { /* leave empty */ }
}

function renderChatMessage(m) {
  const name = m.sender.display_name || m.sender.username;
  return `
    <div class="chat-message">
      <div class="who">${escapeHtml(name)}</div>
      <div class="bubble">${escapeHtml(m.content)}</div>
    </div>
  `;
}

function bindChat() {
  const form = document.getElementById('chat-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    const content = input.value.trim();
    if (!content) return;
    input.value = '';
    try {
      await SynapseAPI.postChat(currentMeetingId, content);
      loadChat();
    } catch (err) { /* noop */ }
  });
}

function renderActionItems(items) {
  const list = document.getElementById('action-item-list');
  if (!items.length) {
    list.innerHTML = '<div class="empty-state"><strong>No action items yet</strong>SynapseMeet AI will surface follow-ups here as the conversation happens.</div>';
    return;
  }
  list.innerHTML = items.map(i => `
    <div class="action-item">
      <input type="checkbox" ${i.is_done ? 'checked' : ''} disabled />
      <div>
        <span class="desc ${i.is_done ? 'done' : ''}">${escapeHtml(i.description)}</span>
        ${i.created_by_ai ? '<span class="tag-ai">AI detected</span>' : ''}
      </div>
    </div>
  `).join('');
}

async function loadSummary() {
  const aiPanel = document.getElementById('ai-summary-box');
  try {
    const summary = await SynapseAPI.getSummary(currentMeetingId);
    aiPanel.textContent = summary.summary_text;
  } catch (err) {
    aiPanel.textContent = 'No summary yet. Generate one once the meeting has some conversation captured.';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const genBtn = document.getElementById('generate-summary');
  if (genBtn) {
    genBtn.addEventListener('click', async () => {
      genBtn.disabled = true;
      genBtn.textContent = 'Thinking…';
      try {
        const summary = await SynapseAPI.generateSummary(currentMeetingId);
        document.getElementById('ai-summary-box').textContent = summary.summary_text;
      } catch (err) {
        alert('Could not generate a summary right now.');
      } finally {
        genBtn.disabled = false;
        genBtn.textContent = 'Regenerate summary';
      }
    });
  }
});

function initMedia() {
  // Integration point: plug in a WebRTC provider (e.g. LiveKit, Daily,
  // Twilio Video, or a custom mediasoup/SFU) here. This mobile-web frontend
  // only models call *state* (who's muted, who's speaking, camera on/off);
  // actual audio/video transport is intentionally provider-agnostic.
}

function initialsOf(name) {
  return (name || '?').split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase();
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
