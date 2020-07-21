import json
import requests
import time
import csv
import pandas as pd

def API_Call(queryStr, APIKEY="YOUR_API_KEY", url ="https://maps.googleapis.com/maps/api/place/textsearch/json?"):
	'''return data from a Google Maps Places API call
	inputs: queryStr: a search string
	Outputs: a json object containing up to 60 results
	'''
	#Build initial url
	url_call = url + "query="
	for word in queryStr.split():
		url_call += word
		url_call += "+"

	url_call += "&radius=10000"
	url_call += "&key=" + APIKEY
	#make request
	req = requests.get(url_call)
	data = req.text
	dataJSON = json.loads(data)
	#parse reuslts
	results = dataJSON['results']

	#Get next pages until all results are found
	while 'next_page_token' in dataJSON.keys():
		#build url
		next_page_token = dataJSON['next_page_token']
		url_call = url + "pagetoken=" + next_page_token
		url_call += "&key=" + APIKEY
		#wait to allow for next page token to become valid
		time.sleep(2)
		#make request
		req = requests.get(url_call)
		data = req.text
		dataJSON = json.loads(data)
		#append data array
		for item in dataJSON['results']:
			results.append(item)
	time.sleep(2)
	return results

def extractData(results, searchType):
	'''Flatten JSON data from the Maps API into a list of lists'''
	extractedArray = []
	for item in results:
		name = item["name"]
		locationType = searchType
		id_ = item["place_id"]
		lat = item["geometry"]["location"]["lat"]
		lng_ = item["geometry"]["location"]["lng"]
		types = item["types"]

		extractedArray.append([name, locationType, id_, lat, lng_, types])

	return extractedArray


#Make search strings or queries
queries = []
items_to_query = ["supermarket in ", "bank in ", "hospital in ", "school in "]
ato = pd.read_csv("ATOdata.csv")

#make one per postcode and service type
for row in ato.iterrows():
	if row[1]["state"] == "VIC":
		for queryHeader in items_to_query:
			query = queryHeader + str(row[1]["postcode"])
			queryType = queryHeader.split()[0]
			queries.append([query, queryType])

print("number of queries: {0}".format(len(queries)))

#run each query through the API
cnt = 0
for query in queries:
	try:
		queryStr = query[0]
		queryType = query[1]
		print("request count: {0}, Query: {1}".format(cnt, queryStr))

		results = API_Call(queryStr)
		results_formatted = extractData(results, queryType)

		#Save results as they are produced
		if cnt == 0:
			with open("MapsData.csv", "w") as f:
				writer = csv.writer(f)
				for row in results_formatted:
					writer.writerow(row)
		else:
			with open("MapsData.csv", "a") as f:
				writer = csv.writer(f)
				for row in results_formatted:
					writer.writerow(row)

		cnt+=1
	except:
		print("ERROR ON: request count: {0}, Query: {1}".format(cnt, queryStr))
		cnt += 1
