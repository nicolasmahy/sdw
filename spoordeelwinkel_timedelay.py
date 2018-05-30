#Spoordeelwinkel info scraper
#How does it work?
#1. Open spreadsheet. Check if there are events that need to be removed.
#2. Open spoordeelwinkel.nl. Fetch details from uitje by checking Alle Uitjes page and categories by going through all of them.
#3. Either update entry on sheet or add new one.
#4. Rinse and repeat.
#For questions: gino@oogstonline.nl
import time
import sys
import requests, gspread
from bs4 import BeautifulSoup
#Requirement for Spreadsheets
from oauth2client.service_account import ServiceAccountCredentials
import json
from pprint import pprint
#Easy way to loop through letters
from string import ascii_uppercase

#Setting functions for cell manipulation
def updateCell(header, row, value):
	#print(headerDict)
	#print(headerDict[header] + row)
	worksheet.update_acell(headerDict[header] + row, value)
	
def cellContents(header, row):
	worksheet.acell(headerDict[header] + row).value	


spoordeelwinkelUrl = 'https://www.spoordeelwinkel.nl'

#Connect to Google Sheets
scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials2.json', scope)

try:
	gc = gspread.authorize(credentials)
except BaseException as e:
	print('Error authenticating with Google. ' + str(e))
	sys.exit(0)	
print('Connected to Google Sheets.')
	
try:
	#sh = gc.open('Test sheet')
	
	sh = gc.open_by_key('1mf_huaXHxUpghSJlF37x3t2NpE9v6h7MUx9i8vIXjPQ') # [DEV] NS - Datafeed - DynamicHeader
	#sh = gc.open_by_key('1XoKXMyS7UViD79JCIWMYitq1CTcqZOxEKVUQ0BxlK50') # SDW - Datafeed - DynamicHeader
	
except BaseException as e:
	print('Error opening spreadsheet. ' + str(e))
	sys.exit(0)
print('Opened spreadsheet.')
	
try:	
	worksheet = sh.worksheet("FeedSDW")
except BaseException as e:
	print('Error opening worksheet. ' + str(e))
	sys.exit(0)
print('Opened worksheet.')	

headerRow = 1;

headerDict ={}

print('Fetching column headers')
try:
	for c in ascii_uppercase:
		cell = c + str(headerRow)
		header = worksheet.acell(cell).value
		#print(header)
		if (header == ''):
			break
		headerDict[header] = c	
except BaseException as e:
	print('Error fetching column headers. ' + str(e))
	sys.exit(0)

#Loop through the sheet and fetch information from uitje page

#start at 2, row 1 is headers
i = 2;

#infinite loop
print ('Deleting the rows...')
while(True):
	cell = headerDict['key'] + str(i)
	key = worksheet.acell(cell).value
	if (key == ''):
		break
	worksheet.delete_row(i)

