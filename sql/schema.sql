create schema usermodel;

create table
    usermodel.orgs (
        org_id text primary key,
        org_name text,
        created_at timestamptz default current_timestamp,
        updated_at timestamptz default current_timestamp
    );

create table
    usermodel.users (
        user_id text primary key,
        created_at timestamptz default current_timestamp,
        updated_at timestamptz default current_timestamp
    );

create table
    usermodel.roles (
        role text primary key,
        ui_visible boolean not null
    );

create table
    usermodel.user_org (
        user_id text primary key,
        org_id text,
        role text not null,
        foreign key (user_id) references usermodel.users (user_id),
        foreign key (org_id) references usermodel.orgs (org_id),
        foreign key (role) references usermodel.roles (role)
    );

insert into
    usermodel.roles (role, ui_visible)
values
    ('owner', true),
    ('viewer', true);

create table
    usermodel.google_account (
        sub text primary key,
        email text,
        email_verified boolean,
        hd text,
        name text,
        picture text,
        given_name text,
        family_name text,
        created_at timestamptz not null default current_timestamp,
        updated_at timestamptz not null default current_timestamp
    );

create table
    usermodel.user_google (
        user_id text primary key,
        sub text unique not null,
        foreign key (user_id) references usermodel.users (user_id),
        foreign key (sub) references usermodel.google_account (sub)
    );

-- Data
insert into
    usermodel.users (user_id)
values
    ('u_361d2473af5d');

insert into
    usermodel.orgs (org_id, org_name)
values
    ('org_261d6673ae4c', 'test org');