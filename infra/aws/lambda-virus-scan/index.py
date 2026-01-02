"""
Lambda function for virus scanning uploaded files using ClamAV.

This function is triggered by S3 object creation events, scans the file
for viruses, and either tags it as clean or moves it to quarantine.
"""

import json
import os
import subprocess
import urllib.parse
from typing import Any, Dict

import boto3

s3_client = boto3.client("s3")

QUARANTINE_BUCKET = os.environ["QUARANTINE_BUCKET"]
SOURCE_BUCKET = os.environ["SOURCE_BUCKET"]


def update_virus_definitions() -> None:
    """Update ClamAV virus definitions."""
    print("Updating ClamAV virus definitions...")
    try:
        subprocess.run(
            ["/opt/bin/freshclam", "--config-file=/opt/etc/freshclam.conf"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Virus definitions updated successfully")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to update virus definitions: {e.stderr}")
        # Continue anyway - we may have cached definitions


def scan_file(file_path: str) -> tuple[bool, str]:
    """
    Scan a file for viruses using ClamAV.

    Args:
        file_path: Path to the file to scan

    Returns:
        Tuple of (is_clean, scan_result)
    """
    print(f"Scanning file: {file_path}")
    try:
        result = subprocess.run(
            ["/opt/bin/clamscan", "--no-summary", file_path],
            capture_output=True,
            text=True,
        )

        # ClamAV exit codes:
        # 0 = No virus found
        # 1 = Virus found
        # 2+ = Error
        if result.returncode == 0:
            print("File is clean")
            return True, "clean"
        elif result.returncode == 1:
            virus_name = result.stdout.strip()
            print(f"Virus detected: {virus_name}")
            return False, virus_name
        else:
            print(f"Scan error: {result.stderr}")
            return False, f"scan_error: {result.stderr}"

    except Exception as e:
        print(f"Exception during scan: {str(e)}")
        return False, f"exception: {str(e)}"


def quarantine_file(bucket: str, key: str, version_id: str | None = None) -> None:
    """
    Move infected file to quarantine bucket.

    Args:
        bucket: Source bucket name
        key: Object key
        version_id: Optional version ID
    """
    print(f"Moving file to quarantine: {bucket}/{key}")

    # Copy to quarantine bucket
    copy_source = {"Bucket": bucket, "Key": key}
    if version_id:
        copy_source["VersionId"] = version_id

    s3_client.copy_object(
        CopySource=copy_source,
        Bucket=QUARANTINE_BUCKET,
        Key=key,
        TaggingDirective="COPY",
        ServerSideEncryption="AES256",
    )

    # Tag in quarantine bucket
    s3_client.put_object_tagging(
        Bucket=QUARANTINE_BUCKET,
        Key=key,
        Tagging={
            "TagSet": [
                {"Key": "scan-status", "Value": "infected"},
                {"Key": "quarantined", "Value": "true"},
            ]
        },
    )

    # Delete from source bucket
    if version_id:
        s3_client.delete_object(Bucket=bucket, Key=key, VersionId=version_id)
    else:
        s3_client.delete_object(Bucket=bucket, Key=key)

    print(f"File quarantined successfully")


def tag_clean_file(bucket: str, key: str, version_id: str | None = None) -> None:
    """
    Tag a clean file in S3.

    Args:
        bucket: Bucket name
        key: Object key
        version_id: Optional version ID
    """
    print(f"Tagging clean file: {bucket}/{key}")

    tagging_args: Dict[str, Any] = {
        "Bucket": bucket,
        "Key": key,
        "Tagging": {"TagSet": [{"Key": "scan-status", "Value": "clean"}]},
    }

    if version_id:
        tagging_args["VersionId"] = version_id

    s3_client.put_object_tagging(**tagging_args)
    print("File tagged as clean")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for S3 virus scanning.

    Args:
        event: S3 event notification
        context: Lambda context

    Returns:
        Response dictionary
    """
    print(f"Received event: {json.dumps(event)}")

    # Update virus definitions (may use cached if update fails)
    update_virus_definitions()

    # Process each S3 record
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        version_id = record["s3"]["object"].get("versionId")

        print(f"Processing: s3://{bucket}/{key}")

        # Download file to /tmp
        local_path = f"/tmp/{os.path.basename(key)}"
        try:
            download_args: Dict[str, Any] = {"Bucket": bucket, "Key": key}
            if version_id:
                download_args["VersionId"] = version_id

            s3_client.download_file(
                Bucket=bucket,
                Key=key,
                Filename=local_path,
                ExtraArgs=download_args.get("ExtraArgs"),
            )

            # Scan the file
            is_clean, scan_result = scan_file(local_path)

            if is_clean:
                tag_clean_file(bucket, key, version_id)
            else:
                quarantine_file(bucket, key, version_id)

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            # Tag as scan-error
            try:
                tag_args: Dict[str, Any] = {
                    "Bucket": bucket,
                    "Key": key,
                    "Tagging": {
                        "TagSet": [
                            {"Key": "scan-status", "Value": "error"},
                            {"Key": "scan-error", "Value": str(e)[:256]},
                        ]
                    },
                }
                if version_id:
                    tag_args["VersionId"] = version_id

                s3_client.put_object_tagging(**tag_args)
            except Exception as tag_error:
                print(f"Failed to tag error: {str(tag_error)}")

        finally:
            # Clean up temp file
            if os.path.exists(local_path):
                os.remove(local_path)

    return {"statusCode": 200, "body": json.dumps("Scan complete")}
