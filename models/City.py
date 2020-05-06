import datetime

class City:
    name = None
    state = None
    country = None
    country_code = None
    continent_name = None
    continent_code = None
    city_geoname_id = None
    country_geoname_id = None
    coordinate = None
    timezone_id = None
    timezone_name = None
    is_safe_to_travel = None
    status = None
    created_date = None
    modified_date = None

    def __init__(self, name, state, country, country_code, continent_code,city_geoname_id, country_geoname_id,
                 latitude, longitude, timezone_id, timezone_name):
        self.name = name
        self.state = state
        self.country = country
        self.country_code = country_code
        self.set_continet_code_and_name(code=continent_code)
        self.city_geoname_id = city_geoname_id
        self.country_geoname_id = country_geoname_id
        self.set_coordinate(lat=latitude, lng=longitude)
        self.timezone_id = timezone_id
        self.timezone_name = timezone_name
        self.is_safe_to_travel = True
        self.status = True
        self.created_date = datetime.datetime.utcnow()
        self.modified_date = datetime.datetime.utcnow()


    def set_continet_code_and_name(self, code):
        if code == "AF":
            self.continent_name = "Africa"
        elif code == "AN":
            self.continent_name = "Antarctica"
        elif code == "AS":
            self.continent_name = "Asia"
        elif code == "EU":
            self.continent_name = "Europe"
        elif code == "NA":
            self.continent_name = "North America"
        elif code == "OC":
            self.continent_name = "Oceania"
        elif code == "SA":
            self.continent_name = "South America"


    def set_coordinate(self,lat,lng):
        self.coordinate = {
                "type": "Point",
                "coordinates": [
                    float(lng),
                    float(lat)
                ]
        }
