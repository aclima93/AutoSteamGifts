#!/usr/bin/python3
__author__ = 'jota'

from io import BytesIO
import gzip
import urllib.request
import urllib.parse
import sys
import re

MAIN_URL = 'http://www.steamgifts.com'
PAGING_URL = 'http://www.steamgifts.com/giveaways/search?page='
USER_AGENT = 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
GLOBAL_HEADERS = {'User-Agent': USER_AGENT, 'Accept': 'application/json, text/javascript, */*; q=0.01',
                  'Accept-encoding': 'gzip, deflate', 'Connection': 'keep-alive',
                  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
MAIN_REGEX = 'href="\/giveaway\/(?P<Code>[a-zA-Z0-9]*?)\/[^\/]*?"'
XSRF_REGEX = 'name="xsrf_token" value="(?P<XSRF>[0-9a-zA-Z]*?)"'


def getWebPage(url, headers, cookies, post_data=None):
    try:
        if post_data:
            params = urllib.parse.urlencode(post_data)
            params = params.encode('utf-8')
            request = urllib.request.Request(url, data=params, headers=headers)
        else:
            print('Fetching ' + url)
            request = urllib.request.Request(url, None, headers)

        request.add_header('Cookie', cookies)

        if post_data:
            response = urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(request)
        else:
            response = urllib.request.urlopen(request)

        if response.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            r = f.read()
        else:
            r = response.read()

        return r

    except Exception as e:
        print("Error processing webpage: " + str(e))
        return None


# https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
def nodup(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def main():
    try:
        if len(sys.argv) < 1:
            print('./steamgifts.py <Cookie>')
            print(
                    'Please insert your cookie. Press CTRL+SHIFT+J on the website (CTRL+SHIFT+K on Firefox) and type document.cookie. Then paste the whole string as an argument.')
            return

        regex = re.compile(MAIN_REGEX)
        xsrf_regex = re.compile(XSRF_REGEX)

        for i in range(1, 10):
            home_page = getWebPage(PAGING_URL + str(i), GLOBAL_HEADERS, sys.argv[1])

            if home_page is None:
                print('An error occurred while fetching results (probably expired cookie?). Terminating...')
                return

            xsrf_token = xsrf_regex.findall(str(home_page))[0]
            games_list = regex.findall(str(home_page))
            games_list = nodup(games_list)
            print(games_list)
            for g in games_list:

                post_data = {'xsrf_token': xsrf_token, 'do': 'entry_insert', 'code': g}
                response_data = getWebPage(MAIN_URL + '/ajax.php', GLOBAL_HEADERS, sys.argv[1], post_data)
                print(response_data)

                if "\"points\":\"0\"" in response_data.decode('ascii'):
                    print("0 points left, exiting.")
                    return

    except KeyboardInterrupt:
        print("Interrupted.")


if __name__ == '__main__':
    main()
