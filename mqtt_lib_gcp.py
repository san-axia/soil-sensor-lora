from datetime import datetime
import warnings
from google.cloud import pubsub_v1
import json
from google.auth import jwt

warnings.filterwarnings("ignore", category=DeprecationWarning)

# GCP Pub/Sub setting
project_id = 'goldfarm-88888888'
topic = 'soildata'
publisher_file = "../soil-sensor-test/publisher.json"
topic_name = ''

def send_data(publisher,topic,data):
    data_byte = json.dumps(data).encode('utf-8')
    future = publisher.publish(topic, data_byte)
    print(future.result())
    return future.result()

def init_gcp(publisher_file=publisher_file,project_id=project_id,topic=topic):
    try:
        global topic_name
        service_account_info = json.load(open(publisher_file))
        publisher_audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"

        credentials = jwt.Credentials.from_service_account_info(
            service_account_info, audience=publisher_audience
        )
        credentials_pub = credentials.with_claims(audience=publisher_audience)
        publisher = pubsub_v1.PublisherClient(credentials=credentials_pub)
        # projects/goldfarm-88888888/topics/soildata
        topic_name = 'projects/{project_id}/topics/{topic}'.format(
            project_id=project_id,
            topic=topic,  # Set this to something appropriate.
        )
        return publisher
        
    except Exception as e:
        print('Error in GCP Pub/Sub initialization')
        print(e)
        return None
