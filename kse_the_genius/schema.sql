create table if not exists user (
  user_id integer primary key autoincrement,
  username string not null,
  email string not null,
  pw_hash string not null
);


create table if not exists follower (
  who_id integer,
  whom_id integer
);

create table if not exists post (
  post_id integer primary key autoincrement,
  author_id integer not null,
  title string not null,
  text string not null,
  publish_date integer not null,
  accident_date_from integer not null,
  accident_date_to integer not null,
  location_latitude double not null,
  location_longitude double not null,
  read_count integer DEFAULT 0,
  img_url string
);