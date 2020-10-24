from multiprocessing.pool import ThreadPool

from torpy.http.requests import tor_requests_session
from bs4 import BeautifulSoup


def fire_threaded_calls(array_of_links):
    car_page_array = []
    with tor_requests_session() as s:
        with ThreadPool(5) as pool:
            tasks = pool.map(s.get, array_of_links)
            pool.close()
            pool.join()
            for task in tasks:
                soup = BeautifulSoup(task.text, 'html.parser')
                if 'ShieldSquare Captcha' == soup.find('title').string:
                    print('Beep, boop. Site is asking for captcha! Yikes')
                else:
                    div = soup.findAll("h3", {"class": "entity-title"})
                    for h3 in div:
                        current_car = task.url.split('/')[-1]
                        if current_car in h3.next.attrs['href']:
                            car_page_array.append(h3.next.attrs['href'])
                    if len(array_of_links) > 0:
                        array_of_links.remove(task.url)
                if len(array_of_links) > 0:
                    print('Not all calls finished successfully. Trying again! Count: ' + str(len(array_of_links)))
                    fire_threaded_calls(array_of_links)
    return car_page_array


if __name__ == '__main__':
    dictionaryOfInterestingCars = {
        'Toyota MR2': 'toyota-mr2',
        'Corvette': 'chevrolet-corvette',
        'Mazda RX-8': 'mazda-rx-8',
        'Ford Mustang': 'ford-mustang',
        'BMW 4 series LCI': 'bmw-serija-4-coupe?yearManufactured%5Bmin%5D=2017'
    }
    arrayOfLinks = []
    print('Script init')
    url = 'https://www.njuskalo.hr/auti/{car}'
    for key, value in dictionaryOfInterestingCars.items():
        arrayOfLinks.append(url.replace("{car}", value))
    arrayOfCars = fire_threaded_calls(arrayOfLinks)
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
