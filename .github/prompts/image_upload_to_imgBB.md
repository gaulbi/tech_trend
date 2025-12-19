# ImgBB Uploader

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Tasks**: Generate a complete Python module implementation based on the detailed requirements below.

---

## Module Overview
**Purpose**: Upload image file to ImgBB. 

---

## Implementation
- Review the existing module, `hashnode.py`, and use it as a reference.
- Keep HashNodeUploader contstructor input parameters.
- Implement following method; upload, _handle_retry, _extract_url, _upload_attempt
- Use **ImgBB API** as a reference

---

## ImgBB API

### Parameters
- **key (required)**  
The API key.

- **image (required)**  
A binary file, base64 data, or an image URL (up to 32 MB).

- **name (optional)**  
The name of the file; this is automatically detected if you upload a file using POST and multipart/form-data.

- **expiration (optional)**  
Enable this if you want uploads to be automatically deleted after a certain time (in seconds, 60-15552000).

**Example call**  
```bash
curl --location --request POST "https://api.imgbb.com/1/upload?expiration=600&key=YOUR_CLIENT_API_KEY" --form "image=R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
```

Note: Always use POST when uploading local files. URL encoding may alter the base64 source due to encoded characters or simply because of the URL length limit when using GET.

### API response
API v1 responses display all uploaded image information in JSON format.

In the JSON response, the headers will include status codes to let you easily determine whether the request was OK. It will also include the `status` property.

**Example response (JSON)**  
```json
{
	"data": {
		"id": "2ndCYJK",
		"title": "c1f64245afb2",
		"url_viewer": "https://ibb.co/2ndCYJK",
		"url": "https://i.ibb.co/w04Prt6/c1f64245afb2.gif",
		"display_url": "https://i.ibb.co/98W13PY/c1f64245afb2.gif",
		"width":"1",
		"height":"1",
		"size": "42",
		"time": "1552042565",
		"expiration":"0",
		"image": {
			"filename": "c1f64245afb2.gif",
			"name": "c1f64245afb2",
			"mime": "image/gif",
			"extension": "gif",
			"url": "https://i.ibb.co/w04Prt6/c1f64245afb2.gif",
		},
		"thumb": {
			"filename": "c1f64245afb2.gif",
			"name": "c1f64245afb2",
			"mime": "image/gif",
			"extension": "gif",
			"url": "https://i.ibb.co/2ndCYJK/c1f64245afb2.gif",
		},
		"medium": {
			"filename": "c1f64245afb2.gif",
			"name": "c1f64245afb2",
			"mime": "image/gif",
			"extension": "gif",
			"url": "https://i.ibb.co/98W13PY/c1f64245afb2.gif",
		},
		"delete_url": "https://ibb.co/2ndCYJK/670a7e48ddcb85ac340c717a41047e5c"
	},
	"success": true,
	"status": 200
}
```

## IMPORTANT
- The hashnode.py is invoked from other py file in current application, and the the newly created py file will replace hashnode.py.
- To minimzie code change in existing application, signaure of methods used by existing code should be reserved as much as. 
- Keep signaure of `__init__` and `upload` methods in hashnode.py AS IS.