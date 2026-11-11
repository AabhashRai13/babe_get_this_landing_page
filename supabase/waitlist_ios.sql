-- iOS waitlist: reuses the existing public.waitlist table (see waitlist.sql).
--
-- Run once in the Supabase SQL editor, AFTER waitlist.sql has been deployed.
-- Do NOT re-run waitlist.sql for this -- it would overwrite waitlist_guard()
-- and its real salt with the TODO placeholder.
--
-- The Android pre-launch signups stay in the same table, tagged 'android'.
-- Email alone can no longer be the key: someone who joined the Android list
-- must still be able to join the iOS one, so the key becomes (email, platform).
-- A repeat signup for the same platform still 409s, which the page shows as
-- "already on the list".

begin;

alter table public.waitlist
  add column if not exists platform text not null default 'android';

-- Existing rows are backfilled as 'android' by the default above. Drop it so
-- new signups must say which platform they want.
alter table public.waitlist alter column platform drop default;

alter table public.waitlist drop constraint if exists waitlist_platform_check;
alter table public.waitlist
  add constraint waitlist_platform_check check (platform in ('android', 'ios'));

alter table public.waitlist drop constraint if exists waitlist_pkey;
alter table public.waitlist add primary key (email, platform);

-- Grants, the insert-only RLS policy, and the rate-limit trigger are
-- table-level, so they already cover the new column. Nothing else to change.

commit;
