import requests
import json
from . import models
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions

def get_request(url, **kwargs):
    api_key = kwargs.get("api_key")
    print("GET from {} ".format(url))
    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

def post_request(url, json_payload, **kwargs):
    try:
        response = requests.post(url, json=json_payload, params=kwargs)
    except:
        print("Something went wrong")
    return response

def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result
        for dealer in dealers:
            dealer_doc = dealer
            dealer_obj = models.CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

def get_dealer_by_id_from_cf(url, id):
    json_result = get_request(url, id=id)
    if json_result:
        dealers = json_result
        dealer_doc = dealers[0] 
        dealer_obj = models.CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
    return dealer_obj

def get_dealer_reviews_by_id_from_cf(url, dealerId):
    results = []
    json_result = get_request(url, id=dealerId)
    if json_result:
        reviews = json_result
        for review in reviews:
            try:
                review_obj = models.DealerReview(
                    name = review["name"], 
                    dealership = review["dealership"], 
                    review = review["review"],
                    purchase=review["purchase"],
                    purchase_date = review["purchase_date"],
                    car_make = review['car_make'],
                    car_model = review['car_model'],
                    car_year= review['car_year'],
                    sentiment= "none"
                )
            except:
                review_obj = models.DealerReview(
                    name = review["name"], 
                    dealership = review["dealership"],
                    review = review["review"], 
                    purchase=review["purchase"],
                    purchase_date = 'none',
                    car_make = 'none',
                    car_model = 'none',
                    car_year= 'none',
                    sentiment= "none"
                )
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)
    return results

def analyze_review_sentiments(text):
    api_key = "jodKrssFMD-TIzy9ZBjreDhAQXunBZ0QADPvvm84keIG"
    url = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/ed95a740-16c3-4916-a3a8-2896f23216f0"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2020-08-01',
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(
        language='en',
        text=text,
        features= Features(sentiment= SentimentOptions())
    ).get_result()
    sentiment_label = response["sentiment"]["document"]["label"]
    sentimentresult = sentiment_label
    return sentimentresult
