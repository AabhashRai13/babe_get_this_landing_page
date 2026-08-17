// Landing-page waitlist signup.
//
// Straight to PostgREST -- no supabase-js needed for one insert.
// The anon key is public by design; RLS grants insert and nothing else,
// and a trigger rate limits by IP. See supabase/waitlist.sql.
const WAITLIST_URL = "https://fpzjyusgqdzqituokrwq.supabase.co/rest/v1/waitlist";
const SUPABASE_ANON_KEY = "sb_publishable_iZuhs5tTaIM5-6790l589g_vKdbzWJD";

const wlForm = document.getElementById("wlForm");
const wlEmail = document.getElementById("wlEmail");
const wlBtn = document.getElementById("wlBtn");
const wlStatus = document.getElementById("wlStatus");

function setStatus(kind, text) {
  wlStatus.className = kind ? "status " + kind : "status";
  wlStatus.textContent = text;
}

wlForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Bots fill every field they see; humans never see this one.
  if (document.getElementById("wlCompany").value) return;

  const email = wlEmail.value.trim();
  if (!wlEmail.checkValidity() || !email) {
    setStatus("err", "That email doesn't look right.");
    wlEmail.focus();
    return;
  }

  wlBtn.disabled = true;
  setStatus("", "Adding you…");

  try {
    const res = await fetch(WAITLIST_URL, {
      method: "POST",
      headers: {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": "Bearer " + SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        // minimal: nothing comes back, so no select policy is needed.
        // Deliberately NOT resolution=ignore-duplicates -- PostgREST turns
        // that into ON CONFLICT DO NOTHING, which Postgres can only
        // evaluate with a SELECT policy on the table. We don't have one
        // (by design), so it fails RLS. A repeat email 409s instead.
        "Prefer": "return=minimal"
      },
      body: JSON.stringify({ email, source: "landing" })
    });

    if (res.ok) {
      wlForm.reset();
      setStatus("ok", "You're on the list 💌 We'll email you the day it lands.");
      return;
    }

    // 409 = primary key conflict, i.e. already signed up. Nothing was
    // changed; their original signup date is intact.
    if (res.status === 409) {
      wlForm.reset();
      setStatus("ok", "You're already on the list 🥰 Thanks for being as excited as we are — we'll email you the day it lands.");
      return;
    }

    const body = await res.text();
    setStatus("err", body.includes("rate limited")
      ? "Too many signups from your network. Try again in an hour."
      : "That didn't go through. Email us at contactus@babegetthis.com and we'll add you.");
  } catch {
    setStatus("err", "Network error — check your connection and try again.");
  } finally {
    wlBtn.disabled = false;
  }
});