#Get details by looping through category pages
r = requests.get(spoordeelwinkelUrl)
soup = BeautifulSoup(r.text, 'html.parser')
print('Going to loop through categories')
#Retrieve every category and loop through them
swCategories = soup.find_all('a', {'class':'navigation__link navigation__item'})
for swCategory in swCategories:
	swCategoryUrl = swCategory['href']
	r = requests.get(spoordeelwinkelUrl + swCategoryUrl)
	soup = BeautifulSoup(r.text, 'html.parser')
	categoryTitle = soup.find('h1', {'class':'intro__title'}).text
	eventItems = soup.findAll('li', {'class' : ['showcase__item', 'slider__item']})
	#On Alle Uitjes, all uitjes can be found. It is therefore used to populate the spreadsheet.
	if(categoryTitle=='Alle uitjes'):
		count = 1
		interupt = 0
		for eventItem in eventItems:

			#time delay trigger
			if count > 50 and interupt < 1:
				print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
				interupt+=1
				time.sleep(100)

			if count > 100 and interupt < 2:
				print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
				interupt+=1
				time.sleep(100)

			if count > 150 and interupt < 3:
				print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
				interupt+=1
				time.sleep(100)

			if count > 200 and interupt < 4:
				print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
				interupt+=1
				time.sleep(100)			

			if count > 250 and interupt < 5:
				print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
				interupt+=1
				time.sleep(100)		

			if count > 300 and interupt < 6:
				print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
				interupt+=1
				time.sleep(100)		

			if count > 350 and interupt < 7:
				print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
				interupt+=1
				time.sleep(100)		

			if count > 400:
				print(">{} API calls reached in loop... Time delay 100 seconds before EVERY new loop...".format(count))
				interupt+=1
				time.sleep(100)	

			#get clicklink, use to find item on sheet
			clickLink = eventItem.find('a', {'class': 'tile__link'})['href']
			key = clickLink.replace('/uitjes/', '').replace('.html','')
			print('Working on ' + key) 
			
			#Try to find uitje on sheet. If it's not there we will add it to the first available row.
			try:
				row = worksheet.find(key).row
			except BaseException as e:
				print('Cell not found. Will attempt to add it later ' + str(e))
				row = i
				i+=1
				#Add key for new entry
				try:
					updateCell('key', str(row), key)
					#add 1 to time delay trigger
					count += 1
				except BaseException as e:
					print('Error saving key to sheet. ' + str(e))
			
			#Here we add/update all information for an event.
			
			#Event name (header on spreadsheet)
			try:
				header = eventItem.find('span', {'class' : 'tile__title'}).text
				updateCell('header', str(row), header)
				#add 1 to time delay trigger
				count += 1
			except BaseException as e:
				print('Error retrieving title. ' + str(e))
			
			#Text before price, e.g. 'voor' or 'vanaf'
			try:
				pricePrefix = eventItem.find('p', {'class': 'tile__text'}).find('span', {'class':'tile__price-text'}).text
				updateCell('pricePrefix', str(row), pricePrefix)
				#add 1 to time delay trigger
				count += 1
			except BaseException as e:
				print('Error retrieving price prefix. ' + str(e))
			
			#Price (excluding euro sign)
			try:					
				price = eventItem.find('p', {'class': 'tile__text'}).find('span', {'class':'tile__price-amount'}).text
				updateCell('price',str(row), price)
				#add 1 to time delay trigger
				count += 1
			except BaseException as e:
				print('Error retrieving price. ' + str(e))			
			
			#Link (without site)
			try:
				updateCell('clickLink', str(row), clickLink)
				#add 1 to time delay trigger
				count += 1
			except BaseException as e:
				print('Error retrieving clickLink. ' + str(e))					
			
			#fetch low res image urls
			try:
				imageLowRes = eventItem.find('source', {'media' : "(min-width: 0px)"})['srcset']
				updateCell('imageLowRes', str(row), imageLowRes)
				#add 1 to time delay trigger
				count += 1
			
				#replace for other resolutions (more effective, as not all resolutions are in source)

				imageMedRes = imageLowRes.replace('/small/','/medium/')
				updateCell('imageMedRes', str(row), imageMedRes)
				#add 1 to time delay trigger
				count += 1

				imageHighRes = imageLowRes.replace('/small/','/large/')
				updateCell('imageHighRes', str(row),imageHighRes)
				#add 1 to time delay trigger
				count += 1

				
				imageXLRes = imageLowRes.replace('/small/','/xlarge/')
				updateCell('imageXLRes', str(row),imageXLRes)
				#add 1 to time delay trigger
				count += 1
			except BaseException as e:
				print('Error retrieving images. ' + str(e))	
			
			#Category 1 (will always be Alle uitjes)
			try:	
				text = eventItem.find('p', {'class': 'tile__text'}).find(text=True).strip()
				updateCell('category1', str(row), categoryTitle)
				#add 1 to time delay trigger
				count += 1
			except BaseException as e:
					print('Error retrieving text. ' + str(e))
			
			#Text (e.g. Dagretour + Entree)
			try:	
				text = eventItem.find('p', {'class': 'tile__text'}).find(text=True).strip()
				updateCell('text', str(row), text)
				#add 1 to time delay trigger
				count += 1
			except BaseException as e:
					print('Error retrieving text. ' + str(e))		
			
			#Sticker (this one is optional, so first determine if it has been set. Could be 'Nieuw!' or 'Laatste kans!')
			try:
				sticker = eventItem.find('span', {'class': 'tile__sticker'})
				
				if (sticker):
					sticker = sticker.text
					updateCell('sticker', str(row), sticker)
					#add 1 to time delay trigger
					count += 1
			except BaseException as e:
					print('Error retrieving sticker. ' + str(e))
			
			

	#the other category pages are used solely to determine what category an uitje is in. If an uitje is found on that specific category page
	#it will be added to category2 in the sheet and if it is already occupied to category3. If both are occupied, it is not added.
	else: 
		print(categoryTitle)
		for eventItem in eventItems:
			clickLink = eventItem.find('a', {'class': 'tile__link'})['href']
			print(clickLink)
			key = clickLink.replace('/uitjes/', '').replace('.html','')  #the logic here: clickLink appears only once per sheet. Get row from cell match and update the other values.
			try:
				row = worksheet.find(key).row
				val = cellContents('category2', str(row))
				print(val)
				if (val == None):
					try:	
						updateCell('category2', str(row), categoryTitle)
					except BaseException as e:
							print('Error setting category2. ' + str(e))
				else:
					val = cellContents('category3', str(row))
					if (val == ''):
						try:	
							updateCell('category3', str(row), categoryTitle)
						except BaseException as e:
								print('Error setting category3. ' + str(e))			
			except BaseException as e:
				print('Cell not found. ' + str(e))	



