"""TestRail API binding for Python 3.x.

(API v2, available since TestRail 3.0)

Compatible with TestRail 3.0 and later.

Learn more:

http://docs.gurock.com/testrail-api2/start
http://docs.gurock.com/testrail-api2/accessing

Copyright Gurock Software GmbH. See license.md for details.
"""

import base64
import json

import requests
import subprocess


class APIClient:
    def __init__(self, base_url):
        self.user, self.password = self.get_test_rail_info_from_1password()
        if not base_url.endswith('/'):
            base_url += '/'
        self.__url = base_url + 'index.php?/api/v2/'

    def get_test_rail_info_from_1password(self):
        try:
            # login to 1password
            # subprocess.run(
            #     ["op", "signin"],
            #     capture_output=True,
            #     text=True
            # )

            # # get testrail api key from 1password
            # result = subprocess.run(
            #     ["op", "item", "get", "TestRail-API key-SH", "--format", "json"],
            #     capture_output=True,
            #     text=True,
            #     check=True
            # )
            # item = json.loads(result.stdout)
            # item_id = item['id']
            #
            # # get testrail email and password from 1password
            # result_credential = subprocess.run(
            #     ["op", "item", "get", item_id, "--reveal", "--format", "json"],
            #     capture_output=True,
            #     text=True,
            #     check=True
            # )
            # item_credential = json.loads(result_credential.stdout)
            # email = item_credential['fields'][4]['value']
            # credential = item_credential['fields'][2]['value']

            # get email and password from 1password
            email_result = subprocess.run(
                ["op", "read", "op://Shanghai QA/TestRail-API key-SH/email"],
                capture_output=True,
                text=True,
                check=True
            )
            email = email_result.stdout.strip()

            credential_result = subprocess.run(
                ["op", "read", "op://Shanghai QA/TestRail-API key-SH/credential"],
                capture_output=True,
                text=True,
                check=True
            )
            credential = credential_result.stdout.strip()

            return email, credential
        except subprocess.CalledProcessError as e:
            raise APIError(f"Error getting TestRail API key from 1password: %s" % e.stderr)


    def send_get(self, uri, filepath=None):
        """Issue a GET request (read) against the API.

        Args:
            uri: The API method to call including parameters, e.g. get_case/1.
            filepath: The path and file name for attachment download; used only
                for 'get_attachment/:attachment_id'.

        Returns:
            A dict containing the result of the request.
        """
        return self.__send_request('GET', uri, filepath)

    def send_post(self, uri, data):
        """Issue a POST request (write) against the API.

        Args:
            uri: The API method to call, including parameters, e.g. add_case/1.
            data: The data to submit as part of the request as a dict; strings
                must be UTF-8 encoded. If adding an attachment, must be the
                path to the file.

        Returns:
            A dict containing the result of the request.
        """
        return self.__send_request('POST', uri, data)

    def __send_request(self, method, uri, data):
        url = self.__url + uri

        auth = str(
            base64.b64encode(
                bytes('%s:%s' % (self.user, self.password), 'utf-8')
            ),
            'ascii'
        ).strip()
        headers = {'Authorization': 'Basic ' + auth}

        if method == 'POST':
            if uri[:14] == 'add_attachment':    # add_attachment API method
                # files = {'attachment': (open(data, 'rb'))}
                with open(data, 'rb') as f:
                    files = {'attachment': f}
                    response = requests.post(url, headers=headers, files=files)
                # files['attachment'].close()

            else:
                headers['Content-Type'] = 'application/json'
                payload = bytes(json.dumps(data), 'utf-8')
                response = requests.post(url, headers=headers, data=payload)
                # response = requests.post(url, headers=headers, json=data)
        else:
            headers['Content-Type'] = 'application/json'
            response = requests.get(url, headers=headers)

        response.raise_for_status()

        if response.status_code > 201:
            try:
                error = response.json()
            except:     # response.content not formatted as JSON
                error = str(response.content)
            raise APIError('TestRail API returned HTTP %s (%s)' % (response.status_code, error))
        else:
            if uri[:15] == 'get_attachment/':   # Expecting file, not JSON
                try:
                    open(data, 'wb').write(response.content)
                    return (data)
                except:
                    return ("Error saving attachment.")
            else:
                try:
                    return response.json()
                except: # Nothing to return
                    return {}



class APIError(Exception):
    pass
