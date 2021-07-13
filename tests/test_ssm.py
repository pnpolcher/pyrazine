import unittest

import boto3
from moto import mock_ssm

from pyrazine.config.ssm import SSMConfigurationReader


class SSMTest(unittest.TestCase):

    TEST_PARAMETERS = [
        {
            'Name': 'test-param-1',
            'Value': 'test-1',
            'Type': 'String',
        },
        {
            'Name': 'test-param-2',
            'Value': 'a,b,c,d,e,f,g,h',
            'Type': 'StringList',
        },
        {
            'Name': 'test-param-3',
            'Value': 'test-3',
            'Type': 'SecureString',
        },
    ]

    @staticmethod
    def _put_parameters(ssm):
        for param in SSMTest.TEST_PARAMETERS:
            ssm.put_parameter(
                Name=param['Name'],
                Value=param['Value'],
                Type=param['Type'],
            )

    @mock_ssm
    def test_read(self):
        ssm = boto3.client('ssm')
        self._put_parameters(ssm)

        reader = SSMConfigurationReader(decrypt_parameters=False)

        for param in self.TEST_PARAMETERS:
            value = reader.read(param['Name'])
            if param['Type'] == 'SecureString':
                self.assertEqual(value, 'kms:alias/aws/ssm:%s' % param['Value'])
            elif param['Type'] == 'StringList':
                self.assertEqual(value, param['Value'].split(','))
            else:
                self.assertEqual(value, param['Value'])

        reader = SSMConfigurationReader(decrypt_parameters=True)

        for param in self.TEST_PARAMETERS:
            value = reader.read(param['Name'])
            if param['Type'] == 'StringList':
                self.assertEqual(value, param['Value'].split(','))
            else:
                self.assertEqual(value, param['Value'])

    @mock_ssm
    def test_read_all(self):
        ssm = boto3.client('ssm')
        self._put_parameters(ssm)

        reader = SSMConfigurationReader(
            decrypt_parameters=False,
            app_prefix='/',
        )
        params = reader.read_all()
        for source_param in self.TEST_PARAMETERS:
            if source_param['Name'] not in params:
                self.fail('Missing parameter: %s' % source_param['Name'])
            value = params[source_param['Name']]
            if source_param['Type'] == 'SecureString':
                self.assertEqual(value, 'kms:alias/aws/ssm:%s' % source_param['Value'])
            elif source_param['Type'] == 'StringList':
                self.assertEqual(value, source_param['Value'].split(','))
            else:
                self.assertEqual(value, source_param['Value'])

        reader = SSMConfigurationReader(
            decrypt_parameters=True,
            app_prefix='/',
        )
        params = reader.read_all()
        for source_param in self.TEST_PARAMETERS:
            if source_param['Name'] not in params:
                self.fail('Missing parameter: %s' % source_param['Name'])
            value = params[source_param['Name']]

            if source_param['Type'] == 'StringList':
                self.assertEqual(value, source_param['Value'].split(','))
            else:
                self.assertEqual(value, source_param['Value'])
