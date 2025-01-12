-- migrate:up

create table searchable_content (
  rowid bigint primary key generated always as identity,
  domain64 bigint not null,
  path text not null,
  tag text default 'p' not null,
  content text not null,
  fts tsvector generated always as (to_tsvector('english', content)) STORED
);


create index if not exists idx_gin_bodies on searchable_content 
  using gin (to_tsvector('english', content));
create index if not exists sc_fts_idx on searchable_content using gin (fts);

-- migrate:down

