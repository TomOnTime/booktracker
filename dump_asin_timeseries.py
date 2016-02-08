#!/usr/bin/python
"""Dump the stored timeseries for a particular ASIN.

"""

import os
import time

# Google Cloud:
from apiclient.discovery import build
import httplib2
from oauth2client.gce import AppAssertionCredentials


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


def ReadProductRank(service, project_id, asin):

  # Read all data points from the time series.
  # When a custom metric is created, it may take a few seconds
  # to propagate throughout the system. Retry a few times.

  # TODO(tlim): Use the pageToken stuff to get all the data
  # https://cloud.google.com/monitoring/v2beta2/timeseries/list

  print "Reading data from custom metric timeseries..."
  read_request = service.timeseries().list(
      project=project_id,
      metric=CUSTOM_METRIC_NAME_BASE % (asin,),
      youngest=now)
  start = time.time()
  while True:
    try:
      read_response = read_request.execute()
      for point in read_response["timeseries"][0]["points"]:
        print "  %s: %s" % (point["end"], point["doubleValue"])
      break
    except Exception as e:
      if time.time() < start + 20:
        print "Failed to read custom metric data, retrying..."
        time.sleep(3)
      else:
        print "Failed to read custom metric data, aborting: exception=%s" % e
        raise  # propagate exception


def main():
  project_id = GetProjectId()

  # Create a cloudmonitoring service to call. Use OAuth2 credentials.
  credentials = AppAssertionCredentials(
      scope="https://www.googleapis.com/auth/monitoring")
  http = credentials.authorize(httplib2.Http())
  service = build(serviceName="cloudmonitoring", version="v2beta2", http=http)

  ReadProductRank(service, project_id, asin):


if __name__ == "__main__":
  main()
