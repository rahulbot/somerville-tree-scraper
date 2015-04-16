import sys, re, logging, csv, os, urllib2
import mechanize
from BeautifulSoup import BeautifulSoup
import pyproj

#logger = logging.getLogger("mechanize")
#logger.addHandler(logging.StreamHandler(sys.stdout))
#logger.setLevel(logging.DEBUG)

BASE_URL = "http://www.daveytreekeeper.com/mass/MI_Somerville/"
SITE_URL = BASE_URL + "site_view.cfm?siteID="
TYPE_STREET_TREES = "street"
TYPE_PARK_TREES = "park"
CACHE_DIR = "cache"
FEET_TO_METERS = 0.3048

# the X/Y co-ordinates are the US state plane for Massachusetts Mainland (in feet)
state_plane_projection = pyproj.Proj(init="epsg:26986")

# setup the cache
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# login as a guest by grabbing in the secret login code
print "Logging in as a guest..."
br = mechanize.Browser()
br.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')]
br.open(BASE_URL)
assert br.viewing_html()
print "  fetched homepage"
html = br.response().read()
search = re.search('"public" . [0-9]*',html)
code = "public"+search.group(0)[11:]
print "  logging in with secret code "+code
br.select_form(name='theForm')
br.form['nameFld'] = code
br.form['pwFld'] = code
br.submit()
assert br.viewing_html()

def cache_get(key):
	if os.path.isfile(os.path.join(CACHE_DIR,key)):
		with open(os.path.join(CACHE_DIR,key), "r") as myfile:
		    return myfile.read()
	return None

def cache_put(key,content):
	text_file = open(os.path.join(CACHE_DIR,key), "w")
	text_file.write(content)
	text_file.close()

