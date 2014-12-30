use candy;
create table KeyStats (symbol varchar(16), lastdate DATE, high5d double, low5d double, high10d double, low10d double,high20d double, low20d double, high50d double,low50d double,high52w double, low52w double, primary key(symbol));
create table StockMetadata (symbol varchar(16), lastdate DATE, p1 varchar(16),p2 varchar(16),p3 varchar(16),p4 varchar(16),p5 varchar(16),p6 varchar(16),p7 varchar(16),p8 varchar(16),p9 varchar(16),p10 varchar(16),primary key(symbol));
create table StockMetadata (symbol varchar(16), lastdate DATE, portfolio varchar(16),primary key(symbol,portfolio));
create table Perfdata (symbol varchar(16), lastdate DATE, annualperf double,y5d double,y2d double,y1d double,ytd double,td200 double,td100 double,td50 double,td20 double,td10 double, td5 double,primary key(symbol));
create table Stocklist (symbol varchar(16), name varchar(64), lastprice float, marketcap BIGINT,sector varchar(32), industry varchar(64), primary key(symbol));