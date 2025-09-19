import json
import boto3
import os

ecs = boto3.client('ecs')

def lambda_handler(event, context):
    print("Lambda triggered. Event:", json.dumps(event, default=str))

    try:
        response = ecs.run_task(
            cluster=os.environ['ECS_CLUSTER'],
            launchType='FARGATE',
            taskDefinition=os.environ['TASK_DEFINITION'],
            count=1,
            platformVersion='LATEST',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': os.environ['SUBNETS'].split(','),
                    'securityGroups': os.environ['SECURITY_GROUPS'].split(','),
                    'assignPublicIp': 'ENABLED'
                }
            },
            overrides={
                'containerOverrides': [
                    {
                        'name': os.environ['CONTAINER_NAME'],
                        'environment': [
                            {
                                'name': 'MY_ENV_VAR',
                                'value': 'example_value'
                            }
                        ]
                    }
                ]
            }
        )

        print("ECS run_task response:", json.dumps(response, indent=2, default=str))

        failures = response.get("failures", [])
        if failures:
            print("ECS run_task FAILED:", json.dumps(failures, indent=2, default=str))
            return {
                'statusCode': 500,
                'body': json.dumps({"message": "ECS task failed to start", "failures": failures}, default=str)
            }

        return {
            'statusCode': 200,
            'body': json.dumps("ECS task started successfully"),
            'response': response
        }

    except Exception as e:
        print("Exception while running ECS task:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