#Loop through the sheet and fetch information from uitje page

#start at 2, row 1 is headers
i = 2;
count = 1
interupt = 0

#infinite loop
print ('Going through the sheet to add city, street and coordinates.')
while(True):

	#time delay trigger
	if count > 10 and interupt < 1:
		print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
		interupt+=1
		time.sleep(100)	

	if count > 20 and interupt < 2:
		print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
		interupt+=1
		time.sleep(100)	

	if count > 30 and interupt < 3:
		print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
		interupt+=1
		time.sleep(100)	

	if count > 40 and interupt < 4:
		print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
		interupt+=1
		time.sleep(100)	

	if count > 50 and interupt < 5:
		print(">{} API calls reached in loop... Time delay 100 seconds before new loop...".format(count))
		interupt+=1
		time.sleep(100)	

	if count > 60:
		print(">{} API calls reached in loop... Time delay 100 seconds before EVERY new loop...".format(count))
		interupt+=1
		time.sleep(100)	

	cell = headerDict['key'] + str(i)
	key = worksheet.acell(cell).value
	if (key == ''):
		break
		
	#clickLink	
	clickLink = spoordeelwinkelUrl + '/uitjes/' + key + '.html'
	
	print('Processing ' + clickLink)	
	
	r = requests.get(clickLink)
	
	if (r.status_code==404) :
		#Uitje got removed, so remove row
		print('Link is dead. Going to remove it, but this is slow.')
		worksheet.delete_row(i)
		i-=1
	else :
		try:
			row = worksheet.find(key).row			
			soup = BeautifulSoup(r.text, 'html.parser')
			city = soup.find('span', {'class':'locality'}).text	
			updateCell('city', str(row), city)
			street = soup.find('div', {'class':'street-address'}).text	
			updateCell('street', str(row), street)
			street = street.replace(" ", "+")
			city_lon_lat = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+street+'+'+city+'+Netherlands&key=AIzaSyClpTjstE8qnA5htrqMcZ5qTZ2Wu5Ge7L4')
			location = city_lon_lat.json()

			print('lat: ',location["results"][0]['geometry']['location']['lat'])
			print('lng: ',location["results"][0]['geometry']['location']['lng'])

			lat = location["results"][0]['geometry']['location']['lat']
			updateCell('lat', str(row), lat)
			lon = location["results"][0]['geometry']['location']['lng']		
			updateCell('lon', str(row), lon)	


		except BaseException as e:
			print('Error retrieving location: ' + str(e))
			updateCell('city', str(row), 'Nederland')

		try:
			#get company name
			row = worksheet.find(key).row
			company = soup.find('span', {'class':'org'}).text
			updateCell('company', str(row), company)
			count+=1
			
		except BaseException as e:
			print('Error retrieving company name: ' + str(e))
			updateCell('company', str(row), 'Not found')
			count+=1


	#Increment i to get the new row	
	i+=1
	count+=1
	

						
