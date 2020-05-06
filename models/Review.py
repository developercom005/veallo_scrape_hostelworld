import datetime

class Review:
    text = None
    review_country = None

    def __init__(self, text,review_country):
        self.text = text
        self.review_country = review_country
