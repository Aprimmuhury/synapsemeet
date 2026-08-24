# SynapseMeet Android APK wrapper

This folder contains a basic Android WebView project that packages the existing SynapseMeet frontend as a mobile app. The APK bundles a full copy of `frontend/` under `app/src/main/assets/frontend/` and loads it locally (`file:///android_asset/frontend/index.html`) — but it still needs a real, internet-reachable Django backend to log in, load meetings, etc.

## How the backend URL works

`assets/frontend/js/config.js` sets `window.SYNAPSEMEET_API_BASE` and is loaded **before** `js/api.js` on every page. That one line is the single source of truth for which backend the app talks to. There is no more emulator-only (`10.0.2.2`) special-casing in the native Java code — `MainActivity.java` just loads the bundled HTML and lets the page's own scripts handle the API base URL.

## Making a build that works standalone (no shared WiFi, no local server)

1. **Deploy the Django backend somewhere public** (see `../backend/DEPLOYMENT.md`) so you have a real HTTPS URL, e.g. `https://synapsemeet.onrender.com`.
2. **Edit `frontend/js/config.js`** at the repo root:
   ```js
   window.SYNAPSEMEET_API_BASE = 'https://synapsemeet.onrender.com/api';
   ```
3. **Re-sync the bundled copy** so the APK picks up the change (the assets folder is a plain copy, it does not auto-update):
   ```bash
   # from the repo root
   rm -rf android/SynapseMeetMobile/app/src/main/assets/frontend
   cp -r frontend android/SynapseMeetMobile/app/src/main/assets/frontend
   ```
   Do this any time you change anything under `frontend/`.
4. Build the APK (see below) and install it on a real device with WiFi off / mobile data only, to confirm it's truly independent.

## Files to review

- [SynapseMeetMobile/app/src/main/java/com/synapsemeet/mobile/MainActivity.java](SynapseMeetMobile/app/src/main/java/com/synapsemeet/mobile/MainActivity.java) — WebView shell, no URL logic
- [SynapseMeetMobile/app/src/main/assets/frontend/js/config.js](SynapseMeetMobile/app/src/main/assets/frontend/js/config.js) — the backend URL

## Build the APK

1. Install Android Studio with Android SDK 34 and JDK 17.
2. Open this project folder in Android Studio: `android/SynapseMeetMobile`
3. Let Gradle sync.
4. Build -> Build Bundle(s) / APK(s) -> Build APK.
5. The generated APK will appear under:
   `android/SynapseMeetMobile/app/build/outputs/apk/debug/`
6. For a signed release APK (needed to share outside your own devices or publish), use Build -> Generate Signed Bundle / APK instead, and create a keystore when prompted. Keep that keystore file and its passwords safe — you need the exact same one for every future update.

## Local testing (optional, before you deploy)

If you just want to test on an emulator against your dev machine before deploying anywhere, temporarily set in `config.js`:
```js
window.SYNAPSEMEET_API_BASE = 'http://10.0.2.2:8000/api';
```
and run `python manage.py runserver 0.0.0.0:8000` on the host machine. Remember to switch it back to the real HTTPS URL — and re-sync the assets folder — before building the APK you actually intend to install/share.

## Important note

This environment does not currently have the Android SDK or Java toolchain installed, so the actual `.apk` file cannot be produced here. Use Android Studio on your own machine to run the build step above.
