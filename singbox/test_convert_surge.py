import json
from pathlib import Path
import tempfile
import unittest

from convert_surge import clean_line, convert, write_atomic


class SurgeRuleSetsTest(unittest.TestCase):
    def test_condition_kinds_remain_or(self):
        result, count, skipped = convert('DOMAIN-SUFFIX,example.com\nPROCESS-NAME,curl\nDOMAIN-SUFFIX,example.com')
        self.assertEqual(result, {'version': 3, 'rules': [
            {'domain_suffix': ['example.com']}, {'process_name': ['curl']}]})
        self.assertEqual(count, 3)
        self.assertEqual(skipped, [])

    def test_comments_cidr_and_process_path(self):
        result, count, skipped = convert('''# comment
IP-CIDR,192.0.2.1/24,no-resolve // comment
IP-CIDR6,2001:db8::1/32
PROCESS-NAME,/Applications/Test.app/
PROCESS-NAME,/usr/bin/curl
DOMAIN,one.test # comment
''')
        self.assertEqual(result['rules'][0], {'ip_cidr': ['192.0.2.0/24', '2001:db8::/32']})
        self.assertEqual(result['rules'][1], {'process_path_regex': [r'^/Applications/Test\.app/']})
        self.assertEqual(result['rules'][2], {'process_path': ['/usr/bin/curl']})
        self.assertEqual(count, 5)
        self.assertFalse(skipped)
        self.assertEqual(clean_line('RULE-SET,https://example.test/a,Proxy'), 'RULE-SET,https://example.test/a,Proxy')

    def test_http_only_rules_reported_without_widening(self):
        result, count, skipped = convert('DOMAIN,a.test\nURL-REGEX,.*secret.*\nUSER-AGENT,Client*')
        self.assertEqual(result['rules'], [{'domain': ['a.test']}])
        self.assertEqual([s['type'] for s in skipped], ['URL-REGEX', 'USER-AGENT'])
        self.assertNotIn('secret', json.dumps(skipped))
        self.assertEqual(count, 3)

    def test_unsupported_changes_fail_before_publication(self):
        for text in ['OTHER,a', 'DOMAIN,', 'IP-CIDR,invalid', 'DOMAIN,a.test,unknown-option', 'USER-AGENT,Only*']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                convert(text)

    def test_atomic_text_and_binary_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'rules.json'
            write_atomic(path, 'text')
            self.assertEqual(path.read_text(), 'text')
            write_atomic(path, b'SRS\0')
            self.assertEqual(path.read_bytes(), b'SRS\0')
            self.assertEqual(list(path.parent.iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
