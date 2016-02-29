#!/usr/bin/python
"""Records ASIN SalesRank and uploads to Google Monitoring

TODO(tlim): Make a Monitor object that carries service,product_id.
TODO(tlim): Currently the data is stored at a timestamp generated
  when the data is being stored. Instead, record the time that
  the data is gathered and use that to timestamp the data.
"""

import gmonitor
import awzconfig


# AWZ:
from amazon.api import AmazonAPI
import creds


def GetProductRanks(product_codes):
  """
  product_codes: A list of asin codes.
  Returns a dict of asin: sales_rank.
  """
  result = {}
  for x in range(0, len(product_codes), 10):
    result.update(Get10ProductRanks(product_codes[x:x+10]))
  return result


def Get10ProductRanks(product_codes):
  """Amazon only permits 10 codes at a time."""
  amazon = AmazonAPI(creds.AMAZON_ACCESS_KEY, creds.AMAZON_SECRET_KEY, creds.AMAZON_ASSOC_TAG)
  products = amazon.lookup(ItemId=','.join(product_codes))
  return dict((x.asin, int(x.sales_rank)) for x in products)


def main():
  gm = gmonitor.GMonitor()

  rankings = GetProductRanks(awzconfig.PRODUCTS)
  for asin, rank in rankings.iteritems():
    print "WRITING", asin, rank
    gm.StoreProductRank(asin, rank)
    # Gene: placeholder
    # run salesrank_add.rb ASIN rank
    subprocess.check_call(['bundle', 'exec', 'ruby', 'salesrank_add.rb', asin, rank])


if __name__ == "__main__":
  main()
