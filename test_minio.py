
from minio import Minio
from config.minio_config import config, BUCKETS

client = Minio(
    config["endpoint"].replace("http://", "").replace("https://", ""),
    access_key=config["access_key"],
    secret_key=config["secret_key"],
    secure=config["secure"]
)

for name, bucket in BUCKETS.items():
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
    print(f"{name}: {bucket} - ready")

print("MinIO connection successful!")
