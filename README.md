# babegetthis.com

Marketing and legal site for **Babe, Get This** — a voice-powered shopping list app for couples (Android).

Plain static site: no build step, no framework.

## Pages

| File | Purpose |
|---|---|
| `index.html` | Landing page |
| `privacy-policy.html` | Privacy policy (linked from Google Play) |
| `terms.html` | Terms of service |
| `delete-account.html` | Self-service account deletion (required by Google Play) |

## Run locally

```sh
npx serve .
```

Then open http://localhost:3000. (Opening the `.html` files directly from disk also works — all paths are relative.)

## Deploy

Hosted on Hostinger. Upload everything (including `.htaccess` and `assets/`) into `public_html`. The `.htaccess` forces HTTPS, enables extensionless URLs (`/privacy-policy`), and sets basic caching.

## Supabase keys — safe to commit

`delete-account.html` contains the Supabase **project URL** and **publishable (anon) key**. These are intentionally public — the same values ship inside the Android APK, and all real security lives in Supabase (row-level security and the `delete_user` security-definer function, which only ever deletes the calling user's own account).

⚠️ Never put the Supabase **`service_role`** key (or any `sb_secret_...` key) in this repo or anywhere client-side — it bypasses all row-level security.

## Related

- Android app repo: `Babe-get-this`
- Contact: raiaabhash3@gmail.com
