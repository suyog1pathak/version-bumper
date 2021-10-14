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
    """ Index limit for version string (1.1.1.1) considering it as a list """
    self.indexLimit = 3

    try:
      poster.debug("Reading package.json")
      with open(self.file) as file:  
        d = file.read()
        """ This will hold the json body of package.json """
        self.jsonData = json.loads(d)
    except Exception as e:
      poster.error(e)
      raise e

  def pullInfo(self):
    """ This method will parse the github payload for the source branch nam. :: external method """
    try:
      with open(self.detailsFile) as f:
        t = f.read()
        """ This is a merge req """
        if json.loads(t).get("pull_request"):
         self.branchName = json.loads(t).get("pull_request").get("head").get("ref")
         poster.debug("merge request detected :: branch name = {}".format(self.branchName)) 

         """ Direct push with local merge """
        elif json.loads(t).get("base_ref"):
          self.branchName = json.loads(t).get("base_ref")
          poster.debug("push with local merge detected :: branch name = {}".format(self.branchName))

        else:
          """ Direct Push on the same branch """
          raise Exception("Error :: As this is the direct commit on branch")

    except Exception as e:
      poster.error(e)
      raise e        

  def versionCreator(self, version: str, indexNumber: int) -> str:
    """ This method will take version string and index number as a input where indexnumber is the position of number
    to increment, rest indicies will be set to zero :: Internal method """
    poster.debug("Creating the incremented version string from {}".format(version))
    versionList = version.split(".")
    versionList[indexNumber] = int(versionList[indexNumber]) + 1
    indexForZero = indexNumber + 1

    while indexForZero <= self.indexLimit:
      poster.debug("Setting {}th index of version string to 0".format(indexForZero))
      versionList[indexForZero] = 0
      indexForZero += 1
    
    finalList = '.'.join(str(i)for i in versionList)
    poster.debug("incremented Version string :: {}".format(finalList))
    return finalList

  def writeConfig(self, version: str) -> None: 
    """ Update the json object and dump it into the file :: Internal method """
    self.jsonData["version"] = version
    try:
      with open(self.file, 'w') as f:
        poster.debug("Updating package.json")
        json.dump(self.jsonData, f, ensure_ascii=False, indent=1)
    except Exception as e:
      poster.error(e)
      raise e        

  def bumpUp(self) -> str:
    """ This is the main method which will bump the version number in package.json based on the branch name :: External Method """
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
