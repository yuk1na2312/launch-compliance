create table public.profiles (
  id uuid primary key references auth.users,
  email text,
  phone_number text,
  date_of_birth date
);
create table public.notes (id bigserial primary key, user_id uuid, body text);
alter table public.notes enable row level security;
