
########################################

######     Maintain Database      ######

########################################


## Imports ##

from bs4 import BeautifulSoup
import requests
import pyodbc as pyo
import time
from datetime import datetime, timedelta
import threading

## Functions ##

def update_listings(): # Collect eBay data

    t0 = time.time() # Find time when database update begins
    errors = []

    #print("Finding listings...")
    
    #print("Preparing to update listing database......")
    #print("Establishing connection to database...")
    conn = pyo.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\james\Desktop\eBay Scraper\MTGCards.accdb;') # Connect to MS Access database
    cursor = conn.cursor() # Create a link to interact with database
    
    sql = "SELECT * FROM Cards ORDER BY Set_ID ASC, Card_ID ASC" # Query to find entire database
    cursor.execute(sql) # Send query to database
    
    for record in cursor.fetchall(): # Iterate through 
        
        start = time.time() # Time to calculate passed time

        try:
            res = requests.get(record[5]) # Downloads the page for processing
            res.raise_for_status() # Raises an exception error if there's an error downloading the website
        except requests.exceptions.HTTPError:
            errors.append(("EBAY_SEARCH_ERROR", str(e), (record[0],record[1])))
        else:
            soupProduct = BeautifulSoup(res.text, 'html.parser') # Creates a BeautifulSoup object for HTML parsing


            ID = 1 # Creates ID for eBay listing
            product = soupProduct.find("li", {"data-view":"mi:1686|iid:"+str(ID)}) # Finds a listing

            sql = "SELECT max(Listing_ID) FROM Listings WHERE Card_ID = ? AND Set_ID = ?"
            cursor.execute(sql,record[0],record[1])

            listingID = cursor.fetchone()[0]
            if listingID == None:
                listingID = 1
            else:
                listingID += 1
                
            #print("Inserting/Updating listings into database (" +str(int(record[0])) + ", " + str(int(record[1]))+ ")... +" + str(time.time()-start)[:4] + "s")
            
            while product != None: # Iterate through each listing
                
                price = product.find("span", {"class": "s-item__price"}).get_text().replace(",", "")[1:] # Find price of listing
                            
                valid = True # Stores validity of listing
                
                if "to" in price: # Determine Validity
                    valid = False # Nullify Listing

                           
                if valid == True: # Continue Analysis if valid
                   
                    try:
                        price = float(price) # Convert to usable data type
                    except ValueError:
                        valid = False
                    else:

                        delivery = product.find("span", {"class": "s-item__shipping s-item__logisticsCost"}) # Find delivery cost of listing
                        link = product.find("a").get("href") # Find the Link for the Listing
                        
                        if delivery != None: # If a value was not found
                            delivery = product.find("span", {"class": "s-item__shipping s-item__logisticsCost"}).get_text().replace(",", "") # Find actual delivery cost
                        else: # Otherwise
                            delivery = product.find("span", {"class": "POSITIVE BOLD"}) # Find the tag for original delivery cost
                            if delivery != None: # Check if there was no delivery option with this tag
                                delivery = product.find("span", {"class": "POSITIVE BOLD"}).get_text().replace(",", "") # Find the text for original delivery cost
                            else:
                                valid = False


                    if valid == True:
                        
                        if delivery == "Shipping not specified" or delivery == "Postage not specified": # Check for delivery availibility
                            valid = False
                        elif delivery[0:4] == "Free": # Check for free delivery
                            delivery = 0 # Set delivery as '0'
                        else: # Otherwise
                            #Iterate through the delivery to find the cost
                            char = 3
                            hit = False
                            while char <= len(delivery) and hit == False:
                                if delivery[char:char+1] == " ":
                                    hit = True
                                else:
                                    char += 1
                            try:
                                delivery = float(delivery[3:char]) # Convert to usable data type
                            except ValueError:

                                try:
                                    delivery = float(delivery[4:char]) # Attempt to convert to usable data type based off known errors
                                except ValueError:
                                    valid == False
                                    print("ERROR")
                                    print(delivery)
                        
                        
                        if valid == True:
                            
                            name = product.find("h3", {"class": "s-item__title"}).get_text(separator=u" ").replace(",", "").lower() # Find name of listing
                            if record[2].lower() not in name or "art series" in name or "mardu shadowspear" in name: # Check if listing contains name of card
                                valid = False

                                
                            if valid == True:
                                
                                # Artificial Intelligence to Analysis Listing Title for Information #
                                
                                quantity = 0
                                foil = False
                                art = "Standard"
                                language = "Unknown"
                                condition = "Unknown"
                                
                                # Quantity in listing
                                if "4x" in name or "4 x" in name or "x4" in name or "x 4" in name:
                                    quantity = 4
                                elif "9x" in name or "9 x" in name or "x9" in name or "x 9" in name:
                                    quantity = 9
                                elif "3x" in name or "3 x" in name or "x3" in name or "x 3" in name:
                                    quantity = 3
                                elif "2x" in name or "2 x" in name or "x2" in name or "x 2" in name:
                                    quantity = 2
                                else:
                                    quantity = 1

                                # Foil
                                if "foil" in name:
                                    if "non-foil" not in name or "non foil" not in name:
                                        foil = True
                                    else:
                                        foil = False
                                else:
                                    foil = False

                                # Condition of card(s)
                                if "nm/m" in name or "m/nm" in name or "near mint" in name:
                                    condition = "Near Mint"
                                elif "mint" in name or "new" in name:
                                    condition = "Mint"
                                else:
                                    condition = "Unable to Determine"

                                # Extended art, alternate art
                                if "alternate art" in name:
                                    art = "Alternate Art"
                                elif "extended art" in name:
                                    art = "Extended Art"
                                elif "borderless" in name:
                                    art = "Borderless"
                                else:
                                    art = "Standard"

                                # Country of origin / language
                                if "english" in name:
                                    language = "English"
                                elif "japanese" in name:
                                    language = "Japanese"
                                elif "german" in name:
                                    language = "German"
                                elif "korean" in name:
                                    language = "Korean"
                                else:
                                    language = "Unable to Determine"

                                
                                link = product.find("a").get("href") # Find the Link for the Listing
                                updatetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S") # Find time when record is inserted into database
                                deleteTime = None

                                auctionHTML = product.find("span", {"class":"s-item__time-left"})
                                if auctionHTML != None:

                                    auction = True
                                    auctionTime = auctionHTML.get_text()
                                    intTime = ""
                                    deleteTime = datetime.now()
                                    for char in auctionTime:
                                        
                                        if char != "d" and char != "h" and char != "m" and char != " ":
                                            intTime += char

                                        elif char == "d":
                                            deleteTime += timedelta(days = int(intTime))
                                            intTime = ""

                                        elif char == "h":
                                            deleteTime += timedelta(hours = int(intTime))
                                            intTime = ""

                                        elif char == "m":
                                            deleteTime += timedelta(minutes = int(intTime))
                                            intTime = ""
                                    
                                    deleteTime += timedelta(hours = 1)

                                        
                                else:
                                    auction = False

                                sql = "SELECT Listing_ID, Listing_Name FROM Listings WHERE Card_ID = ? AND Set_ID = ?"
                                cursor.execute(sql,record[0],record[1])

                                hit = False
                                for listing in cursor.fetchall():
                                    if name == listing[1]:
                                        dupID = listing[0]
                                        hit = True
                                        
                                if hit == True:
                                    
                                    sql = "UPDATE Listings SET Quantity = ?, Foil = ?, Condition = ?, Artwork = ?, Language = ?, Price = ?, Delivery_Cost = ?, Total_Cost = ?, Auction = ?, Auction_Ends = ?, Listing_Search_Link = ?, Last_Updated = ? WHERE  Listing_ID = ? AND Card_ID = ? AND Set_ID = ?"
                                        
                                    cursor.execute(sql,quantity,foil,condition,art,language,price,delivery,price+delivery,auction,deleteTime,link,updatetime,dupID,record[0],record[1]) # Send query to database
                                    conn.commit()
                                    
                                elif hit == False:
                                    
                                    sql = (
                                        r'''
                                            INSERT INTO Listings(Listing_ID, Card_ID, Set_ID, Listing_Name, Quantity, Foil, Condition, Artwork, Language, Price, Delivery_Cost, Total_Cost, Auction, Auction_Ends, Listing_Search_Link, Last_Updated)
                                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                                        '''
                                        ) # Query for inserting listing data into database
                                    
                                    cursor.execute(sql,listingID,record[0],record[1],name,quantity,foil,condition,art,language,price,delivery,price+delivery,auction,deleteTime,link,updatetime) # Send query to database

                                    conn.commit() # Complete the request

                                    listingID += 1 # Prepare to find next place in database
                                
                ID += 1 # Prepare for next eBay listing
                
                product = soupProduct.find("li", {"data-view":"mi:1686|iid:"+str(ID)}) # Finds a listing

            sql = "DELETE FROM Listings WHERE Last_Updated > ? AND Card_ID = ? AND Set_ID = ?"
            cursor.execute(sql, start, record[0],record[1])
            cursor.commit()

    
    
    #print("Closing connection with database...")
    cursor.close() # Close connection with database
    conn.close()

    t1 = time.time() - t0 # Calculate time taken for performance

    return errors

    
def update_cards(set_ID = None, card_ID = None):

    errors = []
    
    conn = pyo.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\james\Desktop\eBay Scraper\MTGCards.accdb;') # Connect to MS Access database
    cursor = conn.cursor() # Create a link to interact with database

    if set_ID != None:

        if card_ID != None:
            sql = "SELECT * FROM Cards WHERE Card_ID = ? AND Set_ID = ?"
            cursor.execute(sql, card_ID, set_ID)

        elif set_ID == "BLANK":
            sql = "SELECT * FROM Cards WHERE Market_Value_Standard = 0 AND Market_Value_Foil = 0"
            cursor.execute(sql)

        else:
            sql = "SELECT * FROM Cards WHERE Set_ID = ?"
            cursor.execute(sql, set_ID)

    else:
        sql = "SELECT * FROM Cards"
        cursor.execute(sql)
    
    for record in cursor.fetchall(): # Iterate through database
        
        start = time.time()

        sql = "SELECT * FROM Sets WHERE Set_ID = ?"
        cursor.execute(sql,record[1])
        set = cursor.fetchone()
        
        urls = ["https://www.mtggoldfish.com/price/" + set[1].replace(" ","+").replace("'", "").replace(",","") + "/" + record[2].replace(" ","+").replace("'", "").replace(",","") + "#paper", "https://www.mtggoldfish.com/price/" + set[1].replace(" ","+").replace("'", "").replace(",","") + ":Foil/" + record[2].replace(" ","+").replace("'", "").replace(",","") + "#paper"] # Create ULRs
        market_value = [] # Stores market value of cards

        for url in urls: # Iterate through URLs to find market values

            try:
                res2 = requests.get(url) # Downloads the page for processing
                res2.raise_for_status() # Raises an exception error if there's an error downloading the website
            except requests.exceptions.HTTPError as e: # Safeguard error
                errors.append(("MARKET_VALUE_ERROR", str(e), record[2])) # Create error warning
                market_value.append(0) # Set default value to '0'
            #except ssl.SSLEOFError as e: # Safeguard error
                #errors.append(("MARKET_VALUE_ERROR", str(e), pseudoname)) # Create error warning
                #market_value.append(0) # Set default value to '0'
            except requests.exceptions.ConnectionError as e: 
                errors.append(("MARKET_VALUE_ERROR", str(e), record[2])) # Create error warning
                market_value.append(0) # Set default value to '0'
            else: # If no error was found
                
                soup2 = BeautifulSoup(res2.text, 'html.parser') # Creates a BeautifulSoup object for HTML parsing

                try:
                    market_value.append(soup2.find("div", {"class":"price-box paper"}).find("div", {"class":"price-box-price"}).get_text()[1:]) # Saves market value of card
                except AttributeError as e:
                    errors.append(("MARKET_VALUE_ERROR", str(e), record[2])) # Create error warning
                    market_value.append(0)

        updatetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S") # Find time when record is inserted into database
        sql = "UPDATE Cards SET Market_Value_Standard = ?, Market_Value_Foil = ?, Last_Updated = ? WHERE Card_ID = ? AND Set_ID = ?"

        #print(record[2] + "... +" + str(time.time() - start)[:4] + "s") # Display confirmation that cards were entered into database
        
        cursor.execute(sql,market_value[0],market_value[1],updatetime,record[0],record[1])
        cursor.commit()
        
    cursor.close() # Close connection with database
    conn.close()
    
    return errors


def update_purchase_listings():
    
    conn = pyo.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\james\Desktop\eBay Scraper\MTGCards.accdb;') # Connect to MS Access database
    cursor = conn.cursor() # Create a link to interact with database

    sql = "DELETE FROM Purchase_Listings"
    cursor.execute(sql)
    cursor.commit()

    #Non-Foil Cards
    sql = "SELECT Listings.Listing_ID, Listings.Card_ID, Listings.Set_ID, Listings.Listing_Name, Listings.Total_Cost,(Cards.Market_Value_Standard*Quantity - Listings.Total_Cost) AS Profit, Listings.Listing_Search_Link FROM Listings, Cards WHERE Listings.Total_Cost/Listings.Quantity < Cards.Market_Value_Standard AND Listings.Foil = False AND Listings.Set_ID = Cards.Set_ID AND Listings.Card_ID = Cards.Card_ID"
    cursor.execute(sql)

    for record in cursor.fetchall():
        margin = record[5]/record[4] * 100

        if margin >= 10:
            sql = "INSERT INTO Purchase_Listings(Listing_ID,Card_ID,Set_ID,Listing_Name,Total_Cost,Profits,Margin,Listing_Search_Link) VALUES(?,?,?,?,?,?,?,?)"
            cursor.execute(sql,record[0],record[1],record[2],record[3],record[4],record[5],margin,record[6])
            conn.commit()

    #Foil Cards
    sql = "SELECT Listings.Listing_ID, Listings.Card_ID, Listings.Set_ID, Listings.Listing_Name, Listings.Total_Cost,(Cards.Market_Value_Foil*Quantity - Listings.Total_Cost) AS Profit, Listings.Listing_Search_Link FROM Listings, Cards WHERE Listings.Total_Cost/Listings.Quantity < Cards.Market_Value_Standard AND Listings.Foil = True AND Listings.Set_ID = Cards.Set_ID AND Listings.Card_ID = Cards.Card_ID"
    cursor.execute(sql)

    for record in cursor.fetchall():
        margin = record[5]/record[4] * 100
        
        sql = "INSERT INTO Purchase_Listings(Listing_ID,Card_ID,Set_ID,Listing_Name,Total_Cost,Profits,Margin,Listing_Search_Link) VALUES(?,?,?,?,?,?,?,?)"
        cursor.execute(sql,record[0],record[1],record[2],record[3],record[4],record[5],margin,record[6])
        conn.commit()

        
def maintain():

    listings_thread = threading.Thread(target = update_listings)
    card_thread = threading.Thread(target = update_cards)

    listings_thread.start()
    card_thread.start()

    listings_thread.join()
    card_thread.join()

    update_purchase_listings()
