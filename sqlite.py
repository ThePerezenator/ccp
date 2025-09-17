import sqlite3
import os
import requests
from sqlite3 import Error
from webserver import path

rapidapi = False

def create_table_recipies():
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute(f'CREATE TABLE IF NOT EXISTS recipies(id Text, name Text, description Text, instructions Text)')
		print(f"database CREATED")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def open(recipie):
	try:
		recipie = str(recipie)[2:-2]
		print(f"opening {recipie}")
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute(f"SELECT * from recipies WHERE name = '{recipie}'")
		return(c.fetchone())
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def add_song(setlist, song, artist, release):
	try:
		if rapidapi and not artist or not release:       
			try:
				#spotify api from rapid api  
				url = "https://spotify23.p.rapidapi.com/search/"                
				querystring = {"q":song,"type":"tracks","offset":"0","limit":"3","numberOfTopResults":"3"}
				headers = {
					"X-RapidAPI-Key": "3f5bdb3f62msh26a0c2dedd6d13ap13a44cjsn52f0c4e75538",
					"X-RapidAPI-Host": "spotify23.p.rapidapi.com"
				}
				r = requests.request("GET", url, headers=headers, params=querystring)
				data = r.json()
				id = data['tracks']['items'][0]['data']['id']
				print(id)

				#iterates and prints top 3 results for the queried song
				i = 0
				while i < len(data['tracks']['items']):
					print(f"RETURN #{i} {data['tracks']['items'][i]['data']['name']}")
					i += 1

				url = "https://spotify23.p.rapidapi.com/tracks/"
				querystring = {"ids":id}
				r = requests.request("GET", url, headers=headers, params=querystring)
				data = r.json()
			
				if artist == "":
					artist = data['tracks'][0]['artists'][0]['name']
				if release == "":
					release = data['tracks'][0]['album']['release_date']
				print(artist)
				print(release)
		
			except:
				artist = ""
				release = ""
				print("error fetching from spotify api")		
		
		else:
			print("artist and release from text field")

		os.chdir(f"{path}/Setlists")
		conn = sqlite3.connect(f"{path}/Setlists/{setlist}")
		print(f"Setlist: {setlist} Song: {song}")
		c = conn.cursor()
		c.execute(f"INSERT INTO {setlist} (song, artist, release) VALUES (?, ?, ?)", 
	    (song, artist, release))
		conn.commit()
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()
		
def remove_song(setlist, song):
	try:
		os.chdir(f"{path}/Setlists")
		conn = sqlite3.connect(f"{path}/Setlists/{setlist}")
		print(f"Setlist: {setlist} Song: {song}")
		c = conn.cursor()
		c.execute(f"DELETE from {setlist} WHERE song = '{song}'")
		conn.commit()
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()




create_table_recipies()