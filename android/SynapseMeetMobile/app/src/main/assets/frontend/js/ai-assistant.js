/**
 * SynapseMeet - ai-assistant.js
 * Shared helpers for AI-facing UI: rendering live captions and simulating
 * caption arrival for demo/testing purposes without a real speech-to-text
 * pipeline wired in yet.
 */
const SynapseAI = (() => {
  function renderCaption(container, speakerName, text) {
    const el = document.createElement('div');
    el.className = 'ai-caption';
    el.innerHTML = `<span class="speaker">${speakerName}:</span> ${text}`;
    container.appendChild(el);
    container.scrollTop = container.scrollHeight;
  }

  /**
   * Demo-only helper: feeds a few sample captions into a container so the
   * live-captions panel can be reviewed without a real transcription
   * pipeline connected. Safe to delete once real audio -> text is wired up.
   */
  function simulateLiveCaptions(container) {
    const sample = [
      ['Priya', "Let's start with the Q3 roadmap review."],
      ['Diego', 'Sounds good, I have the metrics ready to share.'],
      ['Priya', "Great, I'll drop the doc in chat."],
    ];
    let i = 0;
    const interval = setInterval(() => {
      if (i >= sample.length) { clearInterval(interval); return; }
      renderCaption(container, sample[i][0], sample[i][1]);
      i += 1;
    }, 2200);
  }

  return { renderCaption, simulateLiveCaptions };
})();
