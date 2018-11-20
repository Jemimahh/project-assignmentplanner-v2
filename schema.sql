drop table if exists accounts;
create table accounts (
  id integer primary key autoincrement,
  username text not null,
  password text not null
);

drop table if exists assignments;
create table assignments (
  id integer primary key autoincrement,
  title text not null,
  course text not null,
  category text not null,
  duedate text not null,
  description text not null
);