# A parallel MySQL optimizer

## Usage

    $ optimizer.py <-i include [-i...]> [-x <exclude> [-x...]] [-u user -p pass] <ip:port> <database>...

where the **-i** and **-x** options list the tables which are to be optimized and ignored, respectively. There may be more than one of these options.

Those options accept wildcards, so any of the following syntax is correct:

* % (all tables)
* foo (only the *foo* table)
* foo% (tables starting with *foo*)
* %foo% (tables containing *foo* in the name)
* engine:innodb (only InnoDB storage engine.)
* engine:myisam
* engine:archive
* data\_free:5000 (tables with more than 5KB of free space)

optimizer.py does not write the optimize statements in the binary log, since it runs the `OPTIMIZE LOCAL TABLE` command.

By default 2 parallel optimize commands are executed simultaneously. You can tweak this parameter with the **-n** flag.

## Example

    $ optimizer.py -i engine:innodb -x bigTable -x archive% 10.1.1.1:3306 db1 db2

> Optimize all InnoDB tables, excluding *bigtable* and those starting with *archive*, on databases *db1* and *db2*.

    $ optimizer.py -n 4 -i % 10.1.1.1:3306 db1

> Optimize all tables on *db1*, running 4 parallel optimizes.

## Tips

On an idle database server with fast disks, run *n-1* parallel optimizes, where *n* is the total number of CPU cores installed.

## Other

* [Download latest version](https://github.com/1player/mysqloptimizer/zipball/master)

