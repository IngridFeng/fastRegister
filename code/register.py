from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

url = "https://horizon.mcgill.ca/pban1/twbkwbis.P_GenMenu?name=bmenu.P_StuMainMnu"
id = input("Please enter your student ID: ")
try:
	int(id)
except ValueError:
	print("student id should be a number")
	exit()
# error handling if SID input is not a number

pin = input("Please enter your PIN: ")

term = input("Please enter the term you want to register(e.g. Summer 2018): ")
assert term == "Fall 2018" or term == "Winter 2019", "Unable to register courses in this term"
# currently minerva can only register for courses in these two terms

tmp = input("Please enter the course CRNs, separated with comma: ").split(",")
assert len(tmp) <= 10, "too many CRNs"
crns = []
for e in tmp:
	try:
		crns.append(int(e))
	except ValueError:
		crns.append(e.strip())
# parse input crns into a list of numbers and handle weird inputs

driver = webdriver.Firefox()
driver.get(url)

My_ID = driver.find_element_by_name("sid")
My_ID.clear()
My_ID.send_keys(id)#enter Mcgill Id

my_PIN = driver.find_element_by_name("PIN")
my_PIN.clear()
my_PIN.send_keys(pin)#enter password

driver.find_element_by_id("mcg_id_submit").click()#login

driver.implicitly_wait(3) # seconds
try:
	my_search = driver.find_element_by_id("keyword_in_id")
except NoSuchElementException:
	print("Invalid McGill ID or PIN")
	exit()
my_search.clear()
my_search.send_keys("quick")#enter quick
driver.find_element_by_xpath('//input[@value="Go"]').click()#click go

driver.implicitly_wait(3) # seconds
driver.find_element_by_xpath('//a[contains(text(), "Quick Add")]').click()#click quick add or drop

driver.implicitly_wait(3) # seconds
select = Select(driver.find_element_by_id("term_id"))
select.select_by_visible_text("{0}".format(term))#enter term
driver.find_element_by_xpath('//input[@value="Submit"]').click()#click submit

driver.implicitly_wait(3) # seconds
for x in range(0, len(crns)):
	my_CRN = driver.find_element_by_id("crn_id{0}".format(str(x+1)))
	my_CRN.clear()
	my_CRN.send_keys("{0}".format(crns[x]))#recursively enter CRN of courses

driver.implicitly_wait(3) # seconds
driver.find_element_by_xpath('//input[@value="Submit Changes"]').click()
#click submit course changes

driver.implicitly_wait(3) # seconds
def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return True
    return False, driver.find_element_by_xpath(xpath).text

copy_crns = crns
if check_exists_by_xpath('//span[@class="errortext"]')[0]:
	# if no error happens, all courses registered successfully
	print("Congrats! All courses are registered successfully!")
else:
	table = driver.find_element_by_xpath('//table[contains(@summary, "present Registration Errors")]')
	# get the whole error table
	err_mgs = [td.text for td in table.find_elements_by_xpath('//a[contains(@href, "rg_errors")]')]
	# get all the error messages
	i = 0
	for row in table.find_elements_by_xpath('.//tr'):
		info = [td.text for td in row.find_elements_by_xpath('.//td[@class="dddefault"][text()]')]
		# parse all the info of current course into list
		if info:

			j = 0
			if "Fall" in info[j] or "Winter" in info[j] or "Summer" in info[j]:
				j += 1
			try:
				curr_crn = int(info[j])
			except ValueError:
				curr_crn = info[j]
			# store the current crn into curr_crn
			if curr_crn in copy_crns:
				copy_crns.remove(curr_crn)
			# remove the crn from the list since it already failed

			if err_mgs[i] == "CRN DOES NOT EXIST":
				print("Unable to register course with CRN {0}: {1}".format(curr_crn, err_mgs[i]))
			else:
				print("Unable to register course {0} {1} with CRN {2}: {3}".format(info[j+1], info[j+2], curr_crn, err_mgs[i]))
			i += 1
	copy_crns = [e for e in copy_crns if e != ""]
	if copy_crns:
		print("Registered course(s) {0} successfully!".format(copy_crns))
		# remaining courses are registered successfully
driver.close()
