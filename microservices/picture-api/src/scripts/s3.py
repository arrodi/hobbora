import boto3

class S3:
    def __init__(self, access_key, secret_key, endpoint):
        self.client = boto3.client( 's3',
                                    aws_access_key_id=access_key,
                                    aws_secret_access_key=secret_key,
                                    endpoint_url=endpoint,
                                    verify=False)
        
    def get_objects(self, bucket_nm, prefix=""):
        object_lst = [object for object in self.client.get_paginator('list_objects_v2').paginate(Bucket=bucket_nm, Prefix=prefix)]
        print(object_lst)
        return object_lst