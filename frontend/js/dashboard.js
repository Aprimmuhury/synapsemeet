/**
 * SynapseMeet - dashboard.js
 * Renders the meeting list, handles the "new meeting" FAB, and join-by-code.
 */
document.addEventListener('DOMContentLoaded', () => {
  if (!SynapseAPI.isAuthenticated()) {
    window.location.href = 'index.html';
    return;
  }

  const user = SynapseAPI.getCurrentUser();
  const greetingEl = document.getElementById('greeting-name');
  if (greetingEl && user) {
    greetingEl.textContent = (user.profile && user.profile.display_name) || user.username;
  }

  loadMeetings();

  const fab = document.getElementById('fab-new-meeting');
  if (fab) fab.addEventListener('click', () => window.location.href = 'meeting-create.html');

  const joinForm = document.getElementById('join-by-code-form');
  if (joinForm) {
    joinForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const code = document.getElementById('room-code-input').value.trim();
      if (!code) return;
      try {
        const meeting = await SynapseAPI.joinByCode(code);
        window.location.href = `meeting-room.html?id=${meeting.id}`;
      } catch (err) {
        alert('Could not find a meeting with that code.');
      }
    });
  }
});

function timeLabel(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function initials(name) {
  return (name || '?').split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase();
}

async function loadMeetings() {
  const listEl = document.getElementById('meeting-list');
  const emptyEl = document.getElementById('meeting-empty');
  try {
    const data = await SynapseAPI.listMeetings();
    const meetings = data.results || data;
    if (!meetings.length) {
      emptyEl.style.display = 'block';
      return;
    }
    emptyEl.style.display = 'none';
    listEl.innerHTML = meetings.map(renderMeetingCard).join('');
    listEl.querySelectorAll('[data-join]').forEach(btn => {
      btn.addEventListener('click', () => {
        window.location.href = `meeting-room.html?id=${btn.dataset.join}`;
      });
    });
  } catch (err) {
    emptyEl.style.display = 'block';
    emptyEl.querySelector('strong').textContent = 'Could not load meetings';
  }
}

function renderMeetingCard(m) {
  const isLive = m.status === 'live';
  return `
    <div class="meeting-card">
      <div class="meeting-card-top">
        <div>
          <h3>${escapeHtml(m.title)}</h3>
          <div class="meta">
            <span>${timeLabel(m.scheduled_start)}</span>
            <span>·</span>
            <span>${m.participant_count} joined</span>
          </div>
        </div>
        ${isLive ? '<span class="live-badge"><span class="dot"></span>Live</span>' : ''}
      </div>
      <div class="meeting-card-top">
        <div class="avatars">
          <div class="synapse-ring"><div class="avatar">${initials(m.host.display_name || m.host.username)}</div></div>
        </div>
        <button class="btn btn-primary" data-join="${m.id}">${isLive ? 'Join now' : 'Open'}</button>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
