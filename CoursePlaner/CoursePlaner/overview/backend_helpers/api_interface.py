from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

def main():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options = options)
    driver.get("http://www.vvz.ethz.ch/Vorlesungsverzeichnis/sucheLehrangebotPre.view?lang=de")
    assert "ETH" in driver.title


    elem = driver.find_element_by_name("q")
    elem.clear()
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
    driver.close()

def list_courses_dpt():
    #Test for CHAB
    http://www.vvz.ethz.ch/Vorlesungsverzeichnis/sucheLehrangebot.view?lang=de&search=on&semkez=2022S&studiengangTyp=BSC&deptId=20&studiengangAbschnittId=&lerneinheitstitel=&lerneinheitscode=&famname=&rufname=&wahlinfo=&lehrsprache=&periodizitaet=&katalogdaten=&_strukturAus=on&search=Suchen

#TODO: find dept id's 20 = CHAB
def create_search_string(lang = "de", semester = "2022S", degree = "BSC", deptId=20, stgAbschnittID = "", lerneinheitstittel = "", lerneinheitscode = "", famname = "", rufname= "", wahlinfo = ""):
    basepath = "http://www.vvz.ethz.ch/Vorlesungsverzeichnis/sucheLehrangebot.view"



if __name__ == "__main__":
    main()