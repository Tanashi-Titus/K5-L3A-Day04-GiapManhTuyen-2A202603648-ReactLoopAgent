"""Kiểm tra yêu cầu status snapshot khi đã đọc incident."""
import json
import unittest

from agent import run_agent
from status_tools import StatusTools
from test_lab import FakeProvider, final, tool_call


class SnapshotStatusValidationTests(unittest.TestCase):
    def test_snapshot_question_requests_status_after_incident(self):
        tools = StatusTools()
        detail = tools.get_incident_details('github', 't89g2q1800fr')
        response = 'Incident resolved. ' + detail['url']
        provider = FakeProvider([
            tool_call('detail', 'get_incident_details', json.dumps({
                'provider': 'github', 'incident_id': 't89g2q1800fr'})),
            final(response),
            tool_call('status', 'get_status', json.dumps({'provider': 'github', 'component': 'Actions'})),
            final(response),
        ])
        result = run_agent('Kiểm tra snapshot và incident', provider, tools, max_steps=4)
        self.assertEqual(result['status'], 'completed')
        self.assertTrue(any(event['event'] == 'validation_missing_status' for event in result['trace']))
        self.assertEqual([event['name'] for event in result['trace'] if event['event'] == 'tool'],
                         ['get_incident_details', 'get_status'])

    def test_incident_only_does_not_require_status(self):
        tools = StatusTools()
        detail = tools.get_incident_details('github', 't89g2q1800fr')
        provider = FakeProvider([
            tool_call('detail', 'get_incident_details', json.dumps({
                'provider': 'github', 'incident_id': 't89g2q1800fr'})),
            final('Incident resolved. ' + detail['url']),
        ])
        result = run_agent('Chi tiết incident này?', provider, tools, max_steps=2)
        self.assertEqual(result['status'], 'completed')
        self.assertFalse(any(event['event'] == 'validation_missing_status' for event in result['trace']))
