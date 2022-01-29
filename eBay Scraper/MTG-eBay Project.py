
from fill_database import find_cards, find_sets
from maintain_database import maintain
from user_interface import run_interface
import threading

print("Running database maintanance software...")
print("Updating database...")

### Uncomment these lines when running for the first time ##

#find_sets()
#find_cards()

############################################################


print("Database up to date...")
print("Running interface...")

maintanance_thread = threading.Thread(target = maintain)
interface_thread = threading.Thread(target = run_interface)

maintanance_thread.start()
interface_thread.start()

maintanance_thread.join()
interface_thread.join()
