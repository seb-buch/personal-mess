#!/usr/bin/env python
# -*- coding: utf8 -*-
""" gsb: Will do something fancy"""
from __future__ import print_function, unicode_literals
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import pkgutil
import gsblib

__author__ = "Sébastien Buchoux"
__email__ = "sebastien.buchoux@gmail.com"
__copyright__ = "Copyright 2015, Sébastien Buchoux"
__license__ = "GPLv3"
__version__ = "1.0"

parser = ArgumentParser(description="List of useful stuff for MD simulations",
                        formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument('--version', action='version', version="%%(prog)s %s" % __version__)
subparsers = parser.add_subparsers(title="Commands")

prefix = gsblib.__name__ + "."
for importer, modname, ispkg in pkgutil.iter_modules(gsblib.__path__, prefix):
    try:
        module = __import__(modname, fromlist="dummy")
    except ImportError as e:
        print("WARNING: Could not import '%s' (Reason: %s)" % (modname, e.message))
        continue
    else:
        try:
            module.populate_parser(subparsers)
            assert hasattr(module, "run")
        except (AttributeError, AssertionError):
            print("WARNING: '%s' is not a proper gsb sub command and will be ignored." % modname)

if __name__ == "__main__":
    args = parser.parse_args()

    args.func(args)
