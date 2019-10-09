# *****************************************************************
#
# Licensed Materials - Property of IBM
#
# (C) Copyright IBM Corp. 2018. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
#
# *****************************************************************

import io
import json
import logging
import os
import shlex
import subprocess
import sys
import unittest

# Put the local module at the beginning of the path in case there's an installed
# copy on the system
local_module = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'alog'))
sys.path = [local_module] + sys.path
import alog

# Note on log capture: In these tests, we could attach a stream capture handler,
# but logs captured that way will not include formatting, so that doesn't work
# for these tests. Instead, we run python subprocesses and capture the logging
# results.

def get_subproc_cmds(lines):
    commands_to_run = "python3 -c \"import alog;"
    for line in lines:
        commands_to_run += " %s;" % line
    commands_to_run += "\""
    return commands_to_run

class TestJsonCompatibility(unittest.TestCase):
    '''Ensures that printed messages are valid json format when json formatting is specified'''

    def test_merge_msg_json(self):
        '''Tests that dict messages are merged when using json format. May be too complicated...'''
        # Set up the subprocess command
        commands_to_run = get_subproc_cmds([
            "alog.configure(default_level='info', filters='', formatter='json')",
            "test_channel = alog.use_channel('test_merge_msg_json')",
            "test_channel.info(dict({'test_msg':1}))",
        ])

        # run in subprocess and capture stderr
        _, stderr = subprocess.Popen(shlex.split(commands_to_run), stderr=subprocess.PIPE).communicate()
        logged_output = json.loads(stderr)

        self.assertIsNotNone(logged_output)
        self.assertIsInstance(logged_output, dict)

        for key in logged_output.keys():
            # should have merged all dict's!
            self.assertNotIsInstance(logged_output[key], dict)
        # key should be present if the message was merged into top-level dict
        self.assertIn('test_msg', logged_output)
        # value should be the same
        self.assertEqual(logged_output['test_msg'], 1)

    def test_empty_msg_json(self):
        '''Tests that logs are in json format with an empty message. May be too complicated...'''
        # Set up the subprocess command
        commands_to_run = get_subproc_cmds([
            "alog.configure(default_level='info', filters='', formatter='json')",
            "test_channel = alog.use_channel('test_merge_msg_json')",
            "test_channel.info('')",
        ])

        # run in subprocess and capture stderr
        _, stderr = subprocess.Popen(shlex.split(commands_to_run), stderr=subprocess.PIPE).communicate()
        logged_output = json.loads(stderr)

        self.assertIsInstance(logged_output, dict)

class TestCustomFormatter(unittest.TestCase):

    def test_pretty_with_args(self):
        '''Tests that a manually constructed AlogPrettyFormatter can be used'''
        alog.configure('info', '', formatter=alog.AlogPrettyFormatter(10))

if __name__ == "__main__":
    # has verbose output of tests; otherwise just says all passed or not
    unittest.main(verbosity=2)
