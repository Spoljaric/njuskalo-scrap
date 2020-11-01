import json
import re

from torpy.http.requests import tor_requests_session
from bs4 import BeautifulSoup


class Car:
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)

    def from_json(self, j):
        self.__dict__ = json.loads(j)


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
                if len(
                        array_of_links) > 0:  # Njuskalo will not accept immediate calls with same location so create a new request for every car
                    scrap_car_links(array_of_links, car_page_array)
            except Exception as e:
                print(e)
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
                    tuple_of_infos.append(tuple(('link', single_car)))
                    div = soup.findAll("dl", {"class": "ClassifiedDetailHighlightedAttributes-listItemInner"})
                    array_of_individual_cars.remove(single_car)
                    car_obj = Car()
                    for item in div:
                        title = item.find("dt", {"class": "ClassifiedDetailHighlightedAttributes-label"})
                        val = item.find("dd", {"class": "ClassifiedDetailHighlightedAttributes-text"})
                        if val is None:
                            val = title.string
                            title = 'Mjenjač'
                            tuple_of_infos.append(tuple((title, val)))
                        else:
                            tuple_of_infos.append(tuple((title.text, re.sub(r"[\n\t\s]*", "", val.text))))
                if len(
                        array_of_individual_cars) > 0:  # Njuskalo will not accept immediate calls with same location so create a new request for every car
                    scrap_individual_info(array_of_individual_cars, info, tuple_of_infos)
            except Exception as e:
                print(e)
                scrap_individual_info(array_of_individual_cars, info, tuple_of_infos)
    return tuple_of_infos


if __name__ == '__main__':
    dictionaryOfInterestingCars = {
        'Toyota MR2': 'toyota-mr2',
        #'Corvette': 'chevrolet-corvette',
        #'Mazda RX-8': 'mazda-rx-8',
        #'Ford Mustang': 'ford-mustang',
        #'Dodge Charger': 'dodge-charger',
        #'Chevrolet Camaro': 'chevrolet-camaro'
    }
    arrayOfLinks = []
    print('Script init')
    url = 'https://www.njuskalo.hr/auti/{car}'
    for key, value in dictionaryOfInterestingCars.items():
        arrayOfLinks.append(url.replace("{car}", value))
    array_of_cars = scrap_car_links(arrayOfLinks, [])
    individual_info = scrap_individual_info(array_of_cars, [], [])
    for result in individual_info:
        print(result)
    # TODO: Parse results into json
    # TODO: Send email if new results
    print('done!')
