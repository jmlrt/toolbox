#!/usr/bin/env bash

# List all AMI from an AWS account with format: "<region> <ami_name> <ami_id>"

output_file=amis.txt

for region in $(aws ec2 describe-regions --query "Regions[].{Name:RegionName}" --output text --region us-east-1)
do
    aws ec2 describe-images --region us-east-1 --owners self --query 'Images[*].{Id:ImageId,Name:Name}' --output text --region "$region" | awk -v region="$region" '{print $2, $1, region}' | sort
done > "$output_file"
