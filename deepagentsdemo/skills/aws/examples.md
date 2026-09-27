# AWS Skill — Production Examples

This document provides production-ready, security-hardened patterns across core AWS services.

---

## Example 1: Resilient Boto3 S3 Client with Paginator and Backoff

Demonstrates configuration with adaptive retries, pagination, typed `ClientError` checking, and presigned URL generation.

```python
"""Production S3 operations client using boto3."""

import logging
from botocore.config import Config
from botocore.exceptions import ClientError
import boto3

logger = logging.getLogger(__name__)


class S3StorageService:
    def __init__(self, region: str = "us-east-1") -> None:
        self.config = Config(
            region_name=region,
            retries={"max_attempts": 5, "mode": "adaptive"},
            connect_timeout=5,
            read_timeout=15,
        )
        self.client = boto3.client("s3", config=self.config)

    def list_all_files(self, bucket: str, prefix: str = "") -> list[str]:
        """Safely list all object keys in a bucket prefix using boto3 paginator."""
        paginator = self.client.get_paginator("list_objects_v2")
        keys: list[str] = []
        try:
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                if "Contents" in page:
                    for obj in page["Contents"]:
                        keys.append(obj["Key"])
            return keys
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("Failed to list objects in %s [%s]: %s", bucket, code, exc)
            raise

    def generate_secure_upload_url(
        self, bucket: str, key: str, expires_in_seconds: int = 900
    ) -> str:
        """Generate a time-limited presigned PUT URL for client-side uploads."""
        try:
            url = self.client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": bucket,
                    "Key": key,
                    "ServerSideEncryption": "AES256",
                },
                ExpiresIn=expires_in_seconds,
            )
            return url
        except ClientError as exc:
            logger.error("Failed to generate presigned upload URL: %s", exc)
            raise
```

---

## Example 2: Production Serverless Lambda Handler with AWS Lambda Powertools

Demonstrates structured logging, tracing, validation, and standardized error response contracts.

```python
"""Enterprise AWS Lambda Handler for event ingestion."""

import json
from typing import Any
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from pydantic import BaseModel, Field, ValidationError

logger = Logger(service="order-service")
tracer = Tracer(service="order-service")
metrics = Metrics(namespace="Ecommerce", service="order-service")
app = APIGatewayRestResolver()


class CreateOrderRequest(BaseModel):
    customer_id: str = Field(..., min_length=5)
    amount: float = Field(..., gt=0.0)
    items: list[str] = Field(..., min_items=1)


@app.post("/orders")
@tracer.capture_method
def create_order():
    payload = app.current_event.json_body
    try:
        order = CreateOrderRequest.model_validate(payload)
    except ValidationError as err:
        logger.warning("Invalid order payload", extra={"errors": err.errors()})
        return {"statusCode": 400, "body": json.dumps({"error": err.errors()})}

    logger.info("Processing order for customer", extra={"customer_id": order.customer_id})
    metrics.add_metric(name="OrdersCreated", unit=MetricUnit.Count, value=1)
    metrics.add_metric(name="OrderValue", unit=MetricUnit.None_, value=order.amount)

    # Business logic execution
    order_id = f"ord-{order.customer_id[-4:]}-101"
    return {
        "order_id": order_id,
        "status": "ACCEPTED",
        "total": order.amount,
    }


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    return app.resolve(event, context)
```

---

## Example 3: Amazon Bedrock Converse API with Streaming & System Prompts

Demonstrates invoking foundation models (Claude 3.5 Sonnet) using the modern Bedrock Converse stream API.

```python
"""Amazon Bedrock integration using the modern Converse API."""

import logging
from botocore.config import Config
from botocore.exceptions import ClientError
import boto3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def stream_bedrock_completion(
    prompt_text: str,
    system_prompt: str = "You are a cloud architecture expert.",
    model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
    region: str = "us-east-1",
) -> str:
    """Stream text response from Amazon Bedrock using ConverseStream."""
    config = Config(region_name=region, retries={"max_attempts": 3, "mode": "standard"})
    client = boto3.client("bedrock-runtime", config=config)

    messages = [
        {
            "role": "user",
            "content": [{"text": prompt_text}],
        }
    ]
    system = [{"text": system_prompt}]
    inference_config = {
        "maxTokens": 2048,
        "temperature": 0.2,
        "topP": 0.9,
    }

    try:
        response = client.converse_stream(
            modelId=model_id,
            messages=messages,
            system=system,
            inferenceConfig=inference_config,
        )

        accumulated_text: list[str] = []
        for event in response["stream"]:
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"]["delta"]["text"]
                accumulated_text.append(delta)
                print(delta, end="", flush=True)

        print()  # Newline after streaming finishes
        return "".join(accumulated_text)

    except ClientError as exc:
        logger.error("Bedrock invocation failed [%s]: %s", exc.response["Error"]["Code"], exc)
        raise


if __name__ == "__main__":
    stream_bedrock_completion("Explain the benefits of S3 Intelligent-Tiering in 2 sentences.")
```

---

## Example 4: AWS CDK (Python) Least-Privilege Architecture Stack

Demonstrates provisioning an EventBridge rule, SQS queue with dead-letter queue (DLQ), and a Lambda consumer with least-privilege IAM permissions.

```python
"""AWS CDK Stack: Event-driven Lambda pipeline with dead-letter queue."""

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_lambda_event_sources as event_sources,
    aws_sqs as sqs,
)
from constructs import Construct


class EventProcessingPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Dead Letter Queue for failed messages
        dlq = sqs.Queue(
            self,
            "EventProcessingDLQ",
            retention_period=Duration.days(14),
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # 2. Main SQS processing queue
        main_queue = sqs.Queue(
            self,
            "EventProcessingQueue",
            visibility_timeout=Duration.seconds(60),
            enforce_ssl=True,
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=dlq,
            ),
        )

        # 3. Worker Lambda function
        worker_lambda = _lambda.Function(
            self,
            "WorkerFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "QUEUE_URL": main_queue.queue_url,
                "POWERTOOLS_SERVICE_NAME": "event-worker",
            },
        )

        # 4. Attach SQS event source to Lambda
        worker_lambda.add_event_source(
            event_sources.SqsEventSource(main_queue, batch_size=10)
        )

        # 5. Route incoming EventBridge events to SQS
        order_rule = events.Rule(
            self,
            "OrderCreatedRule",
            event_pattern=events.EventPattern(
                source=["ecommerce.orders"],
                detail_type=["OrderCreated"],
            ),
        )
        order_rule.add_target(targets.SqsQueue(main_queue))
```
