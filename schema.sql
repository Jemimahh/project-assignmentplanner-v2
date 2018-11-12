drop table if exists assignments;
create table assignments (
  id integer primary key autoincrement,
  title text not null,
  class text not null,
  category text not null,
  duedate text not null,
  description text not null
);