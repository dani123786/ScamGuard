import unittest
from unittest.mock import patch
import data.checkers as checkers


class ApiResilienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_check_url_normalizes_percent_encoded_input(self):
        with patch('routes.api.analyze_url_with_ai') as mock_analyze:
            mock_analyze.return_value = {
                'risk_score': '85%',
                'risk_level': 'high',
                'scam_type': 'Phishing',
                'confidence': 'medium',
                'summary': 'Encoded URL looked suspicious.',
                'red_flags': 'Percent-encoded redirect',
                'recommendation': 'Avoid visiting the site.',
                'what_scammer_wants': 'Credentials',
                'domain_analysis': {
                    'domain': '',
                    'is_impersonating': 'yes',
                    'impersonating_brand': 'PayPal',
                    'suspicious_patterns': 'encoded redirect'
                }
            }

            response = self.client.post('/api/check/url', json={
                'url': 'paypal.com%2Flogin%3Fnext%3Dsecure'
            })

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['risk_score'], 85)
        self.assertEqual(payload['risk_level'], 'HIGH')
        self.assertEqual(payload['confidence'], 'MEDIUM')
        self.assertEqual(payload['analyzed_url'], 'https://paypal.com/login?next=secure')
        self.assertEqual(payload['domain_analysis']['domain'], 'paypal.com')
        self.assertEqual(payload['domain_analysis']['is_impersonating'], 'YES')
        self.assertEqual(payload['red_flags'], ['Percent-encoded redirect'])

    def test_check_url_rejects_invalid_url(self):
        response = self.client.post('/api/check/url', json={'url': 'https://'})
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertEqual(payload['error'], 'Invalid URL')

    def test_check_endpoint_recovers_stringified_ai_json(self):
        raw_result = """
```json
{
  "risk_score": "72%",
  "risk_level": "medium",
  "scam_type": "Credential Harvesting",
  "confidence": "high",
  "summary": "Suspicious request for account details.",
  "red_flags": ["Urgent language", "Password request"],
  "recommendation": "Do not reply.",
  "what_scammer_wants": "Account access"
}
```
"""
        with patch('routes.api.analyze_with_ai', return_value=raw_result):
            response = self.client.post('/api/check', json={
                'type': 'email',
                'content': 'Reset your password immediately.'
            })

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['risk_score'], 72)
        self.assertEqual(payload['risk_level'], 'MEDIUM')
        self.assertEqual(payload['confidence'], 'HIGH')
        self.assertEqual(payload['red_flags'], ['Urgent language', 'Password request'])
        self.assertTrue(payload['ai_powered'])

    def test_check_url_preserves_fallback_ai_status(self):
        with patch('routes.api.analyze_url_with_ai', return_value={
            'risk_score': 50,
            'risk_level': 'UNKNOWN',
            'risk_color': 'warning',
            'scam_type': 'Unable to Analyse',
            'confidence': 'LOW',
            'summary': 'AI analysis temporarily unavailable.',
            'red_flags': ['Temporary outage'],
            'legitimate_aspects': [],
            'recommendation': 'Try again later.',
            'what_scammer_wants': 'N/A',
            'domain_analysis': {
                'domain': 'paypal.com',
                'is_impersonating': 'UNKNOWN',
                'impersonating_brand': 'N/A',
                'suspicious_patterns': []
            },
            'model_used': 'none',
            'ai_powered': False
        }):
            response = self.client.post('/api/check/url', json={'url': 'https://paypal.com/login'})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload['ai_powered'])

    def test_analysis_retries_when_first_result_is_incomplete(self):
        side_effects = [
            {
                'risk_score': 50,
                'risk_level': 'UNKNOWN',
                'risk_color': 'warning',
                'scam_type': 'Unable to fully analyse',
                'confidence': 'LOW',
                'summary': 'Analysis was partially completed.',
                'red_flags': [],
                'legitimate_aspects': [],
                'recommendation': 'Exercise caution — analysis was incomplete.',
                'what_scammer_wants': 'N/A',
            },
            {
                'risk_score': 86,
                'risk_level': 'HIGH',
                'risk_color': 'danger',
                'scam_type': 'Phishing',
                'confidence': 'HIGH',
                'summary': 'The message pressures the user to reveal credentials.',
                'red_flags': ['Urgent threat', 'Credential request'],
                'legitimate_aspects': ['Uses a recognizable brand name'],
                'recommendation': 'Do not click the link and verify through the official website.',
                'what_scammer_wants': 'Bank login credentials',
                'model_used': 'gemini-2.5-flash'
            }
        ]

        with patch('data.checkers._call_gemini', side_effect=side_effects) as mock_call:
            result = checkers.analyze_with_ai('Reset your bank password right now.', 'message')

        self.assertEqual(mock_call.call_count, 2)
        self.assertEqual(result['risk_score'], 86)
        self.assertEqual(result['risk_level'], 'HIGH')
        self.assertEqual(result['scam_type'], 'Phishing')
        self.assertEqual(result['what_scammer_wants'], 'Bank login credentials')

    def test_report_analysis_is_normalized_with_summary_and_details(self):
        side_effects = [
            {
                'severity': 'HIGH'
            },
            {
                'severity': 'HIGH',
                'scam_category': 'Investment Scam',
                'summary': 'The report describes a high-pressure attempt to obtain money.',
                'common_patterns': ['Urgent payment request'],
                'red_flags_identified': ['Promises guaranteed returns'],
                'victim_advice': 'Stop sending money and contact your bank immediately.',
                'prevention_tips': ['Verify the company through official regulators.'],
                'should_report_to_authorities': 'YES',
                'authorities_to_contact': ['FTC'],
                'community_impact': 'Others may be targeted with the same fake investment pitch.'
            }
        ]

        with patch('data.checkers._call_gemini', side_effect=side_effects) as mock_call:
            result = checkers.analyze_report_with_ai({
                'scam_type': 'investment',
                'contact_method': 'email',
                'lost_money': 'yes',
                'amount': '$2000',
                'description': 'They promised 20 percent daily returns if I sent crypto.'
            })

        self.assertEqual(mock_call.call_count, 2)
        self.assertEqual(result['severity'], 'HIGH')
        self.assertEqual(result['scam_category'], 'Investment Scam')
        self.assertIn('high-pressure', result['summary'])
        self.assertTrue(result['red_flags_identified'])
        self.assertTrue(result['prevention_tips'])
        self.assertEqual(result['should_report_to_authorities'], 'YES')


if __name__ == '__main__':
    unittest.main()
