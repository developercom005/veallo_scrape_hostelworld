import time
from selenium import webdriver
from models.Accommodation import Accommodation
from db.MongoDBService import MongoDBService
from models.Review import Review
from models.ReviewBreakdown import ReviewBreakdown
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import geocoder
import smtplib
from datetime import datetime

db_service = MongoDBService(url = ['mongodb://chandan005:pumpkiN009!@43.240.42.5:1025'])

def send_email(email_text,to):
    try:
        gmail_user = "veallo009"
        gmail_pwd = "Kite009!"
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_pwd)

        msg = MIMEMultipart()
        msg["From"] = gmail_user
        if len(to) == 1:
            msg["To"] = to[0]
        else:
            msg["To"] = ", ".join(to)
        msg["Subject"] = "Hostelworld.com Scrape"
        msg.attach(MIMEText(email_text, 'plain'))
        text = msg.as_string()
        server.sendmail(gmail_user, to, text)
        server.send_message(msg)
    except Exception as e:
        print(e)
        print("Exception sending email")

def prepare_driver():

    #Mac
    # opts = webdriver.ChromeOptions()
    # opts.headless = True
    # driver = webdriver.Chrome('/Users/chandansingh/Documents/travel/scrape/hostelworld_scrape/chromedriver', options=opts)

    #Linux
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=chrome_options)

    return driver

def get_countries_of_continent(driver,continent_name,domain):
    if driver is None:
        driver = prepare_driver()
    driver.get(domain)
    time.sleep(3)
    all_continents = driver.find_elements_by_class_name("accordion-navigation")
    for a_c in all_continents:
        try:
            a_c.find_element_by_class_name("fa-plus-circle").click()
        except:
            a_c.find_element_by_class_name("fa-minus-circle").click()
    countries_ul = driver.find_element_by_xpath("//*[@id='"+continent_name+"']/ul")
    countries_list = countries_ul.find_elements_by_tag_name("li")
    countries_dict_list = []
    for country in countries_list:
        country_dict = dict()
        country_dict["name"] = country.text
        country_dict["url"] = country.find_element_by_tag_name("a").get_attribute('href')
        countries_dict_list.append(country_dict)
    return countries_dict_list

def get_cities_from_url(driver,country,country_url):
    c_sets = set()
    if driver is None:
        driver = prepare_driver()
    time.sleep(3)
    class_locations = driver.find_element_by_class_name("otherlocations")
    other_locations_ul = class_locations.find_element_by_tag_name("ul")
    list_locations = other_locations_ul.find_elements_by_tag_name("li")
    for l in list_locations:
        c_sets.add(l.text)
    return c_sets

def construct_url(city,country,page):
    url = "https://www.hostelworld.com/findabed.php/ChosenCity."+city+"/ChosenCountry."+country+"?page="+str(page)
    return url

def scrape_all_cities():
    driver = prepare_driver()
    continents = ["asia", "north_america", "south_america", "oceania", "africa"]

    for cont in continents:
        print(cont)
        domain = 'https://www.hostelworld.com/hostels#' + cont
        print(domain)
        country_dict_list = get_countries_of_continent(driver=driver,continent_name=cont,domain=domain)
        country_set = set()
        for c_d in country_dict_list:
            print(c_d["name"])
            country_set.add(c_d["name"])
        db_countries = set(db_service.get_country_by_distinct_fields())
        country_set = country_set.difference(db_countries)

        for country in country_set:
            country_name = country
            print("Scraping for ", country_name)
            country_url = "https://www.hostelworld.com/hostels/" + country_name
            driver.get(country_url)
            c_sets = get_cities_from_url(driver=driver, country=country_name, country_url=country_url)
            cities_list = list()
            for city in c_sets:
                country_url = "https://www.hostelworld.com/hostels/" + country_name
                city_url = "https://www.hostelworld.com/findabed.php/ChosenCity." + city + "/ChosenCountry." + country_name
                city_data = {
                    "city": city,
                    "country": country_name,
                    "country_url": country_url,
                    "created_date": datetime.utcnow(),
                    "modified_date": datetime.utcnow(),
                    "city_url": city_url,
                    "scrapped": False,
                    "count": 0
                }
                cities_list.append(city_data)
            db_service.insert_cities(data=cities_list)

