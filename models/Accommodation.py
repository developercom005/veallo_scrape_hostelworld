import datetime

class Accommodation:
    name = None
    country = None
    city = None
    coordinate = None
    address = None
    type = None
    description = None
    image_urls = None
    rating_text = None
    rating_score = None
    total_number_of_ratings = None
    facilities = None
    created_date = None
    modified_date = None
    status = None
    scrape_url = None
    main_url = None
    reviews = None
    review_breakdown = None
    website = None


    def __init__(self, name, country, city, address, type,description, image_urls,
                 latitude, longitude, rating_text, rating_score, total_number_of_ratings, facilities, scrape_url, reviews, review_breakdown):
        self.name = name
        self.country = country
        self.city = city
        self.address = address
        self.set_coordinate(lat=latitude,lng=longitude)
        self.type = type
        self.description = description
        self.image_urls = image_urls
        self.rating_text = rating_text
        self.rating_score = rating_score
        self.total_number_of_ratings = total_number_of_ratings
        self.facilities = facilities
        self.status = True
        self.created_date = datetime.datetime.utcnow()
        self.modified_date = datetime.datetime.utcnow()
        self.scrape_url = scrape_url
        self.reviews = reviews
        self.review_breakdown = review_breakdown
        self.website = "https://www.hostelworld.com/"


    def set_coordinate(self,lat,lng):
        if lat is not None and lng is not None:
            self.coordinate = {
                "type": "Point",
                "coordinates": [
                    float(lng),
                    float(lat)
                ]
            }
        else:
            self.coordinate = None

    def set_main_url(self, main_url):
        self.main_url = main_url