def scrape(type_to_scrape):

	# select street or park trees
	print "Setting type to "+type_to_scrape
	br.open('/mass/MI_Somerville/Prefs_Entry.cfm')
	br.select_form("form") 
	if type_to_scrape==TYPE_STREET_TREES:
		br.form['selectRad'] = ['1']	# street trees
	else:
		br.form['selectRad'] = ['2']	# park trees
	br.submit()
	assert br.viewing_html()

	# now scrape till we run out of sites
	tree_list = []
	current_site_id = 1
	while(True):

		tree_info = {}
		tree_info['type'] = type_to_scrape
		tree_info['id'] = type_to_scrape+str(current_site_id)

		# fetch the page
		print "Scraping "+type_to_scrape+" site "+str(current_site_id) 
		cache_key = type_to_scrape+str(current_site_id)
		if cache_get(cache_key)==None:
			print "  "+SITE_URL+str(current_site_id)+" (adding to cache)"
			try:
				br.open('/mass/MI_Somerville/site_view.cfm?siteID='+str(current_site_id))
			except urllib2.HTTPError, e:
				print "  Error: ", e.code
				break
			assert br.viewing_html()
			cache_put(cache_key, br.response().read())
		else: 
			print "  "+SITE_URL+str(current_site_id)+" (from cache)"
		content = cache_get(cache_key)
		soup = BeautifulSoup( content )
		tables = soup.findAll('table')
		
		if "This site has been deleted." in content:
			current_site_id = current_site_id + 1
			continue
		if "There is no record of this site in the database." in content:
			break

		# grab location details
		tableRows = tables[1].findAll('tr')
		if type_to_scrape==TYPE_STREET_TREES:
			tree_info['number'] = tableRows[1].findAll('td')[1].text
			tree_info['suffix'] = tableRows[2].findAll('td')[1].text
			tree_info['street'] = tableRows[3].findAll('td')[1].text
			tree_info['side'] = tableRows[4].findAll('td')[1].text
			tree_info['site'] = tableRows[5].findAll('td')[1].text
			tree_info['on_street'] = tableRows[7].findAll('td')[1].text
			tree_info['from_street'] = tableRows[8].findAll('td')[1].text
			tree_info['to_street'] = tableRows[9].findAll('td')[1].text
			tree_info['facility'] = ""
			tree_info['facility_name'] = ""
			tree_info['x'] = tableRows[10].findAll('td')[1].text
			tree_info['y'] = tableRows[11].findAll('td')[1].text
		else:
			tree_info['number'] = ""
			tree_info['suffix'] = ""
			tree_info['street'] = ""
			tree_info['side'] = ""
			tree_info['site'] = tableRows[3].findAll('td')[1].text
			tree_info['on_street'] = ""
			tree_info['from_street'] = ""
			tree_info['to_street'] = ""
			tree_info['facility'] = tableRows[1].findAll('td')[1].text
			tree_info['facility_name'] = tableRows[2].findAll('td')[1].text
			tree_info['x'] = tableRows[5].findAll('td')[1].text
			tree_info['y'] = tableRows[6].findAll('td')[1].text

		# convert form state plane to lat/lng
		lat_lng = state_plane_projection(float(tree_info['x'])*FEET_TO_METERS,float(tree_info['y'])*FEET_TO_METERS,inverse=True)
		tree_info['longitude'] = lat_lng[0]
		tree_info['latitude'] = lat_lng[1]

		# grab detailed tree_info
		tableRows = tables[2].findAll('tr')
		tree_info['date'] = tableRows[0].findAll('td')[1].text
		tree_info['remote_id'] = tableRows[1].findAll('td')[1].text
		tree_info['current_site_id'] = tableRows[2].findAll('td')[1].text
		tree_info['species'] = tableRows[3].findAll('td')[1].text.replace("&nbsp;","").strip()
		tree_info['dbh'] = tableRows[4].findAll('td')[1].text
		tree_info['trunks'] = tableRows[5].findAll('td')[1].text
		tree_info['condition'] = tableRows[6].findAll('td')[1].text
		tree_info['cavity_present'] = tableRows[7].findAll('td')[1].text
		tree_info['weak_fork'] = tableRows[8].findAll('td')[1].text
		tree_info['percentage_of_dead_wood'] = tableRows[9].findAll('td')[1].text
		tree_info['maintenance'] = tableRows[10].findAll('td')[1].text
		tree_info['clean'] = tableRows[11].findAll('td')[1].text
		tree_info['raise'] = tableRows[12].findAll('td')[1].text
		tree_info['reduce'] = tableRows[13].findAll('td')[1].text
		tree_info['further_inspection'] = tableRows[14].findAll('td')[1].text
		tree_info['consult'] = tableRows[15].findAll('td')[1].text
		tree_info['utilies_present'] = tableRows[16].findAll('td')[1].text
		tree_info['plant_location'] = tableRows[17].findAll('td')[1].text
		tree_info['area'] = tableRows[18].findAll('td')[1].text
		tree_info['staff'] = tableRows[19].findAll('td')[1].text
		tree_info['location_value'] = tableRows[20].findAll('td')[1].text
		tree_info['ground_maintenance'] = tableRows[21].findAll('td')[1].text

		# grab risk assessment tree_info
		weird_comment_to_remove = "Justin Stratton, 1/17/2008:  Report the value that is being weighted to the user"
		tree_info['size_of_existing_defect'] = tableRows[24].findAll('td')[1].text.replace(weird_comment_to_remove, "")
		tree_info['probability_of_failure'] = tableRows[25].findAll('td')[1].text.replace(weird_comment_to_remove, "")
		tree_info['target_impact'] = tableRows[26].findAll('td')[1].text.replace(weird_comment_to_remove, "")
		tree_info['other'] = tableRows[27].findAll('td')[1].text.replace(weird_comment_to_remove, "")
		tree_info['hazard_rating'] = tableRows[28].findAll('td')[1].text

		tree_list.append(tree_info)
		current_site_id = current_site_id + 1

	print "Collected "+str(current_site_id)+" "+type_to_scrape+" sites"
	return tree_list

tree_list = []
tree_list = tree_list + scrape(TYPE_PARK_TREES)
tree_list = tree_list + scrape(TYPE_STREET_TREES)

field_names = tree_list[0].keys()
writer = csv.DictWriter(open("somerville-tree-details.csv",'wb'), fieldnames=field_names)
headers = dict( (n,n) for n in field_names )
writer.writerow(headers)
for tree_info in tree_list:
	writer.writerow(tree_info)
