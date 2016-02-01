#!/usr/bin/python
"""Writes and reads a lightweight custom metric.

This is an example of how to use the Google Cloud Monitoring API to write
and read a lightweight custom metric. Lightweight custom metrics have no
labels and you do not need to create a metric descriptor for them.

Prerequisites: Run this Python example on a Google Compute Engine virtual
machine instance that has been set up using these intructions:
https://cloud.google.com/monitoring/demos/setup_compute_instance.

Typical usage: Run the following shell commands on the instance:
    python write_lightweight_metric.py
    python write_lightweight_metric.py
    python write_lightweight_metric.py
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
	'B00N7N2CRQ', # The Practice of Cloud: Kindle
	'032194318X', # The Practice of Cloud: Paperback
	'B00AZRBLHO', # Phoenix Project: Kindle
	'0988262592', # Phoenix Project: Hardcover
	'0988262509', # Phoenix Project: Paperback
	'B00VATFAMI', # Phoenix Project: Audible
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
