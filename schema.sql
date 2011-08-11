drop table if exists datapoints;
drop table if exists datasets;
drop table if exists groups;
drop table if exists groupmembers;
drop table if exists lineage;
drop table if exists metadata;
drop table if exists metadata_params;
drop table if exists measurements;
drop table if exists parameters;
drop table if exists permissions;
drop table if exists cores;
drop table if exists corestudies;
drop table if exists sites;
drop table if exists studies;
drop table if exists tokens;
drop table if exists types;
drop table if exists users;

create table types (
    id uuid primary key, 
    name varchar(255) unique, 
    species varchar(50), 
    unit varchar(50), 
    classification integer,
    storage integer,
    description text
);

create table sites (
    id uuid primary key,
    name varchar(255),
    longitude float,
    latitude float,
    elevation integer,
    description text
);

create table cores (
    id uuid primary key,
    name varchar(255),
    site_id uuid,
    longitude float,
    latitude float,
    elevation integer,
    description text
);

create table studies (
    id uuid primary key,
    name varchar(255),
    description text,
    owner_id uuid not null
);

create table corestudies (
    study_id uuid,
    core_id uuid,
    PRIMARY KEY (study_id, core_id)
);

create table datasets (
    id  uuid primary key, 
    study_id uuid, 
    xtype_id uuid, 
    markertype integer, 
    markerlocation integer,
    created timestamp not null,
    closed timestamp,
    description text
);

create table lineage (
    id uuid primary key, 
    from_id uuid not null, 
    to_id uuid not null,
    unique (from_id, to_id)
);

create table parameters (
    id uuid primary key, 
    dataset_id uuid, 
    ytype_id uuid
);

create table measurements (
    id uuid primary key,
    dataset_id uuid not null, 
    x float not null, 
    span float
);

create table datapoints (
    id uuid primary key, 
    parameter_id uuid not null, 
    measurement_id uuid not null, 
    y float not null, 
    quality float
);

create table metadata (
    id uuid primary key,
    dataset_id uuid,
    parameter_id uuid,
    measurement_id uuid,
    datapoint_id uuid,
    created timestamp not null,
    created_by uuid,
    annotation text
);

create table metadata_params (
    id uuid primary key,
    metadata_id uuid,
    key varchar(255),
    value float,
    unique(metadata_id, key)
);

-- permissions and ownership
create table users (
    id uuid primary key, 
    username varchar(50),
    fullname varchar(255), 
    email varchar(255), 
    password varchar(60), 
    userlevel integer not null
);

create table tokens (
    id varchar(32) primary key not null, 
    user_id uuid not null, 
    ts integer not null, 
    valid integer
);

create table groups (
    id uuid primary key, 
    name varchar(50), 
    parent_id uuid
);

create table groupmembers (
    userid integer not null, 
    groupid integer not null
);

create table permissions (
    id uuid primary key, 
    study uuid, 
    permission uuid, 
    groupid uuid
);

-- create users
insert into users 
    
    (id, username, fullname, email, password, userlevel) 
    
    values 
    
    ('12345678-90ab-cdef-1234-567890abcdef', 
     'admin', 
     'Database Administrator', 
     'user@example.com', 
     '$2a$12$3xJErTM6NcJSNKSFP5Chxe9O3XnVmA6V8xXpTD2Jr8Srrst.np4AS', 
     10);


-- create indicies
create index index_measurement_dsid on measurements(dataset_id);
create index index_datapoint_pid on datapoints(parameter_id);
create index index_datapoint_mid on datapoints(measurement_id);
