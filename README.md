# Item Catalog

Project for the Udacity Full Stack Web Developer Nanodegree Program.  
An application that provides a list of items within a variety of categories 
as well as provides a user registration and authentication system. Each user can manage his own categories and items.

## Supported Python versions
Application is compatible with Python 2.7 and higher.

## Installation

1. Install dependencies 
```
pip install flask sqlalchemy oauth2client
```
2. Download the application files
```
git clone https://github.com/azhurb/item-catalog.git
cd ./item-catalog
```
3. Obtain JSON file with OAuth credentials in the [Google Cloud Platform Console](https://console.cloud.google.com/apis/credentials) and put it in the project folder with file name `client_secret.json`.

4. Run the application
```
python ./app.py
```

## API

The application returns either the JSON or the HTML, depending on the value of the `Accept` header.

Get all categories with items:
```
curl -H "Accept: application/json" http://0.0.0.0:5000/catalog/
```
Get items of the specified category:
```
curl -H "Accept: application/json" http://0.0.0.0:5000/catalog/2/
```
Get item info
```
curl -H "Accept: application/json" http://0.0.0.0:5000/catalog/2/items/3/
```

## License

Licensed under the MIT license.
