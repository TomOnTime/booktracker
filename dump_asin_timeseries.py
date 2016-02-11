#!/usr/bin/python
"""Dump the stored timeseries for a particular ASIN.
"""

import sys

import gmonitor
import awzconfig


def main():
  gm = gmonitor.GMonitor()

  # Process command line args.
  asins = sys.argv[1:]
  if len(asins) == 1 and asins[0] == 'all':
    asins = awzconfig.PRODUCTS
  if not asins:
    print "ERROR: Specify at least 1 asin on the command line or 'all' for all."
    sys.exit(1)

  for asin in asins:
    ranks = gm.ReadProductRank(asin)
    for d, rank in ranks:
      print asin, d, rank


if __name__ == "__main__":
  main()
