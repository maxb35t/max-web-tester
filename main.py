import requests
import re
import time
from joblib import Parallel, delayed

words = []

url = "https://raw.githubusercontent.com/dwyl/english-words/master/words.txt"
req = requests.get(url)
if req.status_code == requests.codes.ok:
  lines = []
  for i in req.iter_lines():
    spacesRemoved = re.sub(" ", "", i.decode("utf-8"))
    hasObject = re.search("((?<=\()).*(?=\))", spacesRemoved)
    if hasObject != None:
      lines.append(hasObject.group())
    lines.append(re.sub("\(.*\)", "", spacesRemoved).lower())
  words = lines

domains = [str(x) + ".co.uk" for x in words]

for i in range(len(domains)):
  domains[i] = str(domains[i])

proxies = [
  "135.181.251.106:8888", "5.39.217.21:3128", "45.9.188.100:8888",
  "95.217.131.241:8888", "135.181.198.9:8888", "95.216.223.135:8888",
  "135.181.194.189:8888", "95.217.23.223:8888", "135.181.251.106:8888"
]
currentProxy = 0

proxy = {"https": proxies[currentProxy]}

proxyCounter = 0

n_jobs = 100


def checkDomain(domain):
  global proxyCounter, currentProxy
  try:
    x = requests.get("https://rdap.nominet.uk/uk/domain/" + domain,
                     proxies=proxy)
    while x.status_code == 429:
      proxyCounter = proxyCounter + 1
      if proxyCounter == 10:
        proxyCounter = 0
        if currentProxy != len(proxies) - 1:
          currentProxy = currentProxy + 1
        else:
          currentProxy = 0
      time.sleep(0.1)
      x = requests.get("https://rdap.nominet.uk/uk/domain/" + domain,
                       proxies=proxy)
    if x.status_code == requests.codes.ok:
      if "pending delete" in x.json()["status"]:
        with open("domains.txt", "a") as file:
          file.write("PENDING: " + domain + "\n")
          return domain
    elif x.status_code == requests.codes.not_found:
      if "not found" in x.json()["title"]:
        test = re.search("^[A-Za-z0-9-]*[A-Za-z0-9]\.co\.uk", domain)
        if test:
          with open("domains.txt", "a") as file:
            file.write("NEW: " + domain + "\n")
          return domain
    print(x.status_code)
  except:
    checkDomain(domain)


result = Parallel(n_jobs=n_jobs, verbose=10)(delayed(checkDomain)(domain)
                                             for domain in domains)

available_domains = [domains[idx] for idx, r in enumerate(result) if r != None]
print(available_domains)
