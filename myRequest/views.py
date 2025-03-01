from django.shortcuts import render
import requests
from django.conf import settings as config
import datetime as dt
from requests.auth import HTTPBasicAuth
from zeep.client import Client
from zeep.transports import Transport
from requests import Session
from django.http import HttpResponseRedirect
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import secrets
import string
import base64
import imghdr
from PIL import Image
from io import BytesIO
from cryptography.fernet import Fernet


session = None


# Create your views here.
class UserObjectMixins(object):
    model = None
    sessions = requests.Session()
    sessions.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    O_DATA_AUTH = aiohttp.BasicAuth(config.WEB_SERVICE_UID, config.WEB_SERVICE_PWD)
    cipher_suite = Fernet(config.ENCRYPT_KEY)

    async def fetch_data(self, session, username, password, endpoint, property, filter):
        auth = aiohttp.BasicAuth(login=username, password=password)
        async with session.get(
            config.O_DATA.format(
                f"{endpoint}?$filter={property}%20{filter}%20%27{username}%27"
            ),
            auth=auth,
        ) as res:
            data = await res.json()
            response = {"status_code": res.status, "data": data["value"]}
            return response

    async def simple_fetch_data(self, session, endpoint):
        async with session.get(
            config.O_DATA.format(endpoint), auth=self.O_DATA_AUTH
        ) as res:
            data = await res.json()
            response = data["value"]
            return response

    async def fetch_one_filtered_data(
        self, session, endpoint, property, filter, field_name
    ):
        async with session.get(
            config.O_DATA.format(
                f"{endpoint}?$filter={property}%20{filter}%20%27{field_name}%27"
            ),
            auth=self.O_DATA_AUTH,
        ) as res:
            data = await res.json()
            response = {"status_code": res.status, "data": data["value"]}
            return response

    async def simple_one_filtered_data(
        self, session, endpoint, property, filter, field_name
    ):
        async with session.get(
            config.O_DATA.format(
                f"{endpoint}?$filter={property}%20{filter}%20%27{field_name}%27"
            ),
            auth=self.O_DATA_AUTH,
        ) as res:
            data = await res.json()
            response = data["value"]
            return response

    async def simple_double_filtered_data(
        self,
        session,
        endpoint,
        property_x,
        filter_x,
        filed_name_x,
        operater_1,
        property_y,
        filter_y,
        field_name_y,
    ):
        async with session.get(
            config.O_DATA.format(
                f"{endpoint}?$filter={property_x}%20{filter_x}%20%27{filed_name_x}%27%20{operater_1}%20{property_y}%20{filter_y}%20%27{field_name_y}%27"
            ),
            auth=self.O_DATA_AUTH,
        ) as res:
            data = await res.json()
            response = data["value"]
            return response

    def make_soap_request(self, soap_headers, endpoint, *params):
        global session
        if not session:
            session = Session()
            session.auth = HTTPBasicAuth(
                soap_headers["username"], soap_headers["password"]
            )
        with ThreadPoolExecutor() as executor:
            client = Client(config.BASE_URL, transport=Transport(session=session))
            response = executor.submit(client.service[endpoint], *params).result()
        return response

    def upload_attachment(self, soap_headers, *params):
        global session
        if not session:
            session = Session()
            session.auth = HTTPBasicAuth(
                soap_headers["username"], soap_headers["password"]
            )
        with ThreadPoolExecutor() as executor:
            client = Client(config.BASE_URL, transport=Transport(session=session))
            response = executor.submit(
                client.service["FnUploadAttachement"], *params
            ).result()
        return response

    def delete_attachment(self, soap_headers, *params):
        global session
        if not session:
            session = Session()
            session.auth = HTTPBasicAuth(
                soap_headers["username"], soap_headers["password"]
            )
        with ThreadPoolExecutor() as executor:
            client = Client(config.BASE_URL, transport=Transport(session=session))
            response = executor.submit(
                client.service["FnDeleteDocumentAttachment"], *params
            ).result()
        return response

    def pass_encrypt(self, password):
        encrypted_text = self.cipher_suite.encrypt(password.encode("ascii"))
        encrypted_password = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
        return encrypted_password

    def pass_decrypt(self, password):
        Portal_Password = base64.urlsafe_b64decode(password)
        decoded_text = self.cipher_suite.decrypt(Portal_Password).decode("ascii")
        return decoded_text

    def get_object(self, endpoint):
        response = requests.get(
            endpoint, auth=HTTPBasicAuth(config.WEB_SERVICE_UID, config.WEB_SERVICE_PWD)
        ).json()
        return response

    def get_image_format(encoded_string):
        decoded_data = base64.b64decode(encoded_string)
        image_format = imghdr.what(None, h=decoded_data)
        return image_format

    def decode_image(encoded_string, image_format):
        img_data = base64.b64decode(encoded_string)
        img = Image.open(BytesIO(img_data))
        return image_format, img

    def one_filter(self, endpoint, property, filter, field_name):
        Access_Point = config.O_DATA.format(
            f"{endpoint}?$filter={property}%20{filter}%20%27{field_name}%27"
        )
        response = self.get_object(Access_Point)["value"]
        count = len(response)
        return count, response

    def double_filtered_data(
        self,
        endpoint,
        property_x,
        filter_x,
        filed_name_x,
        operater_1,
        property_y,
        filter_y,
        field_name_y,
    ):
        Access_Point = config.O_DATA.format(
            f"{endpoint}?$filter={property_x}%20{filter_x}%20%27{filed_name_x}%27%20{operater_1}%20{property_y}%20{filter_y}%20%27{field_name_y}%27"
        )
        response = self.get_object(Access_Point)["value"]
        count = len(response)
        return count, response

    def triple_filtered_data(
        self,
        endpoint,
        property_x,
        filter_x,
        filed_name_x,
        operater_1,
        property_y,
        filter_y,
        field_name_y,
        operater_2,
        property_z,
        filter_z,
        field_name_z,
    ):
        Access_Point = config.O_DATA.format(
            f"{endpoint}?$filter={property_x}%20{filter_x}%20%27{filed_name_x}%27%20{operater_1}%20{property_y}%20{filter_y}%20%27{field_name_y}%27%20{operater_2}%20{property_z}%20{filter_z}%20%27{field_name_z}%27"
        )
        response = self.get_object(Access_Point)["value"]
        count = len(response)
        return count, response

    def zeep_client(self, request):
        Username = request.session["User_ID"]
        Password = request.session["password"]
        AUTHS = Session()
        AUTHS.auth = HTTPBasicAuth(Username, Password)
        CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
        return CLIENT

    def comparison_double_filter(
        self,
        endpoint,
        property_x,
        filter_x,
        field_name,
        operater_1,
        property_y,
        filter_y,
        property_z,
    ):
        Access_Point = config.O_DATA.format(
            f"{endpoint}?$filter={property_x}%20{filter_x}%20%27{field_name}%27%20{operater_1}%20{property_y}%20{filter_y}%20{property_z}"
        )
        response = self.get_object(Access_Point)["value"]
        count = len(response)
        return count, response

    def quotes(self):
        category = "health"
        QUOTES_API_KEY = "EIvOjryX23PBwPSqeoWNbA==52tdKajnJVd8uImQ"
        api_url = "https://api.api-ninjas.com/v1/quotes?category={}".format(category)
        try:
            response = requests.get(api_url, headers={"X-Api-Key": QUOTES_API_KEY})
            if response.status_code == requests.codes.ok:
                return response.json()
        except Exception as e:
            return None


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200
