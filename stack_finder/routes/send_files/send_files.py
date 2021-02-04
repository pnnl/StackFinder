import os
import re
import boto3
import requests
#from routes import app_config
from routes.send_files.format_soap import FormatSoap
#from format_soap import FormatSoap


class SendFiles():
    def __init__(self):
        """
        send files to specific endpoint
        files being sent will be from aws
        """
        self.client = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_S3_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("AWS_S3_SECRET_KEY"),
            region_name=os.environ.get("REGION")
        )
        self.bucket = "n25-testset"
        self.soap = FormatSoap()
    
    def populate_files_list(self, file_type, number, vendor, **kwargs) -> list:
        """
        loop to gather 5 files with specific file type to be sent to ardis web service
        - input:
            - file_type: message type to be sent to webservice
            - **kwargs: arguments for boto3
        - output: 
            - list of files gathered from boto3
        """
        files = list()
        while len(files) < number:
            data = self.client.list_objects_v2(**kwargs)
            files += list(filter(
                lambda x: ".xml" in x["Key"] and file_type.lower() in x["Key"].lower() and vendor.lower() in x["Key"].lower(), data["Contents"]
            ))
            try:
                kwargs["ContinuationToken"] = data["NextContinuationToken"]
            except KeyError:
                break
        return files[:number]

    def get_file_names(self, file_type, number, vendor) -> list:
        """
        get the files that will be sent from s3 bucket
        - input:
            - file_type: file type that will be sent to test webservice
        - output:
            - list of file names from s3
        """
        kwargs={ "Bucket": self.bucket }
        files =self.populate_files_list(file_type, number, vendor, **kwargs)
        return list(map(lambda x: x["Key"], files))

    def get_file_data(self, filename) -> str:
        """
        get file data from bucket
        - input:
            - filename: filename of s3 object to get data from
        - output:
            - str of data from s3 file
        """
        kwargs = {
            "Bucket": self.bucket,
            "Key": filename
        }
        data = self.client.get_object(**kwargs)
        try:
            return data["Body"].read().decode("utf-16")
        except ValueError:
            return data["Body"].read().decode("utf-8")

    def send_files(self, endpoint, number, file_type, vendor) -> None:
        """
        send files to the endpoint to test that it is working correctly
        - input:
            - endpoint: endpoint of the webservice
            - number: number of files to be sent (less than 5)
            - file_type: message type to be sent
            - vendor: vendor that produced the file
        - output: None
        """
        responses = list()
        files = self.get_file_names(file_type, number, vendor)
        for _file in files:
            xml = self.get_file_data(_file)
            soapxml = self.soap.format_soap(xml)
            req = requests.post(endpoint, data=soapxml.encode("utf-8"))
            resp_xml = self.soap.parse_soap_response(req.text)
            responses.append(
                {
                    "File": _file,
                    "Status": req.status_code,
                    "XML": resp_xml
                }
            )
        return responses







if __name__ == "__main__":
    sf = SendFiles()
    print(sf.send_files("http://ardis-test.pnl.gov/ws/N25Scan.asmx", 1, "Health", "L3"))