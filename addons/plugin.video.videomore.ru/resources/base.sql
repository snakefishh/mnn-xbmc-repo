CREATE TABLE projects (
  id                 integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  project_id         integer NOT NULL,
  title              nvarchar(32),
  category_id        integer NOT NULL,
  channel_ids        integer,
  overall_count      integer,
  tracks_lastupdate  datetime
);
--
CREATE TABLE seasons (
   id                  integer PRIMARY KEY AUTOINCREMENT NOT NULL,
   project_id          integer NOT NULL,
   season              integer,
   pos                 integer,
   title               nvarchar(32) 
)
--
CREATE TABLE tracks (
  id                  integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  project_id          integer NOT NULL,
  season              integer,
  episode_of_season   integer,
  title               nvarchar(255),
  tvurl               nvarchar(255)
);
--
CREATE TABLE settings (
  id          integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
  lastupdate  datetime
);
--
INSERT INTO settings (id) VALUES ("1")
