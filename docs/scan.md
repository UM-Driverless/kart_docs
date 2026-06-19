---
title: Scan a part QR
---

# Scan a part QR

Point your camera at a part's QR code. The QR holds only a short ID; this page looks it up and
opens that part's documentation. Works in a real browser (Chrome on Android, Safari on iOS) — not
inside an app's in-built browser. The first time, allow camera access when asked.

<div id="scan-status" style="margin:1rem 0;font-weight:bold;">Press start to scan.</div>
<button id="scan-start" style="padding:.6rem 1.2rem;font-size:1rem;cursor:pointer;">Start camera</button>
<div id="reader" style="width:100%;max-width:420px;margin-top:1rem;"></div>

<!-- Vendored locally (not a CDN) so the scanner keeps working even if the CDN disappears.
     Path is relative to the PAGE URL (/scan/), not this source file — see .agents/error-log.md. -->
<script src="../assets/js/html5-qrcode.min.js"></script>
<script>
(function () {
  var ID_RE = /^[0-9]{16}$/;               // 16-digit numeric part ID
  var statusEl = document.getElementById('scan-status');
  var startBtn = document.getElementById('scan-start');
  var scanner = null;
  var handled = false;

  function onScan(decodedText) {
    if (handled) return;
    // Strip all whitespace: the QR holds bare digits, but a grouped "1234 5678 ..." form is
    // what humans read off the label, so tolerate spaces on any future manual-entry path.
    var id = (decodedText || '').replace(/\s/g, '');
    if (!ID_RE.test(id)) {
      statusEl.textContent = 'QR not recognised as a part ID: ' + id;
      return;
    }
    handled = true;
    statusEl.textContent = 'Opening part ' + id + '…';
    // Relative to the page URL (/scan/) so it survives org rename / host changes.
    if (scanner) {
      scanner.stop().catch(function () {}).finally(function () {
        window.location.href = '../p/' + id + '/';
      });
    } else {
      window.location.href = '../p/' + id + '/';
    }
  }

  function start() {
    if (typeof Html5Qrcode === 'undefined') {
      statusEl.textContent = 'Scanner library failed to load.';
      return;
    }
    startBtn.disabled = true;
    statusEl.textContent = 'Starting camera…';
    scanner = new Html5Qrcode('reader');
    scanner.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: 250 },
      onScan,
      function () { /* per-frame decode misses are normal; ignore */ }
    ).then(function () {
      statusEl.textContent = 'Point the camera at a QR code.';
    }).catch(function (err) {
      startBtn.disabled = false;
      statusEl.textContent = 'Could not start camera: ' + err +
        ' (use a real browser and allow camera access).';
    });
  }

  startBtn.addEventListener('click', start);
})();
</script>
