import requests
import json
import credentials as creds

image_file = "elife-images.txt"
uri_root = "https://elife-publishing-cdn.s3.amazonaws.com"
dlcs_api_base_uri = "https://api.dlcs.io"
elife_dlcs_id = "9"

image_info = open(image_file, 'r').readlines()

test_image_info = image_info[:200]
# print test_image_info

def get_url_form_image_info_line(line):
	uri = ""
	line.rstrip()
	uri_stem = line.split()[-1]
	uri = uri_root + "/" + uri_stem
	return uri

uris = map(get_url_form_image_info_line, test_image_info)
# print uris


def get_DLCS(endpoint):
	r = requests.get(endpoint, auth = (creds.KEY, creds.SECRET))
	print r.status_code
	print r.text

def post_DLCS(endpoint, data):
	r = requests.post(endpoint, auth = (creds.KEY, creds.SECRET), data=json.dumps(data))
	print r.status_code
	print r.text

def put_DLCS(endpoint, data):
	r = requests.put(endpoint, auth = (creds.KEY, creds.SECRET), data=json.dumps(data))
	print r
	print endpoint
	print r.status_code
	print r.text
	print r.headers
	print r.text



def generate_collection(space, uris):
	"""
	{
	  "@type": "Collection",
	  "member": [
	    {
	      "space" : "3",
	      "origin": "http://customer.com/images/Mushrooms.jpg",
	      "tags": ["mushroom"],
	      "string1": "mystring"
	    },
	    {
	      "space" : "3",
	      "origin": "http://customer.com/images/chicken-w-mushrooms-1.jpg",
	      "tags": ["mushroom", "tasty"],
	      "string1": "mystring"
	    }
	  ]
	}
	"""
	members = []
	for uri in uris:
		members.append({"space":space, "origin": uri})

	collection = {"@type": "Collection", "member": members}
	return collection

elife_customer_endpoint = dlcs_api_base_uri + "/customers/" + elife_dlcs_id
elife_spaces = elife_customer_endpoint + "/spaces/images"
elife_all_images = elife_customer_endpoint + "/allImages"
elife_submission_endpoint = elife_customer_endpoint + "/queue"
elife_space_new = elife_customer_endpoint + "/spaces/2"

get_DLCS(elife_customer_endpoint)

data = {"name":"test_create", "id": "2{}"}
put_DLCS(elife_space_new, data)


# get_DLCS_endpoint(elife_spaces)
# get_DLCS_endpoint(elife_all_images)


# collection = generate_collection(1, uris)
# print collection
# push_to_DLCS(elife_submission_endpoint, collection)
