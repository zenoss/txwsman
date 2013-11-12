##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in the LICENSE
# file at the top-level directory of this package.
#
##############################################################################

"""
Use twisted web client to enumerate/pull WQL query.
"""

import sys
from twisted.internet import defer
from . import app
from .enumerate import create_wsman_client

class WsmanStrategy(object):

    def __init__(self):
        self._item_count = 0

    @property
    def count_summary(self):
        return '{0} items'.format(self._item_count)


    def _print_items(self, items, hostname, className, include_header):
        if include_header:
            print '\n', hostname, "==>", className
            indent = '  '
        else:
            indent = ''
        is_first_item = True
        for item in items:
            if is_first_item:
                is_first_item = False
            else:
                print '{0}{1}'.format(indent, '-' * 4)
            for name, value in vars(item).iteritems():
                self._item_count += 1
                text = value
                if isinstance(value, list):
                    text = ', '.join(value)
                print '{0}{1} = {2}'.format(indent, name, text)

    def act(self, good_conn_infos, args, config):
        include_header = len(config.conn_infos) > 1
        ds = []
        for conn_info in good_conn_infos:
            client = create_wsman_client(conn_info)
            d = client.enumerate(config.className,
                                 mode=config.mode,
                                 ext=config.ext,
                                 wql=config.wql,
                                 maxelements=config.maxelements,
                                 namespace=config.namespace)
            d.addCallback(self._print_items, conn_info.hostname, config.className, include_header)
            
            ds.append(d)
        return defer.DeferredList(ds, consumeErrors=True)




class WsmanUtility(app.ConfigDrivenUtility):

    def add_args(self, parser):
        parser.add_argument("--wql", "-w")
        parser.add_argument("--className", "-C")
        parser.add_argument("--namespace", "-n")
        parser.add_argument("--mode", "-m")
        parser.add_argument("--references", "-r")
        parser.add_argument("--ext", "-e", action="store_true")
        parser.add_argument("--max", "-M")

    def check_args(self, args):
        legit = args.config or args.className
        if not legit:
            print >>sys.stderr, "ERROR: You must specify a config file with " \
                                "-c or specify a class with -C"
            sys.exit(1)

        if args.mode:
            mode = args.mode
            if mode not in ['epr', 'objepr']:
                print >>sys.stderr, "ERROR: mode must be either epr or objepr"
                sys.exit(1)


        # check max is int and between 1-1048576

        return legit

    def add_config(self, parser, config):
        config.wql = parser.options('wql')

    def adapt_args_to_config(self, args, config):
        config.wql = args.wql
        config.className = args.className
        config.namespace = args.namespace
        config.mode = args.mode
        config.ext = args.ext
        config.maxelements = args.max


if __name__ == '__main__':
    app.main(WsmanUtility(WsmanStrategy()))
