import re
import logging
from lib.iscdn import iscdn
from lib.url import parse_host
from lib.Requests import Requests
from lib.waf import WAF_RULE

payload = (
    "/index.php?id=1 AND 1=1 UNION ALL SELECT 1,NULL,'<script>alert(XSS)</script>',table_name FROM information_schema.tables WHERE 2>1--/**/",
    "/../../../etc/passwd", "/.git/", "/phpinfo.php")


def verify(headers, content):
    for i in WAF_RULE:
        name, method, position, regex = i.split('|')
        if method == 'headers':
            if headers.get(position) != None:
                if re.search(regex, str(headers.get(position))) != None:
                    return name
        else:
            if re.search(regex, str(content)):
                return name

    return 'NoWAF'


def checkwaf(url):
    result = 'NoWAF'
    host = parse_host(url)

    if not iscdn(host):
        return 'CDN IP'

    try:
        req = Requests()
        r = req.get(url)
        result = verify(r.headers, r.text)
        if result == 'NoWAF':
            for i in payload:
                r = req.get(url + i)
                result = verify(r.headers, r.text)
                if result != 'NoWAF':
                    return result
        else:
            return result
    except UnboundLocalError:
        pass
    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    result = checkwaf('http://127.0.0.1')
    print(result)