def get_accommodations_list(driver,url,city,country):
    if driver is None:
        driver = prepare_driver()
    driver.get(url)
    time.sleep(3)

    email_text = {}
    look_for_next_page = True
    listing_urls = list()
    i = 0
    page_count = 1
    total_inserted = 0

    total_listing = driver.find_element_by_class_name("fabfooter").find_element_by_class_name("display-for-dynamic").text
    print(total_listing, "here")
    total_listing = [int(s) for s in total_listing.split() if s.isdigit()]

    if len(total_listing) > 0:
        total_listing = total_listing[0]
    print("total_listing - ", total_listing)

    while look_for_next_page:
        print("total listing for " + city + ", ", total_listing)

        if i == total_listing:
            print()
            print("Breaking here, total_listing - for " + city + ", ", total_listing)
            print("Page Count - ", page_count)
            print("Breaking here, total scraped fo " + city + ", ", total_inserted)
            break

        all_listing = driver.find_element_by_id("fabResultsContainer")
        for listing in all_listing.find_elements_by_class_name("fabresult"):
            listing_url = listing.get_attribute('url')
            listing_urls.append(listing_url)

        if len(listing_urls) < 30:
            print("Length of titles less than 30", len(listing_urls))
            look_for_next_page = False
        else:
            look_for_next_page = True
            page_count += 1

        for l_url in range(0, len(listing_urls)):
            i += 1
            if l_url == len(listing_urls):
                print("Breaking when length of url == len of accommodations links")
                break
            acc = scrape_listing_detail(driver=driver, listing_url=listing_urls[l_url], city=city,
                                            country=country)
            acc.set_main_url(main_url=str(listing_urls[l_url]))
            status = db_service.insert_accommodation(acc.__dict__)
            if status:
                print(i, " accommodation data scraped and inserted in database")
                total_inserted += 1

        listing_urls = list()

        if look_for_next_page:
            next_page_url = construct_url(city=city, country=country, page=2)
            if driver == None:
                driver = prepare_driver()
            driver.get(next_page_url)
            time.sleep(8)

    email_text["city"] = city
    email_text["country"] = country
    email_text["total_inserted"] = total_inserted

    return email_text

