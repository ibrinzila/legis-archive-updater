"""Bounded public-source connectivity test; never prints document bodies or cookies."""
import datetime
import hashlib
import json
import re
from html.parser import HTMLParser
from curl_cffi import requests

class Body(HTMLParser):
    def __init__(self):
        super().__init__(); self.depth = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if dict(attrs).get('id') == 'contentdoc': self.depth = 1
        elif self.depth and tag == 'div': self.depth += 1
        if self.depth and tag in {'p','div','br','tr','li','h1','h2','h3','h4','table'}: self.parts.append('\n')
    def handle_endtag(self, tag):
        if self.depth and tag == 'div': self.depth -= 1
        if self.depth and tag in {'p','div','br','tr','li','h1','h2','h3','h4','table'}: self.parts.append('\n')
    def handle_data(self, data):
        if self.depth: self.parts.append(data)

def main():
    result = {'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checks': []}
    try:
        with requests.Session(impersonate='safari') as session:
            session.get('https://www.legis.md/', timeout=20)
            sitemap = session.get('https://www.legis.md/index.php/Sitemap/indexro/2025/2026', timeout=40)
            ids = set(re.findall(r'doc_id=(\d+)', sitemap.text))
            valid = sitemap.status_code == 200 and '<loc>' in sitemap.text and bool(ids)
            result['checks'].append({'kind':'sitemap','http_status':sitemap.status_code,'valid':valid,'ids':len(ids)})
            if valid:
                response = session.get('https://www.legis.md/cautare/showdetails/156660', timeout=40,
                    headers={'Referer':'https://www.legis.md/','X-Requested-With':'XMLHttpRequest'})
                parser = Body(); parser.feed(response.text)
                text = re.sub(r'\n\s*\n+', '\n\n', re.sub(r'[ \t\xa0]+', ' ', ''.join(parser.parts))).strip()
                valid = response.status_code == 200 and bool(text) and 'cf-mitigated' not in response.headers
                result['checks'].append({'kind':'document','id':156660,'http_status':response.status_code,
                    'valid':valid,'characters':len(text),'sha256':hashlib.sha256(text.encode()).hexdigest() if valid else None})
    except Exception as error: result['error_type'] = type(error).__name__
    result['passed'] = len(result['checks']) == 2 and all(check['valid'] for check in result['checks'])
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1

if __name__ == '__main__': raise SystemExit(main())
