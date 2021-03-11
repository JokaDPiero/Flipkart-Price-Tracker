import time
from selenium.webdriver.common.keys import Keys
from flipkart_config import (
    get_web_driver_options,
    get_firefox_web_driver,
    DIRECTORY,
    BASE_URL
)


from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime

class GenerateReport:
    
    def __init__(self, file_name, filters, base_link, currency, data):
        self.data = data
        self.file_name = file_name
        self.filters = filters
        self.base_link = base_link
        self.currency = currency
        report = {
            'title': self.file_name,
            'date': self.get_now(),
            'best_item': self.get_best_item(),
            'currency': self.currency,
            'filters': self.filters,
            'base_link': self.base_link,
            'products': self.data
        }
        print("Creating report...")
        with open(f'{DIRECTORY}/{file_name}.json', 'w') as f:
            json.dump(report, f)
        print("Done...")

    @staticmethod
    def get_now():
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def get_best_item(self):
        try:
            return sorted(self.data, key=lambda k: k['price'])[0]
        except Exception as e:
            print(e)
            print("Problem with sorting items")
            return None


class FlipkartAPI:
    def __init__(self, search_term, filters, base_url, currency):
        self.base_url = base_url
        self.search_term = search_term
        options = get_web_driver_options()
        self.driver = get_firefox_web_driver(options)
        self.currency = currency
        self.price_filter = f"&p%5B%5D=facets.price_range.from%3D{filters['min']}&p%5B%5D=facets.price_range.to%3D{filters['max']}"

    def run(self):
        print("Starting Script...")
        print(f"Looking for {self.search_term} products...")
        links = self.get_products_links()
        if not links:
            print("Stopped script.")
            return
        print(f"Got {len(links)} links to products...")
        print("Getting info about products...")
        products = self.get_products_info(links)
        print(f"Got info about {len(products)} products...")
        self.driver.quit()
        return products

    def get_products_links(self):
        self.driver.get(self.base_url)
        element = self.driver.find_element_by_class_name("_3704LK")
        element.send_keys(self.search_term)
        element.send_keys(Keys.ENTER)
        time.sleep(2)  # wait to load page
        self.driver.get(f'{self.driver.current_url}{self.price_filter}')
        print(f"Our url: {self.driver.current_url}")
        time.sleep(2)  # wait to load page
        time.sleep(2)  # wait to load page
        result_list = self.driver.find_elements_by_class_name("_13oc-S")
        links = []
        try:
            results = result_list[0].find_elements_by_xpath("//div/div/div[3]/div/div[2]/div/div/div/div/a")
            #/html/body/div/div/div[3]/div/div[2]/div[3]/div/div/div/a
            #/html/body/div/div/div[3]/div/div[2]/div[2]/div/div/div/a
            #/html/body/div/div/div[3]/div/div[2]/div[6]/div/div/div/a
            links = [link.get_attribute('href') for link in results]
            return links
        except Exception as e:
            print("Didn't get any products...")
            print(e)
            return links

    def get_products_info(self, links):
        pids = self.get_pids(links)
        products = []
        for pid in pids:
            product = self.get_single_product_info(pid)
            if product:
                products.append(product)
        return products

    def get_pids(self, links):
        return [self.get_pid(link) for link in links]

    def get_single_product_info(self, pid):
        print(f"Product ID: {pid[pid.find('=')+1:]} - getting data...")
        product_short_url = self.shorten_url(pid)
        self.driver.get(f'{product_short_url}')
        time.sleep(2)
        title = self.get_title()
        seller = self.get_seller()
        price = self.get_price()
        if title and seller and price:
            product_info = {
                'product id': pid[pid.find('=')+1:],
                'url': product_short_url,
                'title': title,
                'seller': seller,
                'price': price
            }
            return product_info
        return None

    def get_title(self):
        try:
            return self.driver.find_element_by_class_name('yhB1nd').text
        except Exception as e:
            print(e)
            print(f"Can't get title of a product - {self.driver.current_url}")
            return None

    def get_seller(self):
        try:
            return self.driver.find_element_by_id('sellerName').text
        except Exception as e:
            print(e)
            print(f"Can't get seller of a product - {self.driver.current_url}")
            return None

    def get_price(self):
        price = None
        try:
            price = self.driver.find_element_by_class_name('_30jeq3 ').text
            price = self.convert_price(price)
        #except NoSuchElementException:
            """
            try:
                availability = self.driver.find_element_by_id('availability').text
                if 'Available' in availability:
                    price = self.driver.find_element_by_class_name('olp-padding-right').text
                    price = price[price.find(self.currency):]
                    price = self.convert_price(price)
            except Exception as e:
                print(e)
                print(f"Can't get price of a product - {self.driver.current_url}")
                return None
            """
        except Exception as e:
            print(e)
            print(f"Can't get price of a product - {self.driver.current_url}")
            return None
        return price

    @staticmethod
    def get_pid(product_link):
        return product_link[product_link.find('/') :product_link.find('&')]

    def shorten_url(self, pid):
        return 'https:' + pid

    def convert_price(self, price):
        price = price.split(self.currency)[1]
        try:
            if len(price)>6 and len(price)>3:
                price = price.split(",")[0] + price.split(",")[1] + price.split(",")[2]
            elif len(price)>3:
                price = price.split(",")[0] + price.split(",")[1]  
            else:
                return float(price)
                

        except:
            Exception()
        return float(price)


    
if __name__ == '__main__':
    
    NAME = input("Enter item to search:")
    CURRENCY = '₹'
    MIN_PRICE = input("Enter item's minimum price:")
    MAX_PRICE =  input("Enter item's maximum price:")
    FILTERS = {
    'min': MIN_PRICE,
    'max': MAX_PRICE
    }
    flp = FlipkartAPI(NAME, FILTERS, BASE_URL, CURRENCY)
    data=flp.run()
    GenerateReport(NAME, FILTERS, BASE_URL, CURRENCY, data)