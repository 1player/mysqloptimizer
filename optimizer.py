#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MySQL Multithreaded Optimizer
# Designed by steph@combo.cc
#

from optparse import OptionParser
import Queue
from math import ceil
import MySQLdb
import re
import sys
import time
import random
import signal
import threading

working_queue = Queue.Queue()
running = True

class OptimizerThread(threading.Thread):
    def __init__(self, conn, id):
        self.conn = conn
        threading.Thread.__init__(self, name='%u' % id)

    def run(self):
        c = self.conn.cursor()

        while running:
            try:
                db, table = working_queue.get(False)
            except Queue.Empty:
                return

            print 'Optimizing %s:%s (thread %s)...' % (db, table, self.getName())
            sys.stdout.flush()

            c.execute('OPTIMIZE LOCAL TABLE %s.%s' % (db, table))
            c.fetchall()

def process_expression(expr_list, tables_status):
    if expr_list is None:
        return []

    matching = []

    for expr in expr_list:
        if expr.find(':') != -1:
            option, value = expr.split(':')

            if option == 'engine':
                matching += [x['name'] for x in filter(lambda x: x['engine'] == value, tables_status)]

            elif option == 'data_free':
                value = int(value)
                matching += [x['name'] for x in filter(lambda x: x['data_free'] > value, tables_status)]

            else:
                print 'not supported'
                sys.exit(1)

        elif expr.find('%') != -1:
            regex = re.compile(expr.replace('%', '.*'), re.I)
            matching += [x['name'] for x in filter(lambda x: regex.match(x['name']) is not None, tables_status)]

        else:
            matching += [x['name'] for x in filter(lambda x: x['name'] == expr, tables_status)]

    return matching

def connect_to_instance(instance_id, user, passwd):
    ipport_match = re.match('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+):([0-9]+)', instance_id)
    if ipport_match:
        ip, port = ipport_match.groups()
        port = int(port)
        conn = MySQLdb.connect(host=ip, port=port, user=user, passwd=passwd)

        return conn

    else:
        print >>sys.stderr, 'Host format not recognized: it should be ip:port'
        sys.exit(1)

    return None

def parse_arguments():
    parser = OptionParser(usage='usage: %prog [options] <ip:port> <databases...>')
    parser.add_option('-n', '--threads', dest='thread_count', help='number of parallel OPTIMIZEs', type='int', default=2)
    parser.add_option('-i', '--include', dest='include_clauses', help='include the specified tables', action='append')
    parser.add_option('-x', '--exclude', dest='exclude_clauses', help='exclude the specified tables', action='append')
    parser.add_option('-t', '--test', dest='test_run', help='show what would be optimized, no operation on the database is done', action='store_true', default=False)
    parser.add_option('-q', '--quiet', dest='quiet', help='only print errors', action='store_true', default=False)
    parser.add_option('-u', '--user', dest='user', help='user to connect with')
    parser.add_option('-p', '--password', dest='password', help='password to connect with', default='')

    options, args = parser.parse_args()

    if len(args) < 1:
        parser.error('No MySQL IP and port specified.')
    elif len(args) < 2:
        parser.error('No database to optimize specified.')

    if not options.user:
        parser.error('No MySQL user specified.')

    instance_id = args[0]
    databases = args[1:]

    return (options, instance_id, databases)

def main():
    options, instance_id, databases = parse_arguments()

    conn = connect_to_instance(instance_id, options.user, options.password)
    assert(conn is not None)

    c = conn.cursor()
    c.execute('SELECT VERSION()')
    instance_version = c.fetchone()[0]

    for db in databases:
        print 'Reading table status from %s' % db
        sys.stdout.flush()

        c.execute('USE %s' % db)
        c.execute('SHOW TABLE STATUS')

        tables_status = []

        for row in c.fetchall():
            try:
                table_name = row[0]
                engine = row[1].lower()
                if instance_version.startswith('4.0'):
                    type = row[2].lower()
                    data_free = row[8]
                elif instance_version.startswith('4.1') or instance_version.startswith('5'):
                    type = row[3].lower()
                    data_free = row[9]
                else:
                    print >>sys.stderr, 'MySQL version %s not supported yet.' % instance_version
                    sys.exit(1)

                # exclude unsupported engines (merges, blackhole, etc.)
                if engine not in ['innodb', 'myisam', 'archive']:
                    continue

                # exclude compressed tables
                if engine == 'myisam' and type == 'compressed':
                    continue

            except:
                continue

            table_status = {'name': table_name, 'engine': engine, 'type': type, 'data_free': data_free}

            tables_status.append( table_status )

        tables_to_process = set(process_expression(options.include_clauses, tables_status))
        tables_to_process -= set(process_expression(options.exclude_clauses, tables_status))

        for table in sorted(tables_to_process):
            if options.test_run:
                print 'Optimizing %s.%s' % (db, table)
            else:
                working_queue.put( (db, table) )

    conn.close()

    if options.test_run == False:

        # create the worker threads
        for i in xrange(options.thread_count):
            thread_connection = connect_to_instance(instance_id, options.user, options.password)
            thread = OptimizerThread(thread_connection, i + 1)
            thread.start()

        try:
            while True:
                time.sleep(1)
            
                if threading.activeCount() == 1:
                    break

        except KeyboardInterrupt:
            print 'Stopping...'
            running = False


################################################

if __name__ == '__main__':
    main()