def scrape_listing_detail(driver,listing_url,city,country):
    if driver is None:
        driver = prepare_driver()
    driver.get(listing_url)
    time.sleep(3)

    acc_type = "Hostel"
    try:
        name = driver.find_element_by_xpath("//*[@id='pagebody']/div[1]/div[1]/div[2]/div[8]/section[1]/div/div[2]/div/div/h1").text.strip()
    except:
        print("Name is None.")
        name = ""
    try:
        address = driver.find_element_by_xpath("//*[@id='pagebody']/div[1]/div[1]/div[2]/div[8]/section[1]/div/div[2]/div/div/div/span/a[1]").text.strip()
        address = address + ", " + city + ", " + country
    except:
        print("Address is None.")
        address = ""
    try:
        rating_score = driver.find_element_by_xpath("//*[@id='pagebody']/div[1]/div[1]/div[2]/div[8]/section[4]/div/section[1]/div/div[1]/div[1]").text.strip()
        try:
            rating_score = float(rating_score)
        except:
            rating_score = None
    except:
        print("Rating Score is None.")
        rating_score = 0
    try:
        rating_text = driver.find_element_by_xpath("//*[@id='pagebody']/div[1]/div[1]/div[2]/div[8]/section[4]/div/section[1]/div/div[1]/div[2]/p").text.strip()
    except:
        print("Rating Text is None.")
        rating_text = ""
    try:
        total_number_of_ratings = driver.find_element_by_xpath("//*[@id='pagebody']/div[1]/div[1]/div[2]/div[8]/section[4]/div/section[1]/div/div[1]/div[2]/a/span").text.strip().replace('Total Reviews', '').strip()
        try:
            total_number_of_ratings = int(total_number_of_ratings)
        except:
            total_number_of_ratings = 0
    except:
        print("Total ratings is None.")
        total_number_of_ratings = 0

    try:
        description = driver.find_element_by_xpath("//*[@id='pagebody']/div[1]/div[1]/div[2]/div[8]/section[4]/div/section[2]/div/div/div").text
    except:
        print("Description is None.")
        description = ""

    try:
        image_urls_class = driver.find_element_by_name("ms-gallery").find_element_by_class_name("row").find_element_by_class_name("small-12").find_element_by_class_name("gallery")
        image_urls = []
        for image in image_urls_class.find_elements_by_class_name("gallery-item"):
            img = image.find_element_by_tag_name("img").get_attribute("src")
            image_urls.append(img)
        print(len(image_urls), "Image urls")
    except:
        print("Image urls is None.")
        image_urls = []

    try:
        reviews = []
        reviews_class = driver.find_element_by_name("ms-latest-reviews")
        reviews_ul = reviews_class.find_element_by_tag_name("ul")
        reviews_li = reviews_ul.find_elements_by_tag_name("li")

        for review in reviews_li:
            r = review.find_element_by_class_name("property-review").find_element_by_class_name("review-info")
            r_country = r.find_element_by_class_name('details-bottom').text.strip()
            r_text = r.find_element_by_class_name("notes").find_element_by_class_name("truncate-container").find_element_by_class_name("text").text.strip()
            rev = Review(text=r_text, review_country=r_country)
            reviews.append(rev.__dict__)
    except:
        print("Reviews is None.")
        reviews = []

    try:
        reviews_breakdown_list = []
        reviews_class = driver.find_element_by_name("ms-reviews-and-ratings")
        reviews_breakdown_ul = reviews_class.find_element_by_tag_name("ul")
        reviews_breakdown_li = reviews_breakdown_ul.find_elements_by_tag_name("li")
        for breakdown in reviews_breakdown_li:
            b_text = breakdown.find_element_by_class_name('rating-label').text.strip()
            b_value = breakdown.find_element_by_class_name('rating-label').find_element_by_class_name('pull-right').text.strip()
            try:
                b_value = int(b_value)
            except:
                b_value = None
            rev_b = ReviewBreakdown(type=b_text,value=b_value)
            reviews_breakdown_list.append(rev_b.__dict__)
    except:
        print("Reviews Breakdown missing")


    try:
        facilities = []
        facilities_class = driver.find_element_by_name("ms-facilities").find_element_by_class_name("row").find_element_by_class_name("small-12").find_element_by_class_name("pb-3")
        groups = facilities_class.find_elements_by_class_name("facility-group")

        for group in groups:
            facilities_ul = group.find_element_by_tag_name("ul")
            facilities_li = facilities_ul.find_elements_by_tag_name("li")
            for f in facilities_li:
                facilities.append(str(f.text.strip()))
    except:
        print("Facilities is None.")
        facilities = []

    g = geocoder.geonames(city+", " + country, key='developer005')
    if g.ok is True:
        latitude = g.lat
        longitude = g.lng
    else:
        latitude = None
        longitude = None

    acc = Accommodation(name=str(name), country=str(country), city=str(city),
                        address=str(address), type=str(acc_type),
                        description=str(description), image_urls=image_urls,
                        latitude=latitude, longitude=longitude, rating_text=str(rating_text),
                        rating_score=rating_score, total_number_of_ratings=total_number_of_ratings,
                        facilities=facilities,
                        scrape_url=str(listing_url), reviews=reviews, review_breakdown=reviews_breakdown_list)

    return acc

def scrape():
    try:
        driver = prepare_driver()
        cities = db_service.get_city_left_to_scrape()
        for c in cities:
            print("Scraping for ", c["city"])
            total_inserted_dict = get_accommodations_list(driver=driver, url=c["city_url"], city=c["city"],country=c["country"])

            db_service.update_cities(city=c["city"], country=c["country"], scrapped_value=True,count=total_inserted_dict["total_inserted"])

            email_text = "The scrape for " + total_inserted_dict["city"] + ", " + total_inserted_dict["country"] + " has ended gracefully and " + str(total_inserted_dict["total_inserted"]) + " inserted in database for hostelworld."
            to_addrs = ["phoenix.com005@gmail.com"]
            send_email(email_text=email_text, to=to_addrs)

        driver.quit()
    except Exception as e:
        to_addrs = ["phoenix.com005@gmail.com"]
        send_email(email_text=str(e) + " in hostel world", to=to_addrs)


