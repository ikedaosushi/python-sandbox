#!/bin/bash
STACK_NAME=amazon-personalize-example-stack
REGION=ap-northeast-1
TEMPLATE_FILE=file://cloudformation.yml

# aws cloudformation create-stack \
#   --stack-name $STACK_NAME \
#   --region $REGION \
#   --template-body $TEMPLATE_FILE

aws cloudformation update-stack \
  --stack-name $STACK_NAME \
  --region $REGION \
  --template-body $TEMPLATE_FILE \
  --capabilities CAPABILITY_IAM