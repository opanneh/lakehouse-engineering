
import io
import os
import tempfile

import pyarrow.parquet as pq
from minio import Minio
from dotenv import load_dotenv


def main():
    load_dotenv()

    # MinIO configuration
    client = Minio(
        "localhost:9000",
        access_key=os.getenv("MINIO_ROOT_USER"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
        secure=False
    )

    # Source and destination buckets
    source_bucket = "bronze"
    destination_bucket = "nyc-taxis-records"
    prefix = "nyc_taxis_files/"

    # Create destination bucket if it doesn't exist
    if not client.bucket_exists(destination_bucket):
        client.make_bucket(destination_bucket)
        print(f"Created bucket: {destination_bucket}")

    # List objects in Bronze
    objects = client.list_objects(
        source_bucket,
        prefix=prefix,
        recursive=True
    )

    # Read the first matching Parquet file
    for obj in objects:
        if not obj.object_name.endswith(".parquet"):
            continue

        print(f"Reading: {obj.object_name}", flush=True)

        # Download Parquet file to temporary disk storage
        with tempfile.NamedTemporaryFile(suffix=".parquet") as temp_file:

            client.fget_object(
                source_bucket,
                obj.object_name,
                temp_file.name
            )

            # Read only the first row using PyArrow
            parquet_file = pq.ParquetFile(temp_file.name)

            first_batch = next(
                parquet_file.iter_batches(batch_size=1)
            )

            data = first_batch.to_pandas()
            row = data.iloc[0]

            print("\nFirst row:")
            print(data)

            # Generate JSON filename
            vendor_id = str(row["VendorID"])
            pickup_datetime = str(row["tpep_pickup_datetime"])

            pickup_datetime_formatted = (
                pickup_datetime
                .replace(":", "-")
                .replace(" ", "_")
            )

            file_name = (
                f"trip_{vendor_id}_"
                f"{pickup_datetime_formatted}.json"
            )

            # Convert row to JSON bytes
            record = row.to_json()
            record_bytes = record.encode("utf-8")
            record_stream = io.BytesIO(record_bytes)
            record_stream_len = len(record_bytes)

            # Upload JSON record to MinIO
            print("\nUploading JSON record...", flush=True)

            client.put_object(
                bucket_name=destination_bucket,
                object_name=f"nyc_taxi_record/{file_name}",
                data=record_stream,
                length=record_stream_len,
                content_type="application/json"
            )

            print(f"Successfully uploaded: {file_name}", flush=True)

        break  # Process only the first Parquet file


if __name__ == "__main__":
    main()
