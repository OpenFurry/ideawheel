drop table if exists auth_users;
create table auth_users (
	id integer primary key autoincrement,
	username text unique not null,
	hashword text not null,
	salt integer not null,
	email text not null,
	display_name text,
	blurb text,
	artist_type text,
	is_staff integer default 0,
	is_admin integer default 0
);
create unique index user_login_idx ON auth_users(username, salt, hashword);

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
	title text,
	format text,
	post_date text,
	content text,
	external_link text,
	foreign key(idea_id) references ideas(id),
	foreign key(user_id) references auth_users(id)
);

drop table if exists suspensions;
create table suspensions (
	id integer primary key autoincrement,
	object_id integer not null,
	object_type text not null, -- user, stub, idea, or post
	suspended_by integer not null,
	start_date text not null,
	end_date text,
	active boolean default true,
	reason text not null default "This {0} has been suspended by {1}, no reason given", -- {0}: object type, {1}: staff/admin name
	foreign key(suspended_by) references auth_users(id)
);
create unique index suspension_idx on suspensions (object_id, object_type, active);
