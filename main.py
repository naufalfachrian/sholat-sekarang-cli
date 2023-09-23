import requests
import inquirer
from lxml import html
from datetime import datetime


def main():
    cookies = {
        'PHPSESSID': fetch_home().cookies['PHPSESSID']
    }
    home = fetch_home(cookies=cookies)
    home_tree = html.document_fromstring(home.content.decode(encoding='iso-8859-1'))
    province_list = home_tree.xpath('//*[@id="search_prov"]/option')
    province_id = select_province_id(province_list)
    city_list = read_city_list(fetch_city(province_id, cookies=cookies))
    city_id = select_city_id(city_list)
    prayer_time = fetch_today_prayer_time(province_id, city_id, cookies=cookies)
    print_prayer_time(prayer_time)


def fetch_home(cookies= None) -> requests.Response:
    return requests.get("https://bimasislam.kemenag.go.id/jadwalshalat", headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    }, cookies=cookies)


def select_province_id(province_list: list) -> str|None:
    questions = [
        inquirer.List('prov',
                      message="Pilih Provinsi",
                      choices=[province.text for province in province_list],
                      carousel=True
                      ),
    ]
    answers = inquirer.prompt(questions)
    for province in province_list:
        if province.text == answers['prov']:
            return province.attrib['value']
    return None


def fetch_city(province_id: str, cookies=None) -> requests.Response:
    return requests.post("https://bimasislam.kemenag.go.id/ajax/getKabkoshalat", headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    }, cookies=cookies, data={
        'x': province_id
    })


def read_city_list(from_response: requests.Response) -> list:
    city_list_html = from_response.content\
        .decode(encoding='iso-8859-1')
    return html.document_fromstring(city_list_html)\
        .xpath('//*/option')


def select_city_id(city_list: list) -> str|None:
    questions = [
        inquirer.List('city',
                      message="Pilih Kota/Kabupaten",
                      choices=[city.text for city in city_list],
                      carousel=True
                      ),
    ]
    answers = inquirer.prompt(questions)
    for city in city_list:
        if city.text == answers['city']:
            return city.attrib['value']
    return None


def fetch_today_prayer_time(province_id: str, city_id: str, cookies=None) -> requests.Response:
    current_time = datetime.now()
    current_month = current_time.month
    current_year = current_time.year
    prayer_time_json = fetch_prayer_time(province_id, city_id, current_month, current_year, cookies=cookies)\
        .json()
    return {
        'province_name': prayer_time_json['prov'],
        'city_name': prayer_time_json['kabko'],
        'data': prayer_time_json['data'][current_time.strftime("%Y-%m-%d")]
    }


def fetch_prayer_time(province_id: str, city_id: str, month: int, year: int, cookies=None) -> requests.Response:
    return requests.post("https://bimasislam.kemenag.go.id/ajax/getShalatbln", headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    }, cookies=cookies, data={
        'x': province_id,
        'y': city_id,
        'bln': month,
        'thn': year
    })


def print_prayer_time(prayer_time: dict):
    print(f"Jadwal Shalat untuk wilayah {prayer_time['province_name']} - {prayer_time['city_name']} dan sekitarnya")
    print(f"Tanggal : {prayer_time['data']['tanggal']}")
    print(f"Imsak   : {prayer_time['data']['imsak']}")
    print(f"Subuh   : {prayer_time['data']['subuh']}")
    print(f"Terbit  : {prayer_time['data']['terbit']}")
    print(f"Dhuha   : {prayer_time['data']['dhuha']}")
    print(f"Dzuhur  : {prayer_time['data']['dzuhur']}")
    print(f"Ashar   : {prayer_time['data']['ashar']}")
    print(f"Maghrib : {prayer_time['data']['maghrib']}")
    print(f"Isya    : {prayer_time['data']['isya']}")
    print(f"")
    print(f"Jadwal Shalat diambil dari https://bimasislam.kemenag.go.id/jadwalshalat")
    print(f"Waktu tertera adalah waktu setempat")


if __name__ == "__main__":
    main()
