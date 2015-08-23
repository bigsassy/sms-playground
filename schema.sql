drop table if exists entries;

create table conversation (
  id integer primary key autoincrement,
  created_at text not null,  -- when the initial text is captured by the server
  started_at text not null,  -- when a program starts a conversation with this user from this message
  sid text not null,
  body text not null,
  from_ text not null,
  conversation_code text null,
);
