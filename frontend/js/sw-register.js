// Registers the service worker so SynapseMeet behaves like an installable
// mobile app (works offline for the shell, faster repeat loads).
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('service-worker.js').catch(() => {});
  });
}
