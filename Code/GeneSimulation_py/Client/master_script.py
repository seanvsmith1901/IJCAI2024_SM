# this master script needs to be able to both start the gui, then start the server, and then have them interact with eachother as appropriate.
# this is gonna be a ride.
import queue
from multiprocessing import Process

import jhg_client
import data_collection_script
import multiprocessing

if __name__ == '__main__':
    q = queue.Queue()
    data_collection_process = Process(target=data_collection_script.start_client(), args=(q,))
    data_collection_process.start()
    jhg_client.start_gui()

    # I need to check the queue periodically to make sure that everything is up to date.




