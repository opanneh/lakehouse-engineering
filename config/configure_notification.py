
import boto3
from botocore.config import Config

client = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
    region_name="us-east-1",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"}
    )
)

client.put_bucket_notification_configuration(
    Bucket="nyc-taxis-records",
    NotificationConfiguration={
        "QueueConfigurations": [
            {
                "Id": "taxi_trip_sink",
                "QueueArn": "arn:minio:sqs::TAXI_TRIP_SINK:kafka",
                "Events": ["s3:ObjectCreated:*"]
            }
        ]
    }
)

print("Bucket notification configured successfully.")

print(
    client.get_bucket_notification_configuration(
        Bucket="nyc-taxis-records"
    )
)
