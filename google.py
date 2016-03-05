import argparse
# [START detect_text]
import base64
import os
import re
import sys

from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.client import GoogleCredentials

DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'

class VisionApi:
  """Construct and use the Google Vision API service."""

  def __init__(self, api_discovery_file='vision_api.json'):
    self.credentials = GoogleCredentials.get_application_default()
    self.service = discovery.build(
      'vision', 'v1', credentials=self.credentials,
      discoveryServiceUrl=DISCOVERY_URL)

  def detect_text(self, image_file, num_retries=3, max_results=6):
    """Uses the Vision API to detect text in the given file.
    """
    image_content = image_file.read()

    batch_request = [{
      'image': {
        'content': base64.b64encode(image_content)
      },
      'features': [{
        'type': 'TEXT_DETECTION',
        'maxResults': max_results
      }],
      'imageContext': {
        'languageHints': ['en']
      }
    }]
    request = self.service.images().annotate(
      body={'requests': batch_request})

    try:
      response = request.execute(num_retries=num_retries)
      if ('responses' in response
         and 'textAnnotations' in response['responses'][0]):
        text_response = response['responses'][0]['textAnnotations']
        return text_response
      else:
        return []
    except errors.HttpError, e:
      print("Http Error for %s: %s" % (image_file, e))
    except KeyError, e2:
      print("Key error: %s" % e2)
# [END detect_text]

def get_words(text):
  return re.compile('\w+').findall(text)

# [START extract_descrs]
def extract_descriptions(input_filename, index, texts):
  """Gets and indexes the text that was detected in the image."""
  if texts:
    document = ''
    for text in texts:
      try:
        document += text['description']
      except KeyError, e:
        print('KeyError: %s' % text)
    index.add(input_filename, document)
    sys.stdout.write('.')  # Output a progress indicator.
    sys.stdout.flush()
  else:
    if texts == []:
      print('%s had no discernible text.' % input_filename)
      index.set_contains_no_text(input_filename)
# [END extract_descrs]


# [START get_text]
def get_text_from_file(vision, index, input_filename):
  """Call the Vision API on a file and index the results."""
  with open(input_filename, 'rb') as image:
    texts = vision.detect_text(image)
    extract_descriptions(input_filename, index, texts)


def main(filename):
  # Create a client object for the Vision API
  vision = VisionApi()
  with open(filename, 'rb') as image:
    texts = vision.detect_text(image)
    print texts
  # get_text_from_file(vision, index, filename)
# [END get_text]

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Detects text in the images in the given directory.')
  parser.add_argument(
    'filename',
    help='the image directory you\'d like to detect text in.')
  args = parser.parse_args()
  main(args.filename)