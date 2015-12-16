#!/usr/bin/env python
# -*- coding: utf8 -*-
""" get_topology: Will do something fancy"""
from __future__ import print_function
from argparse import ArgumentDefaultsHelpFormatter

__author__ = "Sébastien Buchoux"
__email__ = "sebastien.buchoux@gmail.com"
__copyright__ = "Copyright 2015, Sébastien Buchoux"
__license__ = "GPLv3"
__version__ = "1.0"


def populate_parser(parent_parser):
    parser = parent_parser.add_parser("get_topology",
                                      description="Read a .gro and retrieve the number residues",
                                      formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("grofile", help="A .gro file")

    parser.set_defaults(func=run)


def run(args):
    fpath = args.grofile
    last_resid = -1
    last_resname = None

    topo = {}
    res_size = {}
    res_start = -1
    with open(fpath) as fp:
        for lino, line in enumerate(fp):
            if lino == 0:
                continue
            if lino == 1:
                natoms = int(line)
                #print("%i atoms in '%s'" % (natoms, fpath))
                continue
            if lino - 1 > natoms:
                break

            resid = int(line[:5])
            resname = line[5:10].strip()
            if resid != last_resid:
                last_resid = resid
                if last_resname:
                    if res_size[last_resname] == -1:
                        res_size[last_resname] = lino - res_start
                try:
                    topo[resname] += 1
                except KeyError:
                    #print("New resname '%s' found @ resid %i!" % (resname, resid))
                    topo[resname] = 1
                    res_size[resname] = -1
                    res_start = lino
                    last_resname = resname

    print("Topology for '%s' (%i atoms):" % (fpath, natoms))
    counted_atoms = 0
    for key, val in topo.items():
        n = val * res_size[key]
        print("  -> %s (%i atoms): %i (total: %i atoms)" % (key, res_size[key],
                                                       val, n))
        counted_atoms += n

    if counted_atoms != natoms:
        print("ERROR: %i atoms listed in '%s' but %i atoms counted... That is weird!" %(
            natoms, fpath, counted_atoms
        ))
