# A multithreaded MySQL optimizer

## Usage

    $ optimizer.py <-i include [-i ...]> [-x <exclude> [-x ...]] <ip:port> <database>...

where **-i** and **-x** list the tables with are to be optimized and ignored, respectively.

Those options accept wildcards, so any of the following syntax is correct:
* foo (only the *foo* table)
* foo% (tables starting with *foo*)
* %foo% (tables containing *foo* in the name)
* engine:innodb (only InnoDB storage engine.)
* engine:myisam
* engine:archive
* data\_free:5000 (tables with more than 5KB of free space)
