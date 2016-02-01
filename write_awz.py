#!/usr/bin/python
"""Records ASIN SalesRank and uploads to Google Monitoring

TODO(tlim): Make a Monitor object that carries service,product_id.
TODO(tlim): Currently the data is stored at a timestamp generated
  when the data is being stored. Instead, record the time that
  the data is gathered and use that to timestamp the data.
"""

import os
import time

# Google Cloud:
from apiclient.discovery import build
import httplib2
from oauth2client.gce import AppAssertionCredentials

# AWZ:
from amazon.api import AmazonAPI
import creds


PRODUCTS = [
	'B0199EW96U', # Year In White: Kindle
	'0813571197', # Year In White: Paperback
	'0813571200', # Year In White: Hardcover
	'032194318X', # The Practice of Cloud: Paperback
	'B00N7N2CRQ', # The Practice of Cloud: Kindle
	'0321492668', # The Practice of Sysadmin: Paperback
	'B004JLMUJ0', # The Practice of Sysadmin: Kindle
	'0596007833', # Time Mgmt for Sysadmins: Paperback
	'B0026OR2WM', # Time Mgmt for Sysadmins: Kindle
	'1573980420', # April Fools RFCs: Paperback
	'B00AZRBLHO', # Phoenix Project: Kindle
	'0988262509', # Phoenix Project: Paperback
	'0988262592', # Phoenix Project: Hardcover
	'B00VATFAMI', # Phoenix Project: Audible
	'B016CJ5HUA', # Beyond Blame: Kindle
	'1491906413', # Beyond Blame: Paperback
]


CUSTOM_METRIC_NAME_BASE = "custom.cloudmonitoring.googleapis.com/amz_%s"


def GetProjectId():
  """Read the numeric project ID from metadata service."""
  http = httplib2.Http()
  resp, content = http.request(
      ("http://metadata.google.internal/"
       "computeMetadata/v1/project/numeric-project-id"),
      "GET", headers={"Metadata-Flavor": "Google"})
  if resp["status"] != "200":
    raise Exception("Unable to get project ID from metadata service")
  return content


def GetNowRfc3339():
  """Give the current time formatted per RFC 3339."""
  return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


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


def StoreProductRank(service, project_id, asin, sales_rank):
  """
  Stores the product rank to the monitoring system.
  """

  # Set up the write request.
  now = GetNowRfc3339()
  desc = {"project": project_id,
          "metric": CUSTOM_METRIC_NAME_BASE % (asin,)}
  point = {"start": now,
           "end": now,
           "doubleValue": sales_rank}
  print "Writing %d at %s" % (point["doubleValue"], now)

  # Write a new data point.
  try:
    write_request = service.timeseries().write(
        project=project_id,
        body={"timeseries": [{"timeseriesDesc": desc, "point": point}]})
    _ = write_request.execute()  # Ignore the response.
  except Exception as e:
    print "Failed to write custom metric data: exception=%s" % e
    raise  # propagate exception


def main():
  project_id = GetProjectId()

  # Create a cloudmonitoring service to call. Use OAuth2 credentials.
  credentials = AppAssertionCredentials(
      scope="https://www.googleapis.com/auth/monitoring")
  http = credentials.authorize(httplib2.Http())
  service = build(serviceName="cloudmonitoring", version="v2beta2", http=http)

  rankings = GetProductRanks(PRODUCTS)
  for asin, rank in rankings.iteritems():
    print "WRITING", asin, rank
    StoreProductRank(service, project_id, asin, rank)


if __name__ == "__main__":
  main()
