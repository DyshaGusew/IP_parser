import requests
from bs4 import BeautifulSoup
import base64
from proxy_checking import ProxyChecker
import random
import threading

user_agent = [
    'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9a1) Gecko/20060814 Firefox/51.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/58.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.74 Safari/537.36 Edg/79.0.309.43',
]

COOKIES = {
    'fp': '9684d31202d45a617bf0a07c287ed4e2',
    '_ga': 'GA1.1.2071969646.1707652392',
    '_ga_FS4ESHM7K5': 'GS1.1.1707652392.1.1.1707652452.0.0.0',
}

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Referer': 'https://yandex.ru/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': random.choice(user_agent),
}

PROTOCOLES = {
    '0': 'all',
    '1': 'http',
    '2': 'https',
    '3': 'socks',
    '4': 'socks4',
    '5': 'socks5',
}

ANONYMS = {
    '0': 'all',
    '1': 'level1',
    '2': 'level2',
    '3': 'level3',
}

SORT_PARAMETRS = {
    '1': 'ping',
    '2': 'speed',
    '3': 'uptime',
    '4': 'date',
}


def get_url():
    response = requests.get('http://free-proxy.cz/ru/', headers=HEADERS, cookies=COOKIES)

    soup = BeautifulSoup(response.text, 'lxml')

    countries = soup.find('select', id='frmsearchFilter-country').find_all('option')[1:]

    for c in countries:
        short_name = c.get('value')
        name = c.text.split('(')[0].strip()
        print(short_name, '--', name)
    print("ALL -- Все страны")

    country = input("Выберите страну ")

    for key, value in PROTOCOLES.items():
        print(key, '--', value)
    protocol_type = PROTOCOLES[input("Выберите протокол ")]

    for key, value in ANONYMS.items():
        print(key, '--', value)
    anonyms_type = ANONYMS[input("Выберите тип анонимности ")]

    for key, value in SORT_PARAMETRS.items():
        print(key, '--', value)
    sort_parameter = SORT_PARAMETRS[input("Выберите параметр сортировки ")]

    return f"http://free-proxy.cz/ru/proxylist/country/{country}/{protocol_type}/{sort_parameter}/{anonyms_type}"


def get_count_pages(url):
    try:
        response = requests.get(url, headers=HEADERS, cookies=COOKIES)
        soup = BeautifulSoup(response.text, 'lxml')
    except Exception as ex:
        return 1

    try:
        count_pages = soup.find('div', class_='paginator').find_all('a')[-2].text
    except Exception as ex:
        return 1

    return int(count_pages)


def chekc_ip(tr):
    try:
        ip = tr.find('td').find('script').text
    except Exception as ex:
        print(ex)
        return
    if ip:
        ip = base64.b64decode(ip.split('"')[1]).decode('utf-8')
        port = tr.find('span', class_='fport').text
        try:
            checker = ProxyChecker()
            r = checker.check_proxy(f'{ip}:{port}')
            if r['status']:
                print(f"[+] {ip}:{port}, страна {r['country']}, время ответа {r['time_response']}, анонимность - {r['anonymity']}, тип - {r['type']}")
                with open('ip_list.txt', 'a') as file:
                    file.write(f"{ip}:{port}\n")
            else:
                print(f"IP не валидно")
        except Exception as ex:
            print(f"IP не проверено. Ошибка {ex}")
            return
    else:
        print(f"IP не валидно. Ошибка")
        return


def get_proxyes(url):
    print("Начинаю проверку IP")
    procs = []
    count_pages = get_count_pages(url)
    for i in range(count_pages):
        if count_pages == 1:
            response = requests.get(f"{url}", headers=HEADERS, cookies=COOKIES)
        else:
            response = requests.get(f"{url}/{i}", headers=HEADERS, cookies=COOKIES)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            table_trs = soup.find('table', id='proxy_list').find('tbody').find_all('tr')

            for tr in table_trs:
                t1 = threading.Thread(target=chekc_ip, args=(tr,))
                t1.start()
                procs.append(t1)

            for proc in procs:
                proc.join()

        else:
            print(f'Не получилось, код ошибки {response.status_code}')


def main():
    url = get_url()
    get_proxyes(url)
    print("Все прокси получены")


if __name__ == "__main__":
    main()
