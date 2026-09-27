# AWS Skill — Agent Instructions & Guidelines

When architecting, developing, or configuring cloud solutions on **Amazon Web Services (AWS)**, strictly follow these engineering directives.

---

## 1. Security & Identity Directives (Non-Negotiable)

1. **Zero Hardcoded Credentials**:
   - Never write `aws_access_key_id` or `aws_secret_access_key` into code, configs, or `.env` files.
   - Rely solely on the AWS Default Credential Provider Chain:
     - IAM roles for Amazon EC2 / ECS tasks / Lambda execution roles.
     - AWS IAM Identity Center (SSO) or short-lived environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`).
2. **Principle of Least Privilege**:
   - Never write `"Action": "*"` or `"Resource": "*"`. Always specify explicit actions (e.g., `s3:GetObject`, `s3:PutObject`) and scope resources to specific ARNs with account and region variables.
   - Always require encryption at rest (KMS or AES256) and in transit (`aws:SecureTransport: true`).
3. **Secrets Management**:
   - Retrieve database credentials, API keys, and third-party tokens from **AWS Secrets Manager** or **SSM Parameter Store**.
   - Cache secrets outside the execution handler in Lambda to minimize API latency and billing costs.

---

## 2. Production `boto3` Coding Standards

1. **Client Reusability & Retries**:
   - Initialize boto3 clients outside functions or request handlers so connection pools and TLS handshakes persist across invocations.
   - Configure retries using adaptive or standard mode with backoff:
     ```python
     from botocore.config import Config
     import boto3

     boto_config = Config(
         region_name="us-east-1",
         retries={"max_attempts": 5, "mode": "adaptive"},
         connect_timeout=5,
         read_timeout=15,
     )
     s3_client = boto3.client("s3", config=boto_config)
     ```
2. **Defensive Error Handling**:
   - Catch `botocore.exceptions.ClientError` and examine `error["Error"]["Code"]`:
     ```python
     from botocore.exceptions import ClientError
     import logging

     logger = logging.getLogger(__name__)

     try:
         s3_client.head_object(Bucket=bucket_name, Key=object_key)
     except ClientError as exc:
         error_code = exc.response["Error"]["Code"]
         if error_code == "404":
             logger.warning("Object %s does not exist in %s", object_key, bucket_name)
         else:
             logger.error("S3 error [%s]: %s", error_code, exc)
             raise
     ```
3. **Paginators & Waiters**:
   - Never manually paginate using `NextContinuationToken` in a raw `while` loop when `client.get_paginator(...)` is available.
   - Use `client.get_waiter("...")` rather than home-grown polling loops with `time.sleep()`.

---

## 3. Serverless & AWS Lambda Best Practices

1. **Handler Design & Powertools**:
   - Use **AWS Lambda Powertools for Python** (`@logger.inject_lambda_context`, `@tracer.capture_lambda_handler`, `@metrics.log_metrics`).
   - Keep handlers lightweight: validate input -> invoke domain service -> return structured HTTP/Event response.
2. **Cold Start Mitigation**:
   - Initialize heavyweight clients, SDKs, and database pools in module scope (outside `lambda_handler`).
   - Import dependencies only where needed if they are massive and rarely used.
3. **Idempotency**:
   - In event-driven architectures (SQS, EventBridge), consumers may receive duplicate events. Implement idempotency checks using DynamoDB or unique transaction tokens.

---

## 4. DynamoDB Data Modeling Rules

1. **Query Over Scan**:
   - Always design schema around queries on Partition Key (`PK`) and optional Sort Key (`SK`). Avoid `Scan` operations in production paths.
2. **Conditional Writes**:
   - Guard against overwrites using condition expressions:
     ```python
     table.put_item(
         Item=item_payload,
         ConditionExpression="attribute_not_exists(PK)",
     )
     ```

---

## 5. Amazon Bedrock Guidelines

1. **Converse API Standard**:
   - Use `bedrock-runtime.converse()` or `bedrock-runtime.converse_stream()` instead of legacy `invoke_model()` with model-specific JSON bodies. The Converse API provides a unified, cross-model message schema for Claude, Llama, and Mistral.
2. **Tool Calling & Guardrails**:
   - Pass tool definitions using `toolConfig` and guardrails using `guardrailConfig` directly in the Converse API call.

---

## 6. Output Checklist for the Deep Agent

Before delivering AWS code or architecture to the user:
- [ ] Are credentials cleanly separated from code (no hardcoded keys)?
- [ ] Are IAM policies scoped to explicit actions and specific ARNs?
- [ ] Is `ClientError` caught and checked by specific error code?
- [ ] Are boto3 paginators used for scalable listing?
- [ ] Are clients initialized outside Lambda handler functions?
- [ ] Is data encryption (at rest and in transit) guaranteed?
