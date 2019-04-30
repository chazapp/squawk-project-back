import os
import unittest
from flask import json, jsonify
from squawkapi.app import create_app


class TestClass(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestClass, self).__init__(*args, **kwargs)
        os.environ['FLASK_APP'] = 'squawkapitest'
        os.environ['FLASK_ENV'] = 'development'
        os.environ['MONGO_URI'] = 'mongodb://localhost:27017/squawkTest'
        os.environ['TESTING'] = 'true'

    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        self.token = ''
        self.source_id = ''
        with self.app.app_context():
            data = json.dumps({'username': 'fooobar',
                               'email': 'shad@chaz.pro',
                               'password': 'password'
                               })
            resp = self.client.post('/register', data=data, content_type='application/json')
            if resp.status_code == 409:
                data = json.dumps({'email': 'shad@chaz.pro', 'password': 'password'})
                resp = self.client.post('/auth', data=data, content_type='application/json')
                self.assertEqual(200, resp.status_code)
            self.assertEqual(200, resp.status_code)
            self.token = resp.get_json()['token']
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def tearDown(self):
        pass

    def test_00_register(self):
        with self.app.app_context():
            data = json.dumps({'username': 'fooobar',
                               'email': 'shad@chaz.pro',
                               'password': 'password'
                               })
            resp = self.client.post('/register', data=data, content_type='application/json')
            if resp.status_code == 409:
                resp.status_code = 200
            self.assertEqual(200, resp.status_code)

    def test_01_auth(self):
        with self.app.app_context():
            data = json.dumps({'email': 'shad@chaz.pro',
                               'password': 'password'
                               })
            resp = self.client.post('/auth', data=data, content_type='application/json')
            self.assertEqual(200, resp.status_code)

    def test_02_create_source(self):
        with self.app.app_context():
            data = json.dumps({'link': 'https://reddit.com/r/python.rss',
                               "name": 'Reddit /r/Python',
                               })
            resp = self.client.post('/source', data=data, content_type='application/json',
                                    headers={
                                        "Authorization": 'Bearer ' + self.token
                                    })
            self.assertEqual(201, resp.status_code)
            self.source_id = json.loads(resp.get_data(as_text=True))['source_id']
            data = json.dumps({'link': 'foooobar',
                               "name": 'foooobar',
                               })
            resp = self.client.post('/source', data=data, content_type='application/json',
                                    headers={
                                        "Authorization": 'Bearer ' + self.token
                                    })
            self.assertEqual(400, resp.status_code)

    def test_03_get_sources(self):
        with self.app.app_context():
            resp = self.client.get('/sources', headers={
                "Authorization": "Bearer " + self.token
            })
            self.assertEqual(200, resp.status_code)

    # def test_04_get_content(self):
    #     with self.app.app_context():
    #         uri = '/source/' + self.source_id + '/content'
    #         resp = self.client.get(uri, headers={
    #                                     "Authorization": 'Bearer ' + self.token
    #                                 })
    #         self.assertEqual(200, resp.status_code)
    #
    # def test_05_delete_source(self):
    #     with self.app.app_context():
    #         uri = '/source/' + self.source_id
    #         resp = self.client.delete(uri, headers={
    #                                    "Authorization": 'Bearer ' + self.token
    #                                 })
    #         self.assertEqual(200, resp.status_code)
    #
