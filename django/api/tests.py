import json

from django.test import TestCase, Client

from django.contrib.auth import get_user_model

from . import models as ApiModels

"""
If your tests rely on database access such as creating or querying models, be sure to create your test classes as subclasses of django.test.TestCase rather than unittest.TestCase.
https://docs.djangoproject.com/en/2.2/topics/testing/overview/

Run these tests by `python manage.py test --settings=django_server.test_settings`
"""

# Create your tests here.
class ObjectUnitTest:
    
    class BaseTestCases(TestCase):
        def setUp(self):
            super().setUp()

            self.endpoint_url = None
            self.create_object_data = None

            self.credentials = {
                'username': 'testuser',
                'password': 'testuserpassword'
            }
            self.client = Client()
            self.User = get_user_model()
            
            self.user = self.User.objects.create_user(**self.credentials)

            self.assertEqual(
                self.client.login(**self.credentials), True
            )
            
        def tearDown(self):
            super().tearDown()

        
        """
            Helper Functions
        """
        
        def clientApiCall(self, method, endpoint_url, data={}, **kwargs):
            
            method = method.lower()

            if data:
                data = json.dumps(data)
            
            response = getattr(self.client, method)(
                endpoint_url,
                data,
                content_type='application/json',
                **kwargs
            )
            self.assertTrue(200 <= response.status_code < 400)
            if method != 'delete':
                parsed_response = json.loads(response.content)
                return parsed_response
        
        def createObject(self):
            parsed_response = self.clientApiCall('post', 
                self.endpoint_url, 
                data=self.create_object_data,
            )
            uuid = parsed_response['uuid']

            return uuid
        
        def getObjectList(self):
            parsed_response = self.clientApiCall(
                'get',
                self.endpoint_url
            )

            self.assertTrue(
                'results' in parsed_response
            )
            object_list = parsed_response['results']

            return object_list
        
        def getObject(self, uuid):
            res = self.clientApiCall(
                'get',
                f'{self.endpoint_url}{uuid}/'
            )

            return res
        
        """
            Test Cases
        """
        
        def testObjectCreate(self):
            # create an object
            uuid = self.createObject()

            # get objects, see if our created object is in there
            object_list = self.getObjectList()

            self.assertTrue(
                any(
                    model_object['uuid'] == uuid 
                    for model_object in object_list
                ),
                True
            )
        
        def testObjectUpdate(self):
            uuid = self.createObject()
            
            model_object = self.getObject(uuid)

            self.assertTrue(uuid == model_object['uuid'])

            res = self.clientApiCall(
                'patch',
                f'{self.endpoint_url}{uuid}/',
                data=self.update_object_data
            )
            for field in self.update_object_data.keys():
                self.assertEqual(
                    res[field], self.update_object_data[field]
                )
        
        def testObjectDelete(self):
            uuid = self.createObject()

            created_model_object = self.getObject(uuid)
            self.assertTrue(uuid == created_model_object['uuid'])

            self.clientApiCall(
                'delete',
                f'{self.endpoint_url}{uuid}/',
            )

            object_list = self.getObjectList()
            self.assertTrue(
                all(
                    model_object['uuid'] != uuid 
                    for model_object in object_list
                ),
                True
            )

class CompanyTestCase(ObjectUnitTest.BaseTestCases):
    
    def setUp(self):
        super().setUp()
        self.endpoint_url = '/api/companies/'
        self.create_object_data = {
            'name': 'Test Company',
            'hq_location': {
                'full_address': 'MI Michigan State, 48105'
            },
            'home_page': {
                'url': 'example.com',
                'text': 'test link'
            }
        }
        self.update_object_data = {
            'name': 'Updated Company Name'
        }

class ApplicationTestCase(ObjectUnitTest.BaseTestCases):
    
    def setUp(self):
        super().setUp()
        self.endpoint_url = '/api/applications/'

        # create company for application first
        company = ApiModels.Company.objects.create(
            user=self.user,
            name='test company'
        )
        company.save()

        self.create_object_data = {
            'user_company': str(company.uuid),
            'position_title': 'Test Developer',
            'job_description_page': {
                'url': 'jd.example.com',
                'text': 'test JD link'
            },
            'job_source': {
                'url': 'job-source.example.com',
                'text': 'test job source link'
            }
        }
        self.update_object_data = {
            'position_title': 'Updated Test Developer'
        }


class ApplicationStatusTestCase(ObjectUnitTest.BaseTestCases):
    
    def setUp(self):
        super().setUp()
        self.endpoint_url = '/api/application-statuses/'

        # create company for application first
        company = ApiModels.Company.objects.create(
            name='Test Company',
            user=self.user
        )
        company.save()
        application = ApiModels.Application.objects.create(
            user=self.user,
            user_company=company,
            position_title='Test Developer',
        )

        self.create_object_data = {
            'application': str(application.uuid),
            'text': 'Test Status',
            'date': '2019-04-12',
            'applicationstatuslink_set': [],
        }
        self.update_object_data = {
            'text': 'Updated Status'
        }