
########################################

######       User Interface       ######

########################################


## Imports ##

from interface_commands import display_purchase_listings,run_sql,delete_entire_database,find_record, find_cheapest

## Functions ##

def run_interface():
    
    command = input("Command: ")
    while command != "END":

        if command == "SHOW RECOMMENDED":
            display_purchase_listings()
        elif command == "RUN SQL":
            run_sql()
        elif command == "DELETE ALL":
            delete_entire_database()
        elif "FIND " in command:
            command += " "
            
            if "LISTING " in command:
                start = 13
                char2 = 13
                ID = []
                for char in command[13:]:
                    if char == " ":
                        ID.append(int(command[start:char2]))
                        start = char2 + 1
                        
                    char2 += 1
                listingID = ID[0]
                cardID = ID[1]
                setID = ID[2]
                find_record(Set_ID = setID, Card_ID = cardID, Listing_ID = listingID)
            
            elif "CARD " in command:
                start = 10
                char2 = 10
                ID = []
                for char in command[10:]:
                    if char == " ":
                        ID.append(int(command[start:char2]))
                        start = char2 + 1
                        
                    char2 += 1
                cardID = ID[0]
                setID = ID[1]
                find_record(Set_ID = setID, Card_ID = cardID)
               
            elif "SET " in command:
                start = 9
                char2 = 9
                ID = []
                for char in command[9:]:
                    if char == " ":
                        ID.append(int(command[start:char2]))
                        start = char2 + 1
                        
                    char2 += 1
                setID = ID[0]
                find_record(Set_ID = setID)

            elif "CHEAPEST " in command:
                start = 14
                char2 = 14
                ID = []
                for char in command[14:]:
                    if char == " ":
                        ID.append(int(command[start:char2]))
                        start = char2 + 1
                        
                    char2 += 1
                cardID = ID[0]
                setID = ID[1]
                find_cheapest(cardID, setID)

            else:
               print("Command invalid, try again.") 
                    

        else:
            print("Command invalid, try again.")

        command = input("Command: ")
