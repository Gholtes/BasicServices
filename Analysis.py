import pandas as pd
import numpy as np
from math import sin, cos, sqrt, atan2, radians

def DistanceScalar(lat1, lon1, lat2, lon2):
	'''Uses Haversine formula
	All inputs are scalars
	'''
	#approx radius of earth in km
	R = 6373.0

	lat1 = radians(lat1)
	lon1 = radians(lon1)
	lat2 = radians(lat2)
	lon2 = radians(lon2)

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = (sin(dlat / 2)**2) + cos(lat1) * cos(lat2) * (sin(dlon/2)**2)
	c = 2 * atan2(np.sqrt(a), sqrt(1 - a))

	distance = R * c
	# distance = sqrt((lat1-lat2)**2 + (lon1-lon2)**2)
	return distance

def Distance(lat1, lon1, lat2, lon2):
	'''Uses Haversine formula
	lat1, lon1 are presumed to be pandas DF cols, lat2, lon2 are presumed to be float
	'''
	#approx radius of earth in km
	R = 6373.0

	lat1 = np.radians(lat1.astype(float))
	lon1 = np.radians(lon1.astype(float))
	lat2 = radians(lat2)
	lon2 = radians(lon2)

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = np.power(np.sin(np.divide(dlat, 2)), 2) + np.cos(lat1) * cos(lat2) * np.power(np.sin(np.divide(dlon, 2)), 2)
	c = np.multiply(2, np.arctan2(np.sqrt(a), np.sqrt(1 - a)))

	distance = R * c
	return distance


#Open datafiles
SA4centers = pd.read_csv("SA4centres.csv")
MapsData = pd.read_csv("MapsDataUnique.csv")

#exclude non verified
MapsData = MapsData[MapsData["verified"]==1]

postcodeMeta = pd.read_csv("australian_postcodes.csv")
postcodeMeta = postcodeMeta[["postcode", "locality", "long", "lat", "sa3name", "sa4name"]]
postcodeMeta = postcodeMeta.drop_duplicates(subset=['postcode'])
ATO = pd.read_csv("ATOdata.csv")

#make list of postcodes in vic to use for analysis
DataMaster = ATO[ATO['state']=="VIC"]

#merge in postcode data (left merge)
DataMaster = DataMaster.merge(postcodeMeta, left_on = "postcode", right_on = "postcode", how = 'left')

#define radii that we want to use in this analysis
Radii = [0.5,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,20,22,24,26,28,30,32,34,36]

for X in Radii:
	#for each postcode, get the counts of each basic service within X km
	cnt = 1

	#init cols
	DataMaster["supermarketCount"] = 0
	DataMaster["bankCount"] = 0
	DataMaster["schoolCount"] = 0
	DataMaster["healthCount"] = 0
	DataMaster["distfromcenter"] = 0.0
	DataMaster["urban"] = 0.0 #within 45.0km of melbourne as defined by the city limits graph

	#Find all services within X km of each postcode in DataMaster
	for row in DataMaster.iterrows():
		if cnt<10000:
			i = int(row[0])

			lat = row[1]['lat']
			lon = row[1]['long']
			#Get distance from each service to the postcode centroid
			MapsData['Dist'] = Distance(MapsData["lat"], MapsData["long"], lat, lon) 
			#Count those services within X km
			DataMaster.at[i, "supermarketCount"] = MapsData[(MapsData['Dist'] <= X) & (MapsData['type'] == 'supermarket')].count()['name']
			DataMaster.at[i, "bankCount"] = MapsData[(MapsData['Dist'] <= X) & (MapsData['type'] == 'bank')].count()['name']
			DataMaster.at[i, "schoolCount"] = MapsData[(MapsData['Dist'] <= X) & (MapsData['type'] == 'school')].count()['name']
			DataMaster.at[i, "healthCount"] = MapsData[(MapsData['Dist'] <= X) & (MapsData['type'] == 'hospital')].count()['name']
			#make additional control vars
			try:
				#get dist to nearest regional center
				SA4lat = float(SA4centers[SA4centers['sa4'] == row[1]['sa4name']]["lat"])
				SA4long = float(SA4centers[SA4centers['sa4'] == row[1]['sa4name']]["long"])
				dist = DistanceScalar(SA4lat, SA4long, float(lat), float(lon)) 
				DataMaster.at[i, "distfromcenter"] = dist
				#get dist to melbourne to define urban / regional var
				SA4lat = float(SA4centers[SA4centers['sa4'] == "Melbourne - Inner"]["lat"])
				SA4long = float(SA4centers[SA4centers['sa4'] == "Melbourne - Inner"]["long"])
				dist = DistanceScalar(SA4lat, SA4long, float(lat), float(lon)) 
				DataMaster.at[i, "urban"] = (dist <= 45.0)*1.0
			except:
				print("dist error on {0}".format(i))
				pass
		cnt+=1
	
	#Save this dataset
	DataMaster.to_csv("{0}kmMasterDataset.csv".format(X))