-- Eseguire per primo nel SQL Editor di Supabase, poi seed.sql
create table if not exists teams (id int primary key, nome text not null);
create table if not exists players (
  id serial primary key,
  team_id int not null references teams on delete cascade,
  nome text not null,
  ruolo char(1) not null check (ruolo in ('P','D','C','A')),
  costo int not null
);
-- presenza della riga = giocatore in lista trasferimento
create table if not exists transfer_list (
  player_id int primary key references players on delete cascade,
  created_at timestamptz not null default now()
);
-- presenza della riga = la squadra cerca quel ruolo
create table if not exists wanted_roles (
  team_id int references teams on delete cascade,
  ruolo char(1) check (ruolo in ('P','D','C','A')),
  primary key (team_id, ruolo)
);

alter table teams enable row level security;
alter table players enable row level security;
alter table transfer_list enable row level security;
alter table wanted_roles enable row level security;

-- Nessun login (scelta utente): rose in sola lettura, liste modificabili da chiunque abbia il link
create policy "read" on teams for select to anon using (true);
create policy "read" on players for select to anon using (true);
create policy "all" on transfer_list for all to anon using (true) with check (true);
create policy "all" on wanted_roles for all to anon using (true) with check (true);

-- Privilegi espliciti: il progetto non li concede in automatico alle nuove tabelle
grant usage on schema public to anon;
grant select on teams, players to anon;
grant select, insert, update, delete on transfer_list, wanted_roles to anon;

-- Realtime per la bacheca
alter publication supabase_realtime add table transfer_list, wanted_roles;
