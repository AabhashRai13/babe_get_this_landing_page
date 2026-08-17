// Account deletion form.
//
// Same project + flow as the Android app: sign in, then call the
// security-definer Postgres function delete_user (anon key can't touch
// auth.users directly). The anon key is safe to publish.
const SUPABASE_URL = "https://fpzjyusgqdzqituokrwq.supabase.co";
const SUPABASE_ANON_KEY = "sb_publishable_iZuhs5tTaIM5-6790l589g_vKdbzWJD";

const form = document.getElementById("delForm");
const fallback = document.getElementById("delFallback");
const status = document.getElementById("delStatus");
const btn = document.getElementById("delBtn");

if (SUPABASE_URL && SUPABASE_ANON_KEY && window.supabase) {
  const client = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  form.hidden = false;
  fallback.hidden = true;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!confirm("Really delete your account forever? This cannot be undone.")) return;

    btn.disabled = true;
    status.className = "status";
    status.textContent = "Deleting your account…";

    const email = document.getElementById("delEmail").value.trim();
    const password = document.getElementById("delPassword").value;

    try {
      const { error: signInError } = await client.auth.signInWithPassword({ email, password });
      if (signInError) throw new Error("Sign-in failed — check your email and password.");

      const { error: rpcError } = await client.rpc("delete_user");
      if (rpcError) throw new Error("Deletion failed. Please try again or email us and we'll handle it.");

      await client.auth.signOut().catch(() => {});
      form.reset();
      status.className = "status ok";
      status.textContent = "Your account has been deleted. Sorry to see you go 💔";
    } catch (err) {
      status.className = "status err";
      status.textContent = err.message;
    } finally {
      btn.disabled = false;
    }
  });
}
