# DLCS - first impressions

The DLCS (Digital Library Cloud Services) is an experimental piece of infrastructure that the Wellcome trust is creating.
We got early preview access to test it. It intends to be a managed implementation of
the [IIIF](http://iiif.io) standards. You put your assets (usually images) into the service and
you get IIIF endpoints back, including image API endpoints, and the ability to
create presentation API endpoints. These are my experiences playing with these services.

IIIF stands for the International Image Interoperability Framework, but more than just being a standard that we can all go away and read, the development of this
framework has been closely mirrored by the creation of working reference implementations. These implementations allow you to create image servers that can
do pretty neat things with images, and that allow for the mixing and matching of images from different servers, to create combined viewing experiences.

# Why am I/eLife interested in this

At eLife we serve a lot of images, and we give each of those images their own DOI. For every image that we serve we generate a batch of different version of that image in different sizes so that we will be able to serve the most appropriate size for the person reading our paper. If you are reading on a phone you don't
want to be downloading full res images. If we found a way to serve these images
quickly, at just the right size, without having to pre-render them, that could
provide quite a saving on storage. We would get the benefit of allowing our
images to be interoperate with other services that used an IIIF system, and our images might be lined up to support image annotation systems, as the IIIF standard
ought to support image annotation. Finally, for very large biological images, we
could potentially use IIIF as a way to serve google-map like tiles, for an infinite zoom view of these large images, which we currently don't provide on our journal.

I've known about IIIF for close to year now, but I've not had the chance to explore it until Wellcome announced their DLCS pilot, and we got access to it.


# Image and Presentation APIs

The first thing to get sorted with IIIF is that there are two sides to the specification, the image API, and the presentation API.

As I understand it the [image API](http://iiif.io/api/image/2.0/#image-information) is used to request a specific instance of an image from an image server, along with metadata that is specific to that image, such as it's identifier, or what kinds of image manipulations this image supports. Think of this api as being used to get the
raw pixels, crops, rotations, and different versions of an image. We will see
some examples below.

The [presentation API](http://iiif.io/api/presentation/2.0/) returns information about how documents are related to each other, or how they should be laid our or presented. It has a concept of the canvas on which images are laid out, along with
sequence information and something called a manifest that ought to provide enough
information to allow a viewer to start showing information to the reader.

Wellcome have also created an Universal Viewer that can be passed an IIIF manifest, and we will see some examples of doing this later.


# accessing the DLCS

There is [developer documentation for the DLCS on gitbook](https://www.gitbook.com/book/dlcs/book/details), but it very much looked to me like documentation that is useful for people who already know what they are doing.

The trial version that we were given access to uses HTTP basic Auth at this point
for access. All of the interactions with the DLCS can be doing via the REST API,
and I chose to explore this using the python rested library.

Let's say that you have an account with `customer_id = 9`. The endpoint for
exploring the DLCS will be `https://api.dlcs.io/customers/9`. If you place
your login credentials in a `credentials.py` file then you can access the service
via:

>  
	import requests
	import credentials as creds
	customer_endpoint = "https://api.dlcs.io/customers/9"
	r = requests.get(customer_endpoint, auth = (creds.KEY, creds.SECRET))
	print r.status_code
	print r.text

This should return information about your account:

>   
	{
	  "@context": "https://api.dlcs.io/contexts/Customer.jsonld",
	  "@id": "https://api.dlcs.io/customers/9",
	  "@type": "vocab:Customer",
	  "portalUsers": "https://api.dlcs.io/customers/9/portalUsers",
	  "namedQueries": "https://api.dlcs.io/customers/9/namedQueries",
	  "originStrategies": "https://api.dlcs.io/customers/9/originStrategies",
	  "authServices": "https://api.dlcs.io/customers/9/authServices",
	  "roles": "https://api.dlcs.io/customers/9/roles",
	  "queue": "https://api.dlcs.io/customers/9/queue",
	  "spaces": "https://api.dlcs.io/customers/9/spaces",
	  "allImages": "https://api.dlcs.io/customers/9/allImages",
	  "storage": "https://api.dlcs.io/customers/9/storage",
	  "name": "elife",
	  "displayName": "elife",
	  "keys": [
	    "xxx"
	  ],
	  "administrator": false,
	  "created": "2016-03-02T14:30:47.592823+00:00",
	  "acceptedAgreement": true
	}

# Pushing images into DLCS

I manually created a `space` within my DLCS account from the DLCS portal. I know that the id for my space is `1`.

To push images into the DLCS there is a `queue` endpoint, and what seems to be the most basic call tells the queue to ingest an image from a uri into a given space. You can send in a lot more information, e.g. arbitrary metadata, and you can also set access policies on the image, but I just wanted to get started by pushing in some images.

I generated a list of images hosted on the eLife CDN, and created a python list
containing these uris.

From the documentation I copied the payload that you need to send to this API.

>  
	def generate_collection(space, uris):
		"""
		we need to generate the following JSON
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
	#
	uris = ["uri1", "uri2", "uri3"]
	data = generate_collection(1, uris)
	elife_submission_endpoint = elife_customer_endpoint + "/queue"
	r = requests.post(endpoint, auth = (creds.KEY, creds.SECRET), data=json.dumps(data))

I ran the same function a few times, and I expected that images would be replaced, but it seemed to me that copies of the images were created in the space, thought I didn't investigate in detail. You probably want to do a put or a patch to the specific image endpoint if you want to replace or update the image.

# Creating a new space through the API

The documentation was not 100% clear on this, but I got some assistance through the DLCS slack channel. You can do a put request to the space endpoint, but at the moment you need to provide the following in the payload to get the space to be created:

>   
	space_creation_endpoint = elife_customer_endpoint + "/spaces/2"
	data = {"name":"test_create", "id": "2"}
	r = requests.put(space_creation_endpoint, auth = (creds.KEY, creds.SECRET), data=json.dumps(data))

The key thing here is that the payload needs to include a name as well as the id of the space.


# Accessing a version of the served image from the DLCS.

Ok, so we have seen the virtual manifest for this one image, and we have seen that we can pass that manifest in to an instance of the universal viewer, but how do we access, and modify images directly from the IIIF server?

Given the customer id: `9`, the space id: `1` and the UID of the image, in this case: `6dbd6a99-9837-4252-a37f-0367c6fbbe25`, we can construct a query to the IIF image server:

[https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/full/!2000,2000/0/default.jpg](), which will ask for a jpg version of the image that is full size, within a canvas that is 2000 x 2000.

We can modify those parameters to ask for some alternative versions of the image, all of which are generated on the fly from the image server. There is good documentation on the [image API](http://iiif.io/api/image/1.1/), and I'm just going to step through a couple of examples below.

## smaller version of the image

This will give you a smaller version of the image.

[https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/full/!200,200/0/default.jpg](), and you should see:

![alt text][image-api-demo]

[image-api-demo]: https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/full/!200,200/0/default.jpg

## smaller version of the image, cropped to a specific region

![alt text][image-api-demo2]

[image-api-demo2]: https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/0,15,125,200/!100,200/0/default.jpg

## smaller version of the image, cropped to a specific region, and rotated by 90<sup>o</sup> and mirrored.

![alt text][image-api-demo3]

[image-api-demo3]: https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/0,15,125,200/!100,200/!90/default.jpg


## monochrome and smaller version of the image

![alt text][image-api-demo4]

[image-api-demo4]: https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/full/!200,200/0/grey.jpg

# Accessing a PDF version of your image.

The image API does support returning a [PDF version of the image](http://iiif.io/api/image/1.1/#4-5-format), but I'm not sure whether the DLCS system has implemented this yet.

# An example of using IIIF for responsive images.

My colleague [David Moulton]() prepared a small responsive image template for me, and I dropped in the appropriate calls the the IIIF server, and it seems to work perfectly.

>  
	<div class="wrapper">
	  <dl>
	    <dt>Current image path:</dt>
	    <dd class="output"></dd>
	  </dl>
	  <!-- Each srcset attribute takes comma-separated sets of image paths and image widths:
	         srcset="path-to-image [size-of-image-in-px]w, ..."
	       The <img> src attribute contains the path to the default fallback image. -->
	       <picture>
	       	<source media="(min-width: 800px)"  srcset="https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/full/!800,800/0/default.jpg 800w, https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/full/!400,400/0/default.jpg 400w" />
	       	<source media="(min-width: 600px)"  srcset="https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/full/!214,214/0/default.jpg 214w, https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/full/!100,100/0/default.jpg 100w, https://dlcs.io/iiif-img/9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25/full/!50,50/0/default.jpg 50w" />
	       	<img src="1.png" alt="" class="image" />
	       </picture>
	</div>

You can see the file in the gitrepo that I've created to collect these examples.


# Accessing the manifest endpoint for one image

So now we have seen how to add images to DLCS, how to retrieve those images using the IIIF image API, and how to manipulate those images through the IIIF API. The second part of the IIIF specification is about how to present objects in relation to one another, or on their own. One of the resources that the presentation API specifies is a manifest, and Wellcome and Digirati have built an open source viewer that can take a manifest and display it. Manifests can mash up images from multiple IIIF enabled servers.

There is an demo version of the viewer available at `, and with this demo you can point the viewer to any manifest that is available on the web.

The DLCS portal page for an image generates a manifest for that image, so for example for the following image ....


I've had hardly any time to look into this API, but Wellcome with digirati have built the universal viewer that can consume

From the portal I can browse the images that I have uploaded into the DLCS. For example one image is available at [https://portal.dlcs.io/Image.aspx?id=9/1/6dbd6a99-9837-4252-a37f-0367c6fbbe25](), which gives me the portal view to that image. The portal provides a link to a IIIF manifest file, just for that image. In this case the manifest is available from [http://dlcs.io/iiif-manifest/elife/neuroscience/6dbd6a99-9837-4252-a37f-0367c6fbbe25](). That manifest can be plugged in to an instance of the Universal viewer, and the DLCS portal provides a handy link for doing this. You can now view the deep zoom universal view on this image at [http://universalviewer.io/?manifest=http%3A%2F%2Fdlcs.io%2Fiiif-manifest%2Felife%2Fneuroscience%2F6dbd6a99-9837-4252-a37f-0367c6fbbe25#?c=0&m=0&s=0&cv=0&z=-0.7756%2C-0.205%2C2.1109%2C1.392](). I also quite like the non-full screen view of the universal viewer, and you can plug in your own manifest files, or browse some examples, at [http://universalviewer.io/examples/]().

# Named queries

# Summary of impressions of the DLCS and IIIF 
