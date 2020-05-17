from services import hostelworld_services
from db.MongoDBService import MongoDBService
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

db_service = MongoDBService(url = ['mongodb://chandan005:pumpkiN009!@43.240.42.5:1025'])

# db_service = MongoDBService(url = ['127.0.0.1:27017'])

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
        msg["Subject"] = "Booking.com Scrape"
        msg.attach(MIMEText(email_text, 'plain'))
        text = msg.as_string()
        server.sendmail(gmail_user, to, text)
        server.send_message(msg)
    except Exception as e:
        print(e)
        print("Exception sending email")


def get_domain_names():
    continents = ["europe", "asia", "north_america", "south_america", "oceania", "africa"]
    domain = 'https://www.hostelworld.com/hostels#'
    domain_names = []

    for c in continents:
        domain_names.append(domain+c)

    return domain_names



if __name__ == '__main__':
    try:
        for d in get_domain_names():
            hostelworld_services.scrape(domain=d)
        send_email(email_text="Scrape Job Finished", to=["phoenix.com005@gmail.com"])
    except Exception as e:
        print(e)
        print("Exception while scraping")
        to_addrs = ["phoenix.com005@gmail.com"]
        send_email(email_text=str(e) + " in hostel world", to=to_addrs)

