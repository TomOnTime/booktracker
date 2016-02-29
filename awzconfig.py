#!/usr/bin/python

import subprocess

PRODUCTS=[]

def get_asin_list(p):
  # gene: placeholder
  #out = subprocess.check_output(["bundle", "exec", "get_asin.rb"])
  out = subprocess.check_output(["cat", "sample.txt"])
  for line in out.splitlines():
    p.append(line)

get_asin_list(PRODUCTS)
