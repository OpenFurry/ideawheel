drop table if exists auth_users;
create table auth_users (
	id integer primary key autoincrement,
	username text not null,
	hashword text not null,
	salt integer not null,
	email text not null,
	display_name text,
	blurb text,
	artist_type text,
	is_staff integer default 0,
	is_admin integer default 0
);

drop table if exists idea_stubs;
create table idea_stubs (
	id integer primary key autoincrement,
	stub text,
	link text
);

drop table if exists ideas;
create table ideas (
	id integer primary key autoincrement,
	created_by integer not null,
	display_text text not null,
	plain_text text not null,
	foreign key(created_by) references auth_users(id)
);

drop table if exists ideas_to_idea_stubs;
create table ideas_to_idea_stubs (
	id integer primary key autoincrement,
	idea_stub_id integer not null,
	idea_id integer not null,
	weight integer not null,
	foreign key(idea_stub_id) references idea_stubs(id),
	foreign key(idea_id) references ideas(id)
);

drop table if exists pinned_idea_stub;
create table pinned_idea_stub (
	id integer primary key autoincrement,
	idea_stub_id integer not null,
	user_id integer not null,
	weight integer not null,
	foreign key(idea_stub_id) references idea_stubs(id),
	foreign key(user_id) references auth_users(id)
);

drop table if exists claimed_idea;
create table claimed_idea (
	id integer primary key autoincrement,
	idea_id integer not null,
	user_id integer not null,
	foreign key(idea_id) references ideas(id),
	foreign key(user_id) references auth_users(id)
);

drop table if exists posts;
create table posts (
	id integer primary key autoincrement,
	idea_id integer not null,
	user_id integer not null,
	content text,
	external_link text,
	foreign key(idea_id) references ideas(id),
	foreign key(user_id) references auth_users(id)
);
