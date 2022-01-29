
########################################

## Complete Update of Database Tables ##

########################################


## Imports ##

from bs4 import BeautifulSoup
import requests
import pyodbc as pyo
import time
from datetime import datetime

## Functions ##

def find_cards():

    t0 = time.time() # Find time when database update begins
    errors = [] # Keeps track of errors

    #print("Finding cards...")
    
    #print("Preparing to update card database...")
    #print("Establishing connection to database...")
    conn = pyo.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\james\Desktop\eBay Scraper\MTGCards.accdb;') # Connect to MS Access database
    cursor = conn.cursor() # Create a link to interact with database

    sql = "SELECT * FROM Sets" # Query to find entire database
    cursor.execute(sql) # Send query to database

    for record in cursor.fetchall(): # Iterate through database
    
        start = time.time() # Time to calculate passed time
                    
        try:
            res = requests.get(record[2]) # Downloads the page for processing
            res.raise_for_status() # Raises an exception error if there's an error downloading the website
        except requests.exceptions.HTTPError as e: # Safeguard error
            errors.append(("SET_ERROR", str(e), record[0])) # Create error warning
        #except ssl.SSLEOFError as e: # Safeguard error
            #errors.append(("SET_ERROR", str(e), record[0])) # Create error warning
        else:
            
            soup = BeautifulSoup(res.text, 'html.parser') # Creates a BeautifulSoup object for HTML parsing

            ID = 1 # Creates ID for card
            cards = soup.find_all("div", {"class":"resizing-cig"}) # Find all cards on page
            
            #print("Inserting cards into database (" +str(int(record[0])) + ") +" + str(time.time()-start)[:4] + "s")
            
            for card in cards: # Iterate through all cards on page

                sql = "SELECT Card_ID, Set_ID FROM Cards WHERE Card_ID = ? AND Set_ID = ?"
                cursor.execute(sql,ID,record[0])
                result = cursor.fetchone()

                if result == None:

                    name = card.find("img").get("alt") # Find name of card

                    if "Plains" not in name and "Island" not in name and "Swamp" not in name and "Mountain" not in name and "Forest" not in name: # Special Cases

                        link = "https://www.ebay.co.uk/sch/i.html?_from=R40&_trksid=p2380057.m570.l1311&_nkw=" + name.replace(" ", "+").lower() + "+mtg" # Create eBay search link
                        updatetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S") # Find time when record is inserted into database
                        
                        sql = (
                            r'''
                                INSERT INTO Cards (Card_ID, Set_ID, Name_of_Card, eBay_Search_Link, Last_Updated)
                                VALUES (?,?,?,?,?)
                                '''
                            ) # Query for inserting card data into database
                        
                        cursor.execute(sql,ID,record[0],name,link,updatetime) # Send query to database
                        conn.commit() # Complete the request

                ID += 1 # Prepare for card
            
    cursor.close() # Close connection with database
    conn.close()
    
    #print("Finding card values, this may take up to 45 minutes...") 
    #valuingErrors = (update_cards.update_cards()) # Fill Cards with market values and save errors
    #for error in valuingErrors:
        #errors.append(error)

    #print("Closing connection with database...")

    t1 = time.time() - t0 # Calculate time taken for performance

    if len(errors) == 0:
        success = True
        #print("Card database updated successfully...") # Display final messages
    else:
        success = False
        major = 0
        minor = 0
        for error in errors: # Calculate severity of errors
            if error[0] == "SET_ERROR":
                major += 1
            elif error[0] == "MARKET_VALUE_ERROR":
                minor += 1
        #print("Card database updated with " + str(major) + " major error(s)  and " + str(minor) + " minor error(s)") # Update user with problems identified by system
        #print("Error list: ") # Display errors
        #for error in errors:
##            print("------------------------------")
##            print("Type: " + error[0])
##            print("Reason: " + error[1])
##            print("Affected: " + error[2])
##            print("------------------------------")
##  print("Time: " + str(t1)[:4] + "s") # Display total time taken to complete full update
    return success


def find_sets(): # Collect eBay data

    t0 = time.time() # Find time when database update begins

    #print("Finding sets...")

    #print("Preparing to update set database......")
    #print("Establishing connection to database...")
    conn = pyo.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\james\Desktop\eBay Scraper\MTGCards.accdb;') # Connect to MS Access database
    cursor = conn.cursor() # Create a link to interact with database
    
    #print("Searching for sets...")
    res = requests.get("https://magic.wizards.com/en/content/standard-formats-magic-gathering") # Downloads the mtg page for processing
    res.raise_for_status() # Raises an exception error if there's an error downloading the website
    soup = BeautifulSoup(res.text, 'html.parser') # Creates a BeautifulSoup object for HTML parsing
    
    ID = 1 # Creates ID for set
    raw = soup.find_all("div", {"class":"product-parade__item-content module_product-parade-no-hover"}) # Find all sets on page

    #print("Inserting sets into database...")
    
    for set in raw: # Iterate through all sets on page

        sql = "SELECT Set_ID FROM Sets WHERE Set_ID = ?"
        cursor.execute(sql,ID)
        result = cursor.fetchone()

        if result == None:
                    
            name = set.find("h3").get_text().replace(" of ", "") # Find name from raw data

            prev = " "
            name2 = ""
            for char in name:
                if ord(char) >= 65 and ord(char) <= 90:
                    if prev != " ":
                        name2 += " "
                prev = char
                name2 += prev

            if name2[-1:] == " ":
                name = name2[:-1]
            else:
                name = name2.replace("Core ", "Core Set ")
            
            link = "https://magic.wizards.com/en/articles/archive/card-image-gallery/" + name.lower().replace(" ", "-") # Create link for wofthec card database
            updatetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S") # Find time when record is inserted into database

            sql = (
                                    r'''
                                        INSERT INTO Sets(Set_ID, Set_Name, Card_Search_Link, Last_Updated)
                                        VALUES (?,?,?,?)
                                    '''
                                    ) # Query for inserting set data into database

            cursor.execute(sql,ID,name,link,updatetime) # Send query to database
            cursor.commit() # Complete the request

        ID += 1 # Prepare for next eBay listing

    # Special cases
    sql = "UPDATE Sets SET Card_Search_Link = 'https://magic.wizards.com/en/products/throne-of-eldraine/cards' WHERE Set_Name = 'Throne of Eldraine'"
    cursor.execute(sql)
    sql = "UPDATE Sets SET Card_Search_Link = 'https://magic.wizards.com/en/articles/archive/card-image-gallery/ikoria-lair-behemoths' WHERE Set_Name = 'Ikoria Lair of Behemoths'"
    cursor.execute(sql)
    sql = "UPDATE Sets SET Set_Name = 'Strixhaven School of Mages' WHERE Set_Name = 'Strixhaven'"
    cursor.execute(sql)
    cursor.commit()

    #print("Closing connection with database...")
    cursor.close() # Close connection with database
    conn.close()

    t1 = time.time() - t0 # Calculate time taken for performance

    #print("Sets database updated successfully...") # Display final messages 
    #print("Time: " + str(t1)[:4] + "s") # Display total time taken to complete full update
    return True

