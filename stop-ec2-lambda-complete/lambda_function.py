import boto3
import logging

logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    stopped_instances = {}

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        running_instances = ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        
        instance_ids = []
        for reservation in running_instances['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])

        if instance_ids:
            try:
                ec2.stop_instances(InstanceIds=instance_ids)
                stopped_instances[region] = instance_ids
                logging.info(f"Stopped instances in {region}: {instance_ids}")
            except Exception as e:
                logging.error(f"Error stopping instances in {region}: {e}")

    return {
        'statusCode': 200,
        'body': f'Stopped instances: {stopped_instances}'
    }
