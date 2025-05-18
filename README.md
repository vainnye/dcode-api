# DCode API

A Python API wrapper for interacting with dcode.fr tools via it's obfuscated web API. This library provides a clean interface for scraping and interacting with dcode.fr's encryption, encoding, and other utility tools.

I'm not affiliated with dcode (https://www.dcode.fr/). Shoutout to them for making their cool website, very usefull for learning math btw.

I had the idea of this project when I wrote some text using qwerty layout on my pc without knowing it. I went onto dcode's website to decode the text to azerty layout. I was currious about their source code, so I looked into it and made this python project.

## Features

- Form scraping and parameter extraction
- Support for various input types (checkbox, radio, text, textarea, select)
- Automatic form validation
- Clean object-oriented interface

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

![illustration : converting text written in different keyboard layouts on dcode's website from auto to azerty](https://github.com/user-attachments/assets/e48da7ac-47c2-4160-8e99-fac5a97ad46a)
![illustration : converting text written in different keyboard layouts with my dcode-api from auto to azerty](https://github.com/user-attachments/assets/0754f2d9-b196-436a-94e3-271a1881b162)


### Basic Usage

```python
from query import Query

# Create a Query instance
query = Query()

# Fetch a form by its ID (the part after dcode.fr/ in the URL)
query.fetch_form("chiffre-changement-clavier")

# Fill the form with user imput
query.fill_form()

# Send the filled form
query.send()

# Print the response
print(query.response)
```


### Support

A lot of features are not supported yet, and probably never be. This project is just a proof of concept, the code is not optimized and some parts are not verry readable.
For support, please open an issue on GitHub.

## Known Limitations

Currently, the following features are not implemented:

- File upload parameters (not my priority, they're not that interresting)
- Autorefresh parameters I've never seen them (they're just in the js code of dcode.fr)
- Parameters with "=" in their html tag "name" property 
- Array parameters (with [] notation in their html tag "name" property)

## License

NO LICENSE ...
