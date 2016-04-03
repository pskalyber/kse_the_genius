create table if not exists user (
  user_id integer primary key autoincrement,
  username string not null,
  email string not null,
  pw_hash string not null,
  
  munyi_point integer DEFAULT 0,
  munyi_last_quiz integer DEFAULT 0,
  wcyoon_point integer DEFAULT 0,
  wcyoon_last_quiz integer DEFAULT 0,
  uclee_point integer DEFAULT 0,
  uclee_last_quiz integer DEFAULT 0,
  jaegil_point integer DEFAULT 0,
  jaegil_last_quiz integer DEFAULT 0,
  aviv_point integer DEFAULT 0,
  aviv_last_quiz integer DEFAULT 0,
  total_point integer DEFAULT 0
);

create table if not exists quiz (
  quiz_id integer primary key autoincrement,
  professor_id string not null,
  question string not null,
  answer1 integer not null,
  answer2 integer not null,
  answer3 integer not null,
  answer4 integer not null,
  correct_answer string not null,
  quiz_value integer not null
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