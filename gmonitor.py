#!/usr/bin/python

import time
import pprint

# Google Cloud:
from apiclient.discovery import build
import httplib2
from oauth2client.gce import AppAssertionCredentials
from oauth2client.client import GoogleCredentials

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


class GMonitor(object):

  def __init__(self):
    # Find out Google Cloud Customer ID.
    project_id = GetProjectId()

    # OLD VERISON:
    # Create a cloudmonitoring service to call. Use OAuth2 credentials.
    #credentials = AppAssertionCredentials(
    #    scope="https://www.googleapis.com/auth/monitoring")

    # NEW VERSION: https://cloud.google.com/storage/docs/json_api/v1/json-api-python-samples
    # Get the application default credentials. When running locally, these are
    # available after running `gcloud init`. When running on compute
    # engine, these are available from the environment.
    credentials = GoogleCredentials.get_application_default()

    http = credentials.authorize(httplib2.Http())
    service = build(serviceName="cloudmonitoring", version="v2beta2", http=http)

    self._project_id = project_id
    self._service = service


  def StoreProductRank(self, asin, sales_rank):
    """
    Stores the product rank to the monitoring system.
    """
    service = self._service
    project_id = self._project_id

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


  def ReadProductRank(self, asin):

    # Read all data points from the time series.
    # When a custom metric is created, it may take a few seconds
    # to propagate throughout the system. Retry a few times.

    # TODO(tlim): Use the pageToken stuff to get all the data
    # https://cloud.google.com/monitoring/v2beta2/timeseries/list

    service = self._service
    project_id = self._project_id

    #now = '2005-01-01T00:00:00Z'
    now = GetNowRfc3339()

    print "Reading data from custom metric timeseries..."
    read_request = service.timeseries().list(
        project=project_id,
        metric=CUSTOM_METRIC_NAME_BASE % (asin,),
        youngest=now)
    #start = time.time()
    start = 0
    while True:
      try:
        read_response = read_request.execute()
        #pprint.pprint(read_response)
        for point in read_response["timeseries"][0]["points"]:
          yield point["end"], point["doubleValue"]
        if 'nextPageToken' in read_response:
          print "WARNING: There is more data. We need to read other pages."
        break
      except Exception as e:
        if time.time() < start + 20:
          print "Failed to read custom metric data, retrying..."
          time.sleep(3)
        else:
          print "Failed to read custom metric data, aborting: exception=%s" % e
          raise  # propagate exception