#Note: these cell updates throw exceptions if they can't be done. We catch the exceptions because they don't need to halt the script.			
#The below code is legacy from a different setup of the script. It's kept for reasons of nostalgia (+ it may come in handy again).				
		
'''
#Fetch page
r = requests.get(spoordeelwinkelUrl)

#Pass to bs4
soup = BeautifulSoup(r.text, 'html.parser')

#fetch all items from homepage

eventItems = soup.findAll('li', {'class' : ['showcase__item', 'slider__item']})

for eventItem in eventItems:
      title = eventItem.find('span', {'class' : 'tile__title'}).text
      text = eventItem.find('p', {'class': 'tile__text'}).find(text=True).strip()
      priceText = eventItem.find('p', {'class': 'tile__text'}).find('span', {'class':'tile__price-text'}).text
      priceAmount = eventItem.find('p', {'class': 'tile__text'}).find('span', {'class':'tile__price-amount'}).text
      clickLink = eventItem.find('a', {'class': 'tile__link'})['href']
      #fetch low res image urls
      showcaseImageLow = eventItem.find('source', {'media' : "(min-width: 0px)"})['srcset']
      #replace for other resolutions (more effective, as not all resolutions are in source)
      showcaseImageMed = showcaseImageLow.replace('/small/','/medium/')
      showcaseImageHigh = showcaseImageLow.replace('/small/','/large/')
      showcaseImageXL = showcaseImageLow.replace('/small/','/xlarge/')
'''	  
'''
				i+=1
				row = i
				###
				try:
					title = eventItem.find('span', {'class' : 'tile__title'}).text
					updateCell('title', str(row), title)
				except BaseException as e:
					print('Error retrieving title. ' + str(e))
				
				try:
					pricePrefix = eventItem.find('p', {'class': 'tile__text'}).find('span', {'class':'tile__price-text'}).text
					updateCell('pricePrefix', str(row), pricePrefix)
				except BaseException as e:
					print('Error retrieving price prefix. ' + str(e))
				
				try:					
					price = eventItem.find('p', {'class': 'tile__text'}).find('span', {'class':'tile__price-amount'}).text
					updateCell('price',str(row), price)
				except BaseException as e:
					print('Error retrieving price. ' + str(e))			
				
				try:
					updateCell('clickLink', str(row), clickLink)
				except BaseException as e:
					print('Error retrieving clickLink. ' + str(e))					
				
				#fetch low res image urls
				try:
					imageLowRes = eventItem.find('source', {'media' : "(min-width: 0px)"})['srcset']
					updateCell('imageLowRes', str(row), imageLowRes)
				
					#replace for other resolutions (more effective, as not all resolutions are in source)

					imageMedRes = imageLowRes.replace('/small/','/medium/')
					updateCell('imageMedRes', str(row), imageMedRes)
	
					imageHighRes = imageLowRes.replace('/small/','/large/')
					updateCell('imageHighRes', str(row),imageHighRes)

					
					imageXLRes = imageLowRes.replace('/small/','/xlarge/')
					updateCell('imageXLRes', str(row),imageXLRes)
				except BaseException as e:
					print('Error retrieving images. ' + str(e))					
				###
'''	