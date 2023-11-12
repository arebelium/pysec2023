import ftplib
from googlesearch import search
import threading
from queue import Queue, Empty
from urllib.parse import urlparse
from ftplib import FTP

ftp_sites = []
for site in search('inurl:ftp -inurl:(http|https)', tld="co.in", num=20, stop=20, pause=2):
    ftp_sites.append(site)

print_lock = threading.Lock()
def ftp_function(url):
    try:
        ftp = FTP(url.netloc)
        ftp.login()
        ftp.sock.settimeout(3)

        with print_lock:
            print(f"------------------------ {url.netloc} ------------------------")
            ftp.retrlines('LIST')

        ftp.quit()
    except ftplib.error_perm as e:
        with print_lock:
            print(f"Error: {e} - Failed to change directory for {url.netloc}")
    except Exception as e:
        with print_lock:
            print(f"Error: {e} - An unexpected error occurred for {url.netloc}")

def worker(queue, exit_event):
    while not exit_event.is_set():
        try:
            url = queue.get(timeout=1)
        except Empty:
            continue
        ftp_function(url)
        queue.task_done()

url_queue = Queue()
exit_event = threading.Event()
num_threads = 5
threads = []
for _ in range(num_threads):
    thread = threading.Thread(target=worker, args=(url_queue, exit_event))
    thread.start()
    threads.append(thread)

for url in ftp_sites:
    url_queue.put(urlparse(url))

url_queue.join()
exit_event.set()

for thread in threads:
    thread.join()