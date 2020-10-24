from multiprocessing.pool import ThreadPool

from torpy.http.requests import tor_requests_session
from bs4 import BeautifulSoup


def fire_threaded_calls(array_of_links):
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
                    # TODO: Parse HTML
                    print(task.text)
                    if len(array_of_links) > 0:
                        array_of_links.remove(task.url)
                if len(array_of_links) > 0:
                    print('Not all calls finished successfully. Trying again! Count: ' + str(len(array_of_links)))
                    fire_threaded_calls(array_of_links)


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
    fire_threaded_calls(arrayOfLinks)
    # TODO: Parse results into json
    # TODO: Send email if new results
    print('done!')
