%Test datajoint installation
dj.version

%Connect to datajoint database
setenv('DJ_HOST','ucsd-demo-db.datajoint.io');
setenv('DJ_USER','conrad');
setenv('DJ_PASS','pw4dklab');
dj.conn();

%Load schema (from yesterday)
dj.createSchema(); %The database name we are using right now is conrad_test

%{
%Define a new class
dj.new();

%Grab data in table
fetch(ctest.Mouse,'*');
%}