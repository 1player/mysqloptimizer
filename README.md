# A parallel MySQL optimizer

## Usage

    $ optimizer.py <-i include [-i ...]> [-x <exclude> [-x ...]] <ip:port> <database>...

where **-i** and **-x** list the tables with are to be optimized and ignored, respectively.

Those options accept wildcards, so any of the following syntax is correct:

* % (all tables)
* foo (only the *foo* table)
* foo% (tables starting with *foo*)
* %foo% (tables containing *foo* in the name)
* engine:innodb (only InnoDB storage engine.)
* engine:myisam
* engine:archive
* data\_free:5000 (tables with more than 5KB of free space)

Optimizes are local to the database server, by using with the `OPTIMIZE LOCAL TABLE` statement.

## Example

    $ optimizer.py -i engine:innodb -x bigTable 10.1.1.1:3306 db1 db2

> Optimize all InnoDB tables, excluding *bigtable*, on databases *db1* and *db2*.

    $ optimizer.py -n 4 -i % 10.1.1.1:3306 db1

> Optimize all tables on *db1*, running 4 parallel optimizes.

## Tips

On an idle database server with fast disks, run *n-1* parallel optimizes, where *n* is the total number of CPU cores installed.

## Other

* [Bugs and issues](https://bitbucket.org/eazy/mysqloptimizer/issues?status=new&status=open)
* [Download latest version](https://bitbucket.org/eazy/mysqloptimizer/get/tip.tar.gz)

