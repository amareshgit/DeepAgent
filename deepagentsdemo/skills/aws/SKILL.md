---
name: aws
description: AWS cloud architecture and implementation skill for designing, deploying, and managing secure, scalable cloud infrastructure using boto3, CDK, Terraform, Serverless, IAM, S3, DynamoDB, Lambda, ECS, and Bedrock.
version: 1.0.0
tags:
  - aws
  - cloud
  - boto3
  - lambda
  - s3
  - dynamodb
  - iam
  - bedrock
  - cdk
  - serverless
---

# AWS Skill

## Purpose & Scope
This skill equips the **Deep Agent** with production cloud engineering expertise across the **Amazon Web Services (AWS)** ecosystem.

It governs how the agent architects cloud solutions, writes SDK code with `boto3`, structures serverless microservices with AWS Lambda and API Gateway, models NoSQL data in DynamoDB, secures resources with least-privilege IAM policies, leverages Generative AI via Amazon Bedrock, and provisions infrastructure cleanly via AWS CDK (Python/TypeScript) or Terraform.

---

## Core Capabilities

1. **Production Python SDK (`boto3`) Engineering**:
   - Explicit client and session initialization using default credential chains (environment, instance profiles, SSO).
   - Defensive error handling catching `botocore.exceptions.ClientError` and inspecting specific error codes (`EntityAlreadyExists`, `NoSuchKey`, etc.).
   - Efficient pagination using `get_paginator()` for large result sets.
   - Resource state verification using `waiter` abstractions (`get_waiter("bucket_exists")`, etc.).
   - Exponential backoff and jitter configurations with `botocore.config.Config`.

2. **Serverless Architecture (Lambda & API Gateway)**:
   - Writing resilient, low-latency AWS Lambda handlers with **AWS Lambda Powertools** (structured logging, tracing, metrics, validation).
   - Cold-start optimization (lazy imports, connection reuse outside the handler, memory sizing).
   - Event-driven patterns using Amazon EventBridge, SQS FIFO/Standard queues, and SNS topics.

3. **Storage & Databases (S3 & DynamoDB)**:
   - **Amazon S3**: Presigned URLs (upload/download), server-side encryption (SSE-KMS/SSE-S3), bucket policies, lifecycle transitions, multipart uploads for large binaries.
   - **Amazon DynamoDB**: Single-table design principles, partition (`PK`) and sort key (`SK`) modeling, Global Secondary Indexes (GSIs), Query vs. Scan discipline, optimistic concurrency with `attribute_exists` / `attribute_not_exists` condition expressions.

4. **Amazon Bedrock & Cloud AI**:
   - Invoking Foundation Models (Claude 3.5/3.7, Titan, Llama 3) via the **Bedrock Converse API** (`converse`, `converse_stream`).
   - Structured output, system prompts, tool calling, and guardrails with Bedrock.
   - RAG integration with Amazon Bedrock Knowledge Bases and OpenSearch Serverless.

5. **Cloud Security & Identity (IAM)**:
   - Principle of Least Privilege: narrowly scoped IAM role policies (never using `*` actions or resources unless strictly required by AWS documentation).
   - Cross-account and temporary role assumption via `sts:AssumeRole`.
   - Secret management using AWS Secrets Manager and Parameter Store with client-side caching.

6. **Infrastructure as Code (AWS CDK & Terraform)**:
   - Writing declarative, modular CDK stacks in Python (`aws_cdk`).
   - Applying security constructs (encrypted buckets, removal policies, VPC subnets).

---

## When to Use This Skill (Triggers)

Activate this skill when the user query involves:
- Writing or refactoring Python scripts using `boto3` or `botocore`.
- Implementing AWS Lambda functions, Step Functions, or EventBridge workflows.
- Designing or querying DynamoDB tables, S3 bucket configurations, or SQS queues.
- Integrating LLMs or generative AI applications using Amazon Bedrock.
- Authoring IAM roles, policies, security groups, or credential setup.
- Writing AWS CDK stacks, Terraform configs, or CloudFormation templates.

---

## Associated References
- Detailed directives: [`instructions.md`](./instructions.md)
- Production cloud patterns: [`examples.md`](./examples.md)
