### Stack Finder
Python Flask web application used to easily access resources created with AWS Cloud Development Kit (CDK) and CloudFormation. When using CI/CD to deploy dedicated AWS infrastructure per branch, it can be difficult to keep track of what resources are tied to which branch, and application. When the AWS Console S3 bucket list shows 100 buckets, and you aren't quite sure which one is yours... StackFinder can help! Just tag your CloudFormation (or CDK) builds with "stack-finder" (or other configurable tag names). They'll show up in the StackFinder UI along with easy links to access AWS resources for your application. The app only requires read/list IAM permissions on a few resources to work, unlike other open source stack management software that supports adding/deleting stacks.

Stacks tagged with "stack-finder" or other customizable tag will show in the main UI:

![Stack list](https://github.com/pnnl/StackFinder/blob/master/img/stack-list.png)

Clicking into a Stack will show the AWS resources, and optionally a link to the build (Jenkins, Bamboo, TravisCI) that created the stack. Making it super easy for teams to get to Cloudwatch logs, debugging endpoints, and tracing back to the source code for a running application.

![Stack Detail View](https://github.com/pnnl/StackFinder/blob/master/img/stack-view.png)


* ### Endpoints with UI
    * ##### /stacks
        * list of stacks currently in Cloudformation
    * ##### /stacks/login
        * used to login user
    * ##### /stacks/\<stack name\>/outputs
        * outputs that the stack has

* ### Optional Endpoints / Used when not using AD group filtering
    * ##### /stacks/users
        * show users that have been specied in app_config.py
    * ##### /stacks/users/adduser
        * give a user access to the website from their pnnl email address (example@pnnl.gov)
    * ##### /stacks/users/removeuser
        * remove a users access to the website

* ### API Endpoints
    * ##### /stacks-api/login
        * gives the front end information necessary to login
    * ##### /stack-api/user
        * gives the application the current user of the application
    * ##### /stack-api/stacks
        * gives a list of stacks to show
    * ##### /stack-api/outputs
        * gives a list of outputs for a given stack
    * ##### /stack-api/outputs/bucket
        * * build URL for AWS bucket
    * ##### /stack-api/outputs/logs
        * build URL for AWS logs
    * ##### /stack-api/outputs/servicepage
        * build URL for AWS service page


* ### Authentication
    * Authentication is done with PNNL AD, if the user is not apart of it will not allow access
    * Group Authentication, if the user is not apart of the specified group in AD, user will be denied


* ### app_config.py
    * located: ``` stack_finder/routes/endpoints ```
    * ``` 
        CLIENT_SECRET = os.getenv('CLIENT_SECRET') # Our Quickstart uses this placeholder
        # In your production app, we recommend you to use other ways to store your secret,
        # such as KeyVault, or environment variable as described in Flask's documentation here
        # https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
        # CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        # if not CLIENT_SECRET:
        #     raise ValueError("Need to define CLIENT_SECRET environment variable")

        AUTHORITY = "https://login.microsoftonline.com/pnnl.gov"
        # AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
        # AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"

        CLIENT_ID = os.getenv('CLIENT_ID')

        # You can find more Microsoft Graph API endpoints from Graph Explorer
        # https://developer.microsoft.com/en-us/graph/graph-explorer
        ENDPOINT = "https://graph.microsoft.com/v1.0/me/memberOf"  # This resource requires no admin consent

        # You can find the proper permission names from this document
        # https://docs.microsoft.com/en-us/graph/permissions-reference
        SCOPE = ["User.ReadBasic.All"]

        SESSION_TYPE = "filesystem"  # So token cache will be stored in server-side session

        # bucket to grab testset data from, this can be changed to 
        # a different bucket that has data if desired
        BUCKET="temp-bucket"

        # tags to filter on, add new tags with comma ',' seperation
        TAGS=["stack-finder"]

        # group id or id's that you would like to filter on
        # these can be found at: https://portal.azure.com
        GROUP_ID=[
            "12345678-abcd-1234-abcd-123456789abc"
        ]

        # provide users that you would like to add
        GROUP=[
            "first.last@domain.com",
            "first.last@domain.com"
        ]
        ```

    * CLIENT_SECRET: Key that has been giving to the application to access AD
    * AUTHORITY: Endpoint to hit to authorize single sign on to application
    * CLIENT_ID: Application ID that AD knows the application as
    * SCOPE: Graph permissions references
    * SESSION_TYPE: Where the cache token should be saved
    * BUCKET: Where to get test data to be send to endpoint (this can be omitted if now using with data pipeline)
    * TAGS: What to filter stacks on
        * if left empty it will grab all stacks
    * GROUP_ID: IDs to filter users on. these groups can be found at <a href="https://portal.azure.com">https://portal.azure.com</a>
    * GROUP: Used to filter users based on a specified list of users
        * this is an optional variable when using AD group filtering
        * if using certificate auth and group filtering (PNNL cert) then a login page will need to be made to filter by username. 

* ### How to Run Locally
    * Add AWS Region, ID, and Secret to the docker-compose.yml
    * Run ```docker-compose up```


* ### How to Deploy to AWS
    * create 2 scripts
        * ``` stack_finder/build_docker.sh ``` (or another name you would like to use)
        * ``` AWS-CDK/build_cdk.sh ``` (or another name you would like to use)
    * stack_finder/build_docker.sh
        * ```
            #! /usr/bin/env bash

            $( aws ecr get-login --no-include-email )
            num=<tag to be used to mark docker image>
            docker -D build --build-arg secret="<secret for AD>" --build-arg id="<ID for AD>" -t <ECR URI>:1.$num .
            docker push <ECR URI>:1.$num
            ```
        * num: an incremental number to attach to docker image
    * AWS-CDK/build_cdk.sh
        * ```
            #! /usr/bin/env bash

            export AWS_ACCESS_KEY="<aws access key of user>"
            export AWS_SECRET_KEY="<aws secret key of user>"
            export REGION="us-west-2"
            export TAG="<tag to be used to make docker image"

            cdk deploy
            ```
        * AWS_ACCESS_KEY: AWS User access key to run the script as that user
        * AWS_SECRET_KEY: AWS User secret key to run the script as that user
        * REGION: Region to build the resources in (default for our stuff is us-west-2)
        * TAG: an incremental number used to grab docker image from ECR (Elastic Container Register)
    * Run stack_finder/build_docker.sh before AWS-CDK/build_cdk.sh

* ### Adding Dedicated AWS User in AWS
    * Adding an IAM user is a good idea to make sure the user has minimum permissions to do its job
    * Example Inline Policy:
        * ```
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "VisualEditor0",
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "cloudformation:ListExports",
                            "cloudformation:ListStacks",
                            "s3:ListAllMyBuckets",
                            "s3:ListBucket",
                            "cloudformation:DescribeStacks"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            ```
        * This policy is the least amount of permissions needed for this application

* ### How to run UnitTests (Template file provided: ``` runtests.template ```)
    * ##### Make sure pytests is installed (if used requirements.txt it will have been installed)
    * create script ``` runtests.sh ``` (or another name you would like to use)
        * ```
            #! /usr/bin/env bash
            
            export TESTING=1                                    # let the application know we are testing
            export STACK="aws-stack"                            # the default stack I am using
            export BUCKET="temp-bucket"                         # bucket the test stack is using
            export WEBSERVICE_NAME="aws-stack"                  # webservice name on AWS
            export CLUSTER="aws-cluster"                        # cluster the webservice is on
            export LOG_GROUP="/ecs/aws-stack"                   # log group the webservice writes to

            pytest -v
            ```
        * STACK: a default stack that I know exists in cloudformation currently
        * BUCKET: a bucket that the stack uses and outputs in cloudformation
        * WEBSERVICE_NAME: name of the service in ECS
        * CLUSTER: cluster that the webservice belongs to
        * LOG_GROUP: the log group that the webservice writes to and outputs in cloudformation
    * now run the script, if no errors are found the flask application is ready to go!
        * <i> if running tests on a server without network connection the "test_can_send_files()" will fail, comment this out to continue test</i>

* ### Important Websites
    * <a href="https://docs.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0">Graph API Documentation</a>
    * <a href="https://portal.azure.com">Azuze Portal</a>
    * <a href="https://boto3.amazonaws.com/v1/documentation/api/latest/index.html">Boto3 Documentation</a>
    * <a href="https://docs.aws.amazon.com/cdk/api/latest/docs/aws-construct-library.html">CDK Documentation</a>

* ### More Information
    * for more information email: <a href="mailto:henry.macias@pnnl.gov">henry.macias@pnnl.gov</a>
