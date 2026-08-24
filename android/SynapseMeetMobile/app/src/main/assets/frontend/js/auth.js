/**
 * SynapseMeet - auth.js
 * Handles the login and register screens.
 */
document.addEventListener('DOMContentLoaded', () => {
  if (SynapseAPI.isAuthenticated() && document.body.dataset.page === 'auth') {
    window.location.href = 'dashboard.html';
    return;
  }

  const authButtons = document.querySelectorAll('.auth-toggle');
  const authPanels = {
    login: document.querySelector('.auth-panel[data-mode="login"]'),
    register: document.querySelector('.auth-panel[data-mode="register"]'),
  };

  const setAuthMode = (mode) => {
    const errorBox = document.getElementById('form-error');
    if (errorBox) {
      errorBox.classList.remove('visible');
      errorBox.textContent = '';
    }

    authButtons.forEach((button) => {
      const isActive = button.dataset.mode === mode;
      button.classList.toggle('is-active', isActive);
      button.setAttribute('aria-pressed', String(isActive));
    });

    Object.entries(authPanels).forEach(([key, panel]) => {
      if (!panel) return;
      const isVisible = key === mode;
      panel.classList.toggle('active', isVisible);
      panel.hidden = !isVisible;
    });
  };

  authButtons.forEach((button) => {
    button.addEventListener('click', () => setAuthMode(button.dataset.mode));
  });

  const defaultMode = document.body.dataset.defaultAuthMode || 'login';
  setAuthMode(defaultMode);

  const attachPasswordToggle = (inputId) => {
    const input = document.getElementById(inputId);
    const toggle = document.querySelector(`[data-target="${inputId}"]`);

    if (!input || !toggle) return;

    toggle.addEventListener('click', () => {
      const shouldShow = input.type === 'password';
      input.type = shouldShow ? 'text' : 'password';
      toggle.classList.toggle('is-visible', shouldShow);
      toggle.setAttribute('aria-label', shouldShow ? 'Hide password' : 'Show password');
      toggle.setAttribute('aria-pressed', String(shouldShow));
      toggle.title = shouldShow ? 'Hide password' : 'Show password';
    });
  };

  attachPasswordToggle('password');
  attachPasswordToggle('reg-password');

  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorBox = document.getElementById('form-error');
      errorBox.classList.remove('visible');
      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value;

      try {
        await SynapseAPI.login(username, password);
        window.location.href = 'dashboard.html';
      } catch (err) {
        errorBox.textContent = 'Could not sign in. Check your username and password.';
        errorBox.classList.add('visible');
      }
    });
  }

  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorBox = document.getElementById('form-error');
      errorBox.classList.remove('visible');

      const payload = {
        username: document.getElementById('reg-username').value.trim(),
        email: document.getElementById('reg-email').value.trim(),
        password: document.getElementById('reg-password').value,
        display_name: document.getElementById('reg-display-name').value.trim(),
      };

      try {
        await SynapseAPI.register(payload);
        await SynapseAPI.login(payload.username, payload.password);
        window.location.href = 'dashboard.html';
      } catch (err) {
        errorBox.textContent = 'Could not create your account. ' + err.message;
        errorBox.classList.add('visible');
      }
    });
  }
});
