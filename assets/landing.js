// Landing-page interactions: the voice demo and the sticky mobile CTA.
//
// Both are progressive enhancements -- without JS the demo shows its finished
// list and the sticky CTA simply never appears.

// ---------- Voice demo ----------
//
// Types out the spoken sentence and drops each list item in as soon as the
// words that produce it have been "said". Items name their trigger word in
// data-at.
(function () {
  const demo = document.getElementById("demo");
  if (!demo) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const speech = document.getElementById("demoSpeech");
  const replay = document.getElementById("demoReplay");
  const items = Array.from(demo.querySelectorAll(".list-item"));
  const fullText = speech.textContent.trim();
  let timer = null;

  function reveal(item) {
    item.classList.add("in");
    item.closest(".list-group").classList.add("in");
  }

  function play() {
    clearInterval(timer);
    replay.hidden = true;
    demo.classList.add("armed", "listening");
    demo.querySelectorAll(".in").forEach((el) => el.classList.remove("in"));

    const textNode = document.createTextNode("");
    const caret = document.createElement("span");
    caret.className = "caret";
    speech.replaceChildren(textNode, caret);

    let i = 0;
    timer = setInterval(() => {
      i++;
      textNode.data = fullText.slice(0, i);
      const said = textNode.data.toLowerCase();
      items.forEach((item) => {
        if (!item.classList.contains("in") && said.includes(item.dataset.at)) reveal(item);
      });
      if (i >= fullText.length) {
        clearInterval(timer);
        items.forEach(reveal);
        demo.classList.remove("listening");
        caret.remove();
        replay.hidden = false;
      }
    }, 38);
  }

  // Arm immediately so the list doesn't flash full before the demo starts.
  demo.classList.add("armed");
  speech.textContent = "";

  new IntersectionObserver((entries, obs) => {
    if (entries[0].isIntersecting) {
      obs.disconnect();
      play();
    }
  }, { threshold: 0.4 }).observe(demo);

  replay.addEventListener("click", play);
})();

// ---------- Sticky mobile CTA ----------
//
// Shows once the hero's own CTA has scrolled away, and steps aside while the
// final CTA band is on screen so there are never two buttons at once.
(function () {
  const bar = document.getElementById("mobileCta");
  const heroCta = document.getElementById("heroCta");
  const finalCta = document.getElementById("finalCta");
  if (!bar || !heroCta) return;

  let heroGone = false;
  let finalVisible = false;
  const update = () => bar.classList.toggle("show", heroGone && !finalVisible);

  new IntersectionObserver(([e]) => {
    heroGone = !e.isIntersecting && e.boundingClientRect.top < 0;
    update();
  }).observe(heroCta);

  if (finalCta) {
    new IntersectionObserver(([e]) => {
      finalVisible = e.isIntersecting;
      update();
    }).observe(finalCta);
  }
})();

// ---------- "Join the waitlist" buttons (ios.html) ----------
//
// Jumping back to the form isn't enough on a phone; open the keyboard too.
(function () {
  const email = document.getElementById("wlEmail");
  if (!email) return;
  document.querySelectorAll('a[href="#join"]').forEach((a) => {
    a.addEventListener("click", () => email.focus({ preventScroll: true }));
  });
})();
