// Tags <html> with .is-ios on iPhone/iPad so the homepage can swap the
// Google Play CTA (useless there) for the iOS waitlist. Loaded in <head>,
// synchronously, so the right CTA is showing on first paint. Without JS the
// page falls back to the Android CTA plus a plain link to /ios.
(function () {
  var ua = navigator.userAgent;
  // iPadOS 13+ reports itself as a Mac; the touch screen gives it away.
  var isIOS = /iPhone|iPad|iPod/.test(ua) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  if (isIOS) document.documentElement.classList.add("is-ios");
})();
