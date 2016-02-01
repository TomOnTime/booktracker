#!/usr/bin/env python

from amazon.api import AmazonAPI

import creds

amazon = AmazonAPI(creds.AMAZON_ACCESS_KEY, creds.AMAZON_SECRET_KEY, creds.AMAZON_ASSOC_TAG)
product = amazon.lookup(ItemId='032194318X')
print "TITLE =", product.title
print "SALES RANK =", product.sales_rank
import pdb; pdb.set_trace()
