create schema usermodel;

create table
  usermodel.orgs (org_id text primary key, org_name text, created_at timestamptz default current_timestamp, updated_at timestamptz default current_timestamp);

create table
  usermodel.users (user_id text primary key, created_at timestamptz default current_timestamp, updated_at timestamptz default current_timestamp);

create table
  usermodel.roles (role text primary key, ui_visible boolean not null);

create table
  usermodel.user_org (
    user_id text primary key
  , org_id text
  , role text not null
  , foreign key (user_id) references usermodel.users (user_id)
  , foreign key (org_id) references usermodel.orgs (org_id)
  , foreign key (role) references usermodel.roles (role)
  );

insert into
  usermodel.roles (role, ui_visible)
values
  ('owner', true)
, ('viewer', true);

create table
  usermodel.google_account (
    sub text primary key
  , email text
  , email_verified boolean
  , hd text
  , name text
  , picture text
  , given_name text
  , family_name text
  , created_at timestamptz not null default current_timestamp
  , updated_at timestamptz not null default current_timestamp
  );

create table
  usermodel.user_google (user_id text primary key, sub text unique not null, foreign key (user_id) references usermodel.users (user_id), foreign key (sub) references usermodel.google_account (sub));

-- Data
-- Insert into orgs
insert into
  usermodel.orgs (org_id, org_name)
values
  ('org_a1b2c3d4e5f6', 'Organization One');

-- Insert into users
insert into
  usermodel.users (user_id)
values
  ('u_1a2b3c4d5e6f')
, ('u_2b3c4d5e6f7a')
, ('u_3c4d5e6f7a8b');

-- Insert into user_org
insert into
  usermodel.user_org (user_id, org_id, role)
values
  ('u_1a2b3c4d5e6f', 'org_a1b2c3d4e5f6', 'owner')
, ('u_2b3c4d5e6f7a', 'org_a1b2c3d4e5f6', 'viewer')
, ('u_3c4d5e6f7a8b', 'org_a1b2c3d4e5f6', 'viewer');

-- Insert into google_account
insert into
  usermodel.google_account (sub, email, email_verified, hd, name, picture, given_name, family_name)
values
  ('sub_4d5e6f7a8b9c', 'user1@example.com', true, 'example.com', 'User One', 'https://example.com/user1.jpg', 'User', 'One')
, ('sub_5e6f7a8b9c0d', 'user2@example.com', true, 'example.com', 'User Two', 'https://example.com/user2.jpg', 'User', 'Two')
, ('sub_6f7a8b9c0d1e', 'user3@example.com', true, 'example.com', 'User Three', 'https://example.com/user3.jpg', 'User', 'Three');

-- Insert into user_google
insert into
  usermodel.user_google (user_id, sub)
values
  ('u_1a2b3c4d5e6f', 'sub_4d5e6f7a8b9c')
, ('u_2b3c4d5e6f7a', 'sub_5e6f7a8b9c0d')
, ('u_3c4d5e6f7a8b', 'sub_6f7a8b9c0d1e');