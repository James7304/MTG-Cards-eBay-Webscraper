
########################################

######     Interface Commands     ######

########################################


## Imports ##

import pyodbc as pyo
import time
from tabulate import tabulate
from maintain_database import update_purchase_listings

## Functions ##

def display_purchase_listings(top = 10, profit = 0.4, margin = None):

    update_purchase_listings()
    
    conn = pyo.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\james\Desktop\eBay Scraper\MTGCards.accdb;') # Connect to MS Access database
    cursor = conn.cursor() # Create a link to interact with database
    
    if margin != None:
        sql = "SELECT * FROM Purchase_Listings WHERE profits >= ? AND Margin >= ? ORDER BY Profits DESC, Margin DESC"
        cursor.execute(sql,margin,profit)

    else:
        sql = "SELECT * FROM Purchase_Listings WHERE profits >= ? ORDER BY Profits DESC, Margin DESC"
        cursor.execute(sql,profit)

    headers = ["Listing_ID","Card_ID","Set_ID","Listing_Name","Total_Cost","Profits","Margin"]
    records = []

    index = 1
    for record in cursor.fetchall():
        records.append(record[:-1])
        if index >= top:
            break
        else:
            index += 1
        
        
    print(tabulate(records, headers = headers ))
    
    cursor.close() # Close connection with database
    conn.close()


def run_sql(sql = None):

    conn = pyo.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\james\Desktop\eBay Scraper\MTGCards.accdb;') # Connect to MS Access database
    cursor = conn.cursor() # Create a link to interact with database

    if sql == None:
        sql = input("SQL Command (Click ENTR when done) : \n")
    
    if sql[:11] == "DELETE FROM" and "where" not in sql.lower():
        print("User attempting to entire restricted command. To continue please enter password.")
        password = input("Password: ")

        if password == "4762241406522623":
            try:
                cursor.execute(sql)
                conn.commit()
            except:
                print("Invalid command entered... Aborting...")
                return False

    elif sql[:6] == "SELECT":
        try:
            cursor.execute(sql)
        except:
            print("Invalid command entered... Aborting...")
            return False
        print(tabulate(cursor.fetchall()))
        
    else:
        try:
            cursor.execute(sql)
            conn.commit()
        except:
            print("Invalid command entered... Aborting...")
            return False

    cursor.close() # Close connection with database
    conn.close()

    print("Command entered successfully")
    return True


def delete_entire_database():

    print("ARE YOU SURE YOU WOULD LIKE TO DELETE ENTIRE DATABASE?")
    ans = input("Yes/No: ")
    if ans == "Yes":
        password = input("Password: ")
        if password == "4762241406522623":
            print("DELETING ENTIRE DATABASE...")
            
            conn = pyo.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\james\Desktop\eBay Scraper\MTGCards.accdb;') # Connect to MS Access database
            cursor = conn.cursor() # Create a link to interact with database

            sql = "DELETE FROM Purchase_Listings"
            cursor.execute(sql)
            sql = "DELETE FROM Listings"
            cursor.execute(sql)
            sql = "DELETE FROM Cards"
            cursor.execute(sql)
            sql = "DELETE FROM Sets"
            cursor.execute(sql)

            conn.commit()

            print("DATABASE DELETED")

            cursor.close() # Close connection with database
            conn.close()


def find_record(Set_ID = None, Card_ID = None, Listing_ID = None):

    if  Listing_ID != None:
        sql = "SELECT * FROM Listings WHERE Listing_ID = " + str(Listing_ID) + " AND Card_ID = " + str(Card_ID) + " AND Set_ID = " + str(Set_ID)
        run_sql(sql = sql)
    
    elif Card_ID != None:
        sql = "SELECT * FROM Cards WHERE Card_ID = " + str(Card_ID) + " AND Set_ID = " + str(Set_ID)
        run_sql(sql = sql)

    elif Set_ID != None:
        sql = "SELECT * FROM Sets WHERE Set_ID = " + str(Set_ID)
        run_sql(sql = sql)

    else:
        print("Invalid command entered... Aborting...")


def find_cheapest(Card_ID, Set_ID):

    conn = pyo.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\james\Desktop\eBay Scraper\MTGCards.accdb;') # Connect to MS Access database
    cursor = conn.cursor() # Create a link to interact with database
    
    sql = "SELECT * FROM Listings WHERE Card_ID = ? AND Set_ID = ? ORDER BY Total_Cost/Quantity ASC"

    cursor.execute(sql,Card_ID,Set_ID)
    print(tabulate([cursor.fetchone()]))

def find_cheapest_search(name):

    try:
        res = requests.get()#Ebay#) # Downloads the page for processing
        res.raise_for_status() # Raises an exception error if there's an error downloading the website
    except requests.exceptions.HTTPError:
        errors.append(("EBAY_SEARCH_ERROR", str(e), (record[0],record[1])))
    else:
        soupProduct = BeautifulSoup(res.text, 'html.parser') # Creates a BeautifulSoup object for HTML parsing


    ## Find Cheapest Card From Searching Name ##
