#!/bin/bash

set -e

LAYER_DIR=".layers"
LAYER_FILES=(
    "pyrazine_layer_python3.6.zip"
    "pyrazine_layer_python3.7.zip"
    "pyrazine_layer_python3.8.zip"
)

AWS_PROFILE_NAME="$1"
[[ -z $AWS_PROFILE_NAME ]] && { echo "Must specify a profile name."; exit 1; }

SIGNING_PROFILE_NAME="pnpolcher_lambda_signer"
S3_BUCKET_NAME="pnpolcher-code-signing-bucket"
S3_BUCKET_REGION="eu-south-1"

for layer_file in "${LAYER_FILES[@]}"
do
    PATH_TO_LAYER="${LAYER_DIR}/${layer_file}"
    UUID=$(uuidgen)
    S3_UNSIGNED_ZIP_KEY="${UUID}.zip"
    S3_UNSIGNED_ZIP_URI="s3://${S3_BUCKET_NAME}/${S3_UNSIGNED_ZIP_KEY}"
    aws s3 cp "${PATH_TO_LAYER}" "${S3_UNSIGNED_ZIP_URI}" \
        --profile "${AWS_PROFILE_NAME}" \
        --region "${S3_BUCKET_REGION}"

    SIGNING_JOB_ID=$(aws signer start-signing-job \
        --source "s3={bucketName=${S3_BUCKET_NAME},key=${S3_UNSIGNED_ZIP_KEY},version=null"} \
        --destination "s3={bucketName=${S3_BUCKET_NAME}}" \
        --profile-name "${SIGNING_PROFILE_NAME}" \
        --profile "${AWS_PROFILE_NAME}" \
        --region "${S3_BUCKET_REGION}" \
        | jq -r '.jobId'\
    )

    echo "Waiting for signing job."
    SECONDS_WAITED=0
    while :
    do
        sleep 3
        SECONDS_WAITED=$((SECONDS_WAITED + 3))

        SIGNING_JOB_DESCRIPTION=$(aws signer describe-signing-job \
            --job-id "${SIGNING_JOB_ID}" \
            --profile "${AWS_PROFILE_NAME}" \
            --region "${S3_BUCKET_REGION}"\
        )

        SIGNING_JOB_STATUS=$(echo "${SIGNING_JOB_DESCRIPTION}" | jq -r '.status')
        SIGNING_JOB_STATUS_REASON=$(echo "${SIGNING_JOB_DESCRIPTION}" | jq -r '.statusReason')

        if [ "${SIGNING_JOB_STATUS}" = "Succeeded" ]; then
            echo "Signing complete."
            break
        fi

        if [ "${SIGNING_JOB_STATUS}" = "Failed" ]; then
          echo "Signing job failed. See reason below."
          echo "$SIGNING_JOB_STATUS_REASON"
          exit 1
        fi

        if [ $SECONDS_WAITED -ge 60 ]; then
          echo "Timed out waiting for signing job to complete."
          exit 1
        fi
    done

    S3_SIGNED_ZIP_KEY="${SIGNING_JOB_ID}.zip"
    S3_SIGNED_ZIP_URI="s3://${S3_BUCKET_NAME}/${S3_SIGNED_ZIP_KEY}"
    aws s3 cp "${S3_SIGNED_ZIP_URI}" "${PATH_TO_LAYER}" \
        --profile "${AWS_PROFILE_NAME}" \
        --region "${S3_BUCKET_REGION}"

    echo "Cleaning up S3 bucket."
    aws s3api delete-object --bucket "${S3_BUCKET_NAME}" \
        --key "${S3_UNSIGNED_ZIP_KEY}" \
        --profile "${AWS_PROFILE_NAME}" \
        --region "${S3_BUCKET_REGION}"

    aws s3api delete-object --bucket "${S3_BUCKET_NAME}" \
        --key "${S3_SIGNED_ZIP_KEY}" \
        --profile "${AWS_PROFILE_NAME}" \
        --region "${S3_BUCKET_REGION}"

done
