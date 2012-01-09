-- Structural metadata

drop table if exists "project";
create table project (
    id uuid primary key,
    name varchar(255),
    longitude float,
    latitude float,
    radius float,
    elevation integer,
    description text
);

drop table if exists "activity";
create table "activity" (
    id uuid primary key,
    name varchar(255),
    project_id uuid,
    activity_type int,
    longitude float,
    latitude float,
    radius float,
    elevation integer,
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


-- Dataset
drop table if exists dataset;
create table dataset (
    id uuid primary key,
    "type" varchar(255) not null,
    created timestamp not null,
    closed timestamp,
    curation_status int,
    curated_by_id uuid,
    curated timestamp,
    description text
);

-- METADATA

drop table if exists metadata;
create table metadata (
    id uuid primary key,
    dataset_id uuid not null,               -- dataset uuid
    "type" varchar(255) not null,           -- metadata type
    "level" int,                            -- top level or dataset type dependent
    created timestamp not null,             -- time created
    created_by_id uuid                      -- uuid of user that created the dataset
);

drop table if exists metadata_annotation;
create table metadata_annotation (
    id uuid primary key,
    metadata_id uuid not null,
    annotation text not null
);

drop table if exists metadata_tag;
create table metadata_tag (
    id uuid primary key,
    metadata_id uuid not null,
    tag varchar(255) not null
);

drop table if exists metadata_link_activity;
create table metadata_link_activity (
    id uuid primary key,
    metadata_id uuid not null,
    activity_id uuid not null
);

drop table if exists metadata_link_study;
create table metadata_link_study (
    id uuid primary key,
    metadata_id uuid not null,
    study_id uuid not null
);

drop table if exists metadata_keyvaluestore;
create table metadata_keyvaluestore (
    id uuid primary key,
    metadata_id uuid not null,
    name varchar(255) not null
);

drop table if exists metadata_keyvalue_float;
create table metadata_keyvalue_float (
    id uuid primary key,
    keyvaluestore_id uuid not null,
    "key" varchar(255),
    "value" float
);

drop table if exists metadata_keyvalue_int;
create table metadata_keyvalue_int (
    id uuid primary key,
    keyvaluestore_id uuid not null,
    "key" varchar(255),
    "value" float
);

drop table if exists metadata_keyvalue_string;
create table metadata_keyvalue_string (
    id uuid primary key,
    keyvaluestore_id uuid not null,
    "key" varchar(255),
    "value" text
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

drop table if exists dataset_sequence_type;
create table dataset_sequence_type (
    id uuid primary key, 
    name varchar(255) unique, 
    unit varchar(50), 
    storage integer,
    description text
);

drop table if exists dataset_sequence_parameter;
create table dataset_sequence_parameter (
    id uuid primary key, 
    dataset_id uuid not null, 
    type_id uuid
);

drop table if exists dataset_sequence_index;
create table dataset_sequence_index (
    id uuid primary key,
    location float not null, 
    span float
);

drop table if exists dataset_sequence_point;
create table dataset_sequence_point (
    id uuid primary key, 
    parameter_id uuid not null, 
    index_id uuid not null, 
    "value" float not null, 
    quality float
);

create index dataset_sequence_point_parameter on dataset_sequence_point(parameter_id);
create index dataset_sequence_point_index on dataset_sequence_point(index_id);

drop table if exists dataset_sequence_metadata;
create table dataset_sequence_metadata (
    id uuid primary key,
    metadata_id uuid not null,
    dataset_id uuid,
    parameter_id uuid,
    index_id uuid,
    point_id uuid
);


-- System tables: permissions and ownership
drop table if exists "user";
create table "user" (
    id uuid primary key, 
    username varchar(50),
    fullname varchar(255), 
    email varchar(255), 
    password varchar(60), 
    userlevel integer not null
);

drop table if exists token;
create table token (
    id varchar(32) primary key not null, 
    user_id uuid not null, 
    "timestamp" integer not null, 
    validity integer
);

drop table if exists "group";
create table "group" (
    id uuid primary key, 
    parent_id uuid,
    name varchar(50) 
);

drop table if exists group_member;
create table group_member (
    user_id integer not null, 
    group_id integer not null
);

drop table if exists permission;
create table permission (
    id uuid primary key, 
    study_id uuid, 
    permission_id uuid, 
    group_id uuid
);

insert into "user" (id, username, fullname, email, password, userlevel) values ('12345678-90ab-cdef-1234-567890abcdef', 'admin', 'Database Administrator', 'user@example.com', '$2a$12$3xJErTM6NcJSNKSFP5Chxe9O3XnVmA6V8xXpTD2Jr8Srrst.np4AS', 10);

