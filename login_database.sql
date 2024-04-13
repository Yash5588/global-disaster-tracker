create table login_details(
    username varchar(255) not null,
    email varchar(255),
    password text not null,
    contact varchar(255) not null,
    unique(username),
    unique(contact),
    primary key (email)
);

alter table login_details modify column password varchar(255);
desc login_details;
alter table login_details modify column password varchar(255) not null unique;

use disaster;
select * from login_details;

use disaster;
delete from login_details;

use disaster;
alter table login_details add constraint uni_pass_cont unique(password,contact);

use disaster;
alter table login_details drop index password;

desc login_details

alter table login_details drop column contact

alter table login_details add password varchar(255) not null;
alter table login_details add contact varchar(255) not null;