drop table if exists assignments;
create table assignments (
  id integer primary key autoincrement,
  title text not null,
  class text not null,
  category text not null,
  duedate date not null,
  description text not null
);