-- Waitlist for the pre-launch landing page (index.html).
--
-- Threat model: the anon key is public (it ships in the APK and in the page
-- source), so anyone can POST to this table. RLS below grants INSERT and
-- nothing else -- no one can read, edit, or delete the list. The trigger caps
-- how fast a single IP can insert, which is the part that actually stops spam.
--
-- Run once in the Supabase SQL editor. Before running, replace the salt marked
-- TODO below with the output of `openssl rand -hex 32`. Do NOT commit the real
-- salt -- this repo is public, and a published salt makes the stored IP hashes
-- reversible. The guard at the bottom refuses to deploy with the placeholder.

create table if not exists public.waitlist (
  email      text primary key,
  source     text,
  ip_hash    text,
  created_at timestamptz not null default now(),
  constraint waitlist_email_shape check (
    email ~* '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'
    and length(email) <= 254
  )
);

-- The rate-limit lookup runs on every insert; keep it index-only.
create index if not exists waitlist_ip_recent
  on public.waitlist (ip_hash, created_at desc);

alter table public.waitlist enable row level security;

-- Supabase grants anon/authenticated full CRUD on new public tables by
-- default; only the absence of policies was blocking reads. Drop the grants we
-- never use, so exposing the list would take two mistakes instead of one.
revoke all on public.waitlist from anon, authenticated;
grant insert on public.waitlist to anon, authenticated;

-- INSERT only. Deliberately no select/update/delete policy: a caller can add
-- itself to the list but can never read the list back.
--
-- Consequence: clients must NOT send `Prefer: resolution=ignore-duplicates`.
-- PostgREST compiles it to ON CONFLICT DO NOTHING, which Postgres can only
-- evaluate with a SELECT policy present, so it fails RLS. Let repeat signups
-- 409 on the primary key instead -- index.html shows a friendly "already on
-- the list" for that. The 409 does tell a caller whether an address is on the
-- list; the per-IP rate limit below keeps that from being useful at scale.
drop policy if exists "anon can join waitlist" on public.waitlist;
drop policy if exists "anyone can join waitlist" on public.waitlist;
create policy "anyone can join waitlist"
  on public.waitlist for insert to public
  with check (true);

-- Normalises the row and rate limits by client IP.
-- security definer so it can count existing rows despite the no-select policy.
create or replace function public.waitlist_guard()
returns trigger
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  headers json := nullif(current_setting('request.headers', true), '')::json;
  xff     text := headers ->> 'x-forwarded-for';
  client_ip text;
  recent  integer;
  max_per_hour constant integer := 3;
begin
  -- Cloudflare sets cf-connecting-ip itself and appends the true client IP to
  -- the end of x-forwarded-for, so take the LAST entry -- earlier ones can be
  -- forged by the caller.
  client_ip := coalesce(
    nullif(btrim(headers ->> 'cf-connecting-ip'), ''),
    nullif(btrim(split_part(xff, ',', array_length(string_to_array(xff, ','), 1))), ''),
    'unknown'
  );

  -- ponytail: md5 + static salt is a privacy bucket, not a security hash. It
  -- keeps raw IPs out of the table while still grouping repeat submitters.
  new.ip_hash    := md5(client_ip || 'TODO-replace-with-a-long-random-string');
  new.email      := lower(btrim(new.email));
  new.source     := left(coalesce(new.source, 'unknown'), 32);
  new.created_at := now();  -- ignore any client-supplied timestamp

  select count(*) into recent
    from public.waitlist
   where ip_hash = new.ip_hash
     and created_at > now() - interval '1 hour';

  if recent >= max_per_hour then
    raise exception 'rate limited' using errcode = 'P0001';
  end if;

  return new;
end;
$$;

drop trigger if exists waitlist_guard_trg on public.waitlist;
create trigger waitlist_guard_trg
  before insert on public.waitlist
  for each row execute function public.waitlist_guard();

-- Deploy guard: this repo is public, so a committed salt would be a published
-- salt. Abort (and roll the whole script back) rather than silently going live
-- with a salt anyone can read on GitHub.
do $$
begin
  if pg_get_functiondef('public.waitlist_guard()'::regprocedure)
       like '%TODO-replace-with-a-long-random-string%' then
    raise exception
      'Replace the TODO salt in waitlist_guard() with the output of `openssl rand -hex 32` before deploying.';
  end if;
end $$;
