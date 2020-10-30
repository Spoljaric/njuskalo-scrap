import re

from torpy.http.requests import tor_requests_session
from bs4 import BeautifulSoup


def scrap_car_links(array_of_links, car_page_array):
    with tor_requests_session() as s:
        for car in array_of_links:
            print('calling task: ' + car)
            try:
                html = s.get(car)
                soup = BeautifulSoup(html.text, 'html.parser')
                if 'ShieldSquare Captcha' == soup.find('title').string:
                    print('Beep, boop. Site is asking for captcha! Yikes')
                else:
                    div = soup.findAll("h3", {"class": "entity-title"})
                    for h3 in div:
                        current_car = html.url.split('/')[-1]
                        if current_car in h3.next.attrs['href']:
                            car_page_array.append('https://www.njuskalo.hr' + h3.next.attrs['href'])
                    array_of_links.remove(car)
                if len(array_of_links) > 0:  # Njuskalo will not accept immediate calls with same location so create a new request for every car
                    scrap_car_links(array_of_links, car_page_array)
            except:
                scrap_car_links(array_of_links, car_page_array)
    return car_page_array


def scrap_individual_info(array_of_individual_cars, info, tuple_of_infos):
    with tor_requests_session() as s:
        for single_car in array_of_individual_cars:
            try:
                print('calling task: ' + single_car)
                html = s.get(single_car)
                soup = BeautifulSoup(html.text, 'html.parser')
                if 'ShieldSquare Captcha' == soup.find('title').string:
                    print('Beep, boop. Site is asking for captcha! Yikes')
                else:
                    array_of_individual_cars.remove(single_car)
                    div = soup.findAll("dl", {"class": "ClassifiedDetailHighlightedAttributes-listItemInner"})
                    for item in div:
                        title = item.find("dt", {"class": "ClassifiedDetailHighlightedAttributes-label"})
                        val = item.find("dd", {"class": "ClassifiedDetailHighlightedAttributes-text"})
                        tuple_of_infos.append(tuple((title.text, re.sub(r"[\n\t\s]*", "", val.text))))
                if len(array_of_individual_cars) > 0:  # Njuskalo will not accept immediate calls with same location so create a new request for every car
                    scrap_individual_info(array_of_individual_cars, info, tuple_of_infos)
            except:
                scrap_individual_info(array_of_individual_cars, info, tuple_of_infos)
    return tuple_of_infos


if __name__ == '__main__':
    dictionaryOfInterestingCars = {
        'Toyota MR2': 'toyota-mr2',
        'Corvette': 'chevrolet-corvette',
        'Mazda RX-8': 'mazda-rx-8',
        'Ford Mustang': 'ford-mustang',
        'Dodge Charger': 'dodge-charger',
        'Chevrolet Camaro': 'chevrolet-camaro'
    }
    arrayOfLinks = []
    print('Script init')
    url = 'https://www.njuskalo.hr/auti/{car}'
    for key, value in dictionaryOfInterestingCars.items():
        arrayOfLinks.append(url.replace("{car}", value))
    array_of_cars = scrap_car_links(arrayOfLinks, [])
    individual_info = scrap_individual_info(array_of_cars, [], [])
    print(individual_info)
    # TODO: Fire calls to individual pages, array result:
    # 00 = {str} '/auti/toyota-mr2-2.0-gti-16v-reg-11-2020-jako-dobro-stanje-oglas-31503431'
    # 01 = {str} '/auti/toyota-mr2-oglas-29535763'
    # 02 = {str} '/auti/mazda-rx-8-revolution-ls-oglas-32692355'
    # 03 = {str} '/auti/mazda-rx-8-revolution-ls-oglas-32692355'
    # 04 = {str} '/auti/mazda-rx-8-revolution-oglas-28953343'
    # 05 = {str} '/auti/mazda-rx-8-40th-anniversary-motor-10.000-km-oglas-32415476'
    # 06 = {str} '/auti/ford-mustang-shelby-gt-500-oglas-8390922'
    # 07 = {str} '/auti/ford-mustang-coupe-v6-oglas-12759611'
    # 08 = {str} '/auti/ford-mustang-oglas-31669505'
    # 09 = {str} '/auti/ford-mustang-gt-4.0-v6-automatik-oglas-32421761'
    # 10 = {str} '/auti/ford-mustang-2.3-ecoboost-premium-shaker-usa-model-oglas-23375096'
    # 11 = {str} '/auti/ford-mustang-gt-v8-automatik-oglas-32595323'
    # 12 = {str} '/auti/ford-mustang-cabrio-2.3i-premium-oglas-31861944'
    # 13 = {str} '/auti/ford-mustang-2.3-oglas-29173740'
    # TODO: Parse results into json
    # TODO: Send email if new results
    print('done!')
