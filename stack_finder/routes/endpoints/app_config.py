import os


CLIENT_SECRET = os.getenv("CLIENT_SECRET") # Our Quickstart uses this placeholder
# In your production app, we recommend you to use other ways to store your secret,
# such as KeyVault, or environment variable as described in Flask"s documentation here
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# if not CLIENT_SECRET:
#     raise ValueError("Need to define CLIENT_SECRET environment variable")

AUTHORITY = "https://login.microsoftonline.com/pnnl.gov"
# AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
# AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"

CLIENT_ID = os.getenv("CLIENT_ID")

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = "https://graph.microsoft.com/v1.0/me/memberOf"  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

SESSION_TYPE = "filesystem"  # So token cache will be stored in server-side session

# tags to filter on, add new tags with comma "," seperation
TAGS=["stack-finder"]

# group id or id's that you would like to filter on
# these can be found at: https://portal.azure.com
GROUP_ID=[
    "6244b1cd-56a0-4f32-b192-9f418cf7239f", # panda-viking group
    "614be0eb-4e41-4ccf-99b6-a702572671a4", # ardis aws group
    "0ba160f8-742c-4ec2-8d5a-60df11b66d95",  # ardis adfs group
    #"c5b17646-d605-48ef-b405-a66545f5dd7a"  # voltron - testing to make sure i get blocked
]

# provide users that you would like to add
GROUP=[
    "henry.macias@pnnl.gov",
    "bryan.gerber@pnnl.gov",
    "juan.barajas@pnnl.gov",
    "devin.wright@pnnl.gov"
]