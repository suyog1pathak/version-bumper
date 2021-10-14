from typing import Dict
import os, json
import logging

"""Custom logger to log for console """
logging.basicConfig(
        format="%(asctime)s : %(levelname)s : [%(filename)s:%(lineno)s - %(funcName)10s()] : %(message)s"
  )
poster = logging.getLogger("poster")
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
poster.setLevel(level=LOGLEVEL)

#-------------------------------------------------------------------------------------------#

class operation():

  def __init__(self) -> None:
    self.branchName = ""
    self.file = "./package.json"
    self.detailsFile = os.environ.get("GITHUB_EVENT_PATH", "./detail.json")
    poster.debug("gathered required information..")
    self.indexLimit = 3

    try:
      with open(self.file) as file:  
        d = file.read()
        self.jsonData = json.loads(d)
    except Exception as e:
      raise e

  def pullInfo(self):
    try:
      with open(self.detailsFile) as f:
        t = f.read()
        """ This is a merge req """
        if json.loads(t).get("pull_request"):
         self.branchName = json.loads(t).get("pull_request").get("head").get("ref")

         """ Direct push with local merge """
        elif json.loads(t).get("base_ref"):
          self.branchName = json.loads(t).get("base_ref")
          poster.debug("Branchname == {}".format(self.branchName))

        else:
          """ Direct Push on the same branch """
          raise Exception("Error :: As this is the direct commit on branch")

        #self.branchName = json.loads(t).get("pull_request").get("head").get("ref")      
    except Exception as e:
      raise e        

  def versionCreator(self, version: str, indexNumber: int) -> str:
  
    versionList = version.split(".")
  
    versionList[indexNumber] = int(versionList[indexNumber]) + 1
    indexForZero = indexNumber + 1

    while indexForZero <= self.indexLimit:
      versionList[indexForZero] = 0
      indexForZero += 1
    
    finalList = '.'.join(str(i)for i in versionList)
    return finalList

  def writeConfig(self, version: str) -> None: 
    self.jsonData["version"] = version

    with open(self.file, 'w') as f:
      json.dump(self.jsonData, f, ensure_ascii=False, indent=2)    

  def bumpUp(self) -> str:
    if "release" in self.branchName:
      version = self.versionCreator(self.jsonData.get("version"), 1)
      self.writeConfig(version)
      return version

    elif "feature" in self.branchName:
      version = self.versionCreator(self.jsonData.get("version"), 2)
      self.writeConfig(version)
      return version

    elif "bugfix" in self.branchName or "hotfix" in self.branchName:
      version = self.versionCreator(self.jsonData.get("version"), 3)
      self.writeConfig(version)
      return version

    else:
      raise Exception("No matching branch found")


#--------------------------------------------------------------------------------------------------#
def initiate(event: dict = {} , context: dict = {}) -> None:
  try: 
    obj = operation()
    obj.pullInfo()
    version = obj.bumpUp()
    print(version)
  except Exception as e:
    raise e

if __name__ == "__main__":
  initiate({}, {})
