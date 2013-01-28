-- Structural metadata

drop table if exists "location";
create table "location" (
    id uuid primary key,
    longitude float not null,
    latitude float not null,
    radius float default 0 not null,
    elevation integer
);

drop table if exists "project";
create table project (
    id uuid primary key,
    name varchar(255),
    location_id uuid,
    description text
);

drop table if exists "activity";
create table "activity" (
    id uuid primary key,
    name varchar(255),
    project_id uuid,
    location_id uuid,
    description text
);

drop table if exists "study";
create table "study" (
    id uuid primary key,
    name varchar(255),
    description text,
    owner_id uuid not null
);

drop table if exists "activitystudy";
create table "activitystudy" (
    study_id uuid,
    activity_id uuid,
    primary key(study_id, activity_id)
);

drop table if exists lineage;
create table lineage (
    id uuid primary key, 
    from_dataset_id uuid not null, 
    to_dataset_id uuid not null,
    fork_type int not null,                     -- derived or corrected data from lineage
    forked timestamp not null,                  -- timestamp of derivation
    forked_by_id uuid not null,                 -- user id of the fork               
    unique (from_dataset_id, to_dataset_id)
);

-- DATASET
drop table if exists dataset;
create table dataset (
    "id" uuid primary key,
    "type" varchar(255) not null,
    "study_id" uuid not null,
    "created" timestamp not null,
    "creator_id" uuid not null,
    "closed" timestamp,
    "curation_status" int,
    "curated_by_id" uuid,
    "curated" timestamp,
    "description" text
);

-- METADATA
drop table if exists metadata;
create table metadata (
    "id" uuid primary key,
    "dataset_id" uuid not null,               -- dataset uuid
    "metadata_type" int,
    "metadata_handler" int,                   -- handled by the specific data type
    "level" int,                              -- dataset top level or a part of the data
    "created" timestamp not null,             -- time created
    "created_by_id" uuid                      -- uuid of user that created the dataset
);

drop table if exists metadata_annotation;
create table metadata_annotation (
    "id" uuid primary key,
    "metadata_id" uuid not null,
    "annotation" text not null
);

drop table if exists metadata_tag;
create table metadata_tag (
    "id" uuid primary key,
    "metadata_id" uuid not null,
    "tag" varchar(255) not null
);


drop table if exists metadata_keyvalue;
create table metadata_keyvalue (
    "id" uuid primary key,
    "metadata_id" uuid not null,
    "key" varchar(255),
    "holds" int,
    "value_float" float,
    "value_int" int,
    "value_string" text,
    unique ("metadata_id", "key")
);

-- DATA TYPE: FILE
drop table if exists dataset_file;
create table dataset_file (
    id uuid primary key,
    filename text,
    mimetype varchar(255)
);

-- DATA TYPE: SEQUENCE
drop table if exists dataset_sequence;
create table dataset_sequence (
    id uuid primary key,
    dataset_id uuid not null,
    index_type_id uuid not null, 
    index_marker_type integer, 
    index_marker_location integer
);

drop table if exists dataset_type;
create table dataset_type (
    id uuid primary key, 
    name varchar(255) unique, 
    unit varchar(50), 
    description text
);

drop table if exists dataset_sequence_parameter;
create table dataset_sequence_parameter (
    index int not null, 
    sequence_id uuid not null, 
    type_id uuid,
    uncertainty_value float,
    uncertainty_type int,
    storage int,
    primary key(index, sequence_id)
);

drop table if exists dataset_sequence_index;
create table dataset_sequence_index (
    id uuid primary key,
    sequence_id uuid not null,
    location float not null, 
    span float
);

drop table if exists dataset_sequence_point;
create table dataset_sequence_point (
    id uuid primary key, 
    parameter_index integer not null, 
    index_id uuid not null, 
    "value" float not null, 
    uncertainty_value float
);

create index dataset_sequence_point_parameter on dataset_sequence_point(parameter_index);
create index dataset_sequence_point_index on dataset_sequence_point(index_id);

drop table if exists dataset_sequence_metadata;
create table dataset_sequence_metadata (
    id uuid primary key,
    metadata_id uuid not null,
    sequence_id uuid,
    parameter_index int,
    index_id uuid,
    point_id uuid
);


-- AUTH
drop table if exists "user";
create table "user" (
    id uuid primary key not null, 
    username varchar(50) not null,
    fullname varchar(255), 
    email varchar(255) not null, 
    password varchar(60) not null, 
    userlevel integer not null
);

drop table if exists "user_settings";
create table "user_settings" (
    "id" uuid primary key not null,
    "user_id" uuid not null,
    "setting" varchar(255) not null,
    "value" varchar(255)
);

drop table if exists "token";
create table "token" (
    "id" varchar(32) primary key not null, 
    "user_id" uuid not null, 
    "timestamp" integer not null, 
    "validity" integer                              -- seconds of validity of this token, if NULL, always valid
);

drop table if exists "group";
create table "group" (
    "id" uuid primary key, 
    "parent_id" uuid,
    "name" varchar(50) 
);

drop table if exists "group_member";
create table "group_member" (
    "user_id" uuid not null, 
    "group_id" uuid not null,
    primary key("user_id", "group_id")
);

drop table if exists permission;
create table permission (
    user_id uuid, 
    granted_by_id uuid not null,
    granted timestamp not null,
    identifier varchar(255),
    primary key("user_id", "identifier")
);

drop table if exists study_group;
create table study_group (
    "study_id" uuid not null, 
    "group_id" uuid not null,
    "role" int not null,
    primary key("study_id", "group_id")
);

drop table if exists favorite;
create table favorite (
    "id" uuid primary key,
    "name" varchar(255) not null,
    "user_id" uuid not null,
    "ref_id" uuid not null,
    "ref_type" int not null,
    unique("name", "user_id")
);

insert into "user" (id, username, fullname, email, password, userlevel) values ('12345678-90ab-cdef-1234-567890abcdef', 'admin', 'Database Administrator', 'user@example.com', '$2a$12$3xJErTM6NcJSNKSFP5Chxe9O3XnVmA6V8xXpTD2Jr8Srrst.np4AS', 10);
