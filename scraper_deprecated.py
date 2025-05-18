from datetime import datetime
from optparse import Option
from typing import TypedDict, Any, override
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from pprint import pprint
import requests
import logging
import json







# TODO: recode the fucntion that scrapes all the tools from dcode, in the new version













logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DCResponse(TypedDict):
    class Data(TypedDict):
        caption: str
        notice: str
        results: str|int|float
        results2: Any
    class Meta(TypedDict):
        time: Any
        html: str
        display: Any
        fullscreen: Any
    class Errors(TypedDict):
        captcha: str
        fatalerror: str
        error: str
    data: 'Data'
    meta: 'Meta'
    errors: 'Errors'


class DCRequestParams(dict):
    def __init__(self, form: 'DCFormModel'):
        super().__init__()
        self.model = form
        super().__setitem__('tool', form["tool_id"])

    @override
    def __getattribute__(self, name: str):
        if name == "model": return super().__getattribute__(name)
        if name in self.model['params']: 
            return self.get(name)
        else:
            return super().__getattribute__(name)

    @override
    def __setattr__(self, name: str, value):
        if name == "model": super().__setattr__(name, value)
        elif name in self.model['params']: 
            self[name] = value
        else:
            raise ValueError("request attributes are not assignable")

    @override
    def __setitem__(self, name: str, value):
        if name not in self.model['params']:
            if name == 'tool': raise ValueError(f"tool can't be reasigned")
            else: raise ValueError(f"wrong param name: {name} (with value: {value})")
        super().__setitem__(name, value)

    def setP(self, name: str, value):
        self[name] = value

    def send(self) -> 'DCQuery':
        return DCode.call_api(self)


class DCFormModel(TypedDict):
    class Option(TypedDict):
        option: str
        desc: str
    class Param(TypedDict):
        options: Option|list[Option]
        id: str
        desc: str
    tool_id: str
    tool_name: str
    tool_url: str
    form_id: str
    method: str
    params: dict[str, Param|list[Param]] # str est le name



class DCQuery(TypedDict):
    model: DCFormModel
    request: DCRequestParams
    response: DCResponse
    x: 'DCQueryHelper'


class DCQueryHelper:
    def __init__(self, model: DCQuery):
        self._model = model
    
    @property
    def json_resp(self):
        return json.dumps(self._model["response"]["data"], indent=4, ensure_ascii=False)


class DCode:
    DCODE_URL = "https://www.dcode.fr/"
    API_URL = "https://www.dcode.fr/api/"
    session = None
    session_cookie = "PHPSESSID=53f9d4835d46e8ee7f2010a70a0a7e92"

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(DCode, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        DCode.session_cookie = DCode._fetch_session_id()
        if not DCode.session_cookie:
            logger.error("Failed to obtain session ID")
            exit(1)
        DCode.HEADER["Cookie"] = "PHPSESSID="+DCode.session_cookie

    @classmethod
    def init(cls):
        return DCode()

    # First make a GET request to obtain a valid session
    @staticmethod
    def _fetch_session_id():
        DCode.session = requests.Session()
        DCode.session.get(DCode.DCODE_URL)
        if 'PHPSESSID' in DCode.session.cookies:
            return DCode.session.cookies['PHPSESSID']
        else:
            logger.error("Failed to obtain session ID")
            return None

    @staticmethod
    def fill_form(form_model: DCFormModel) -> DCRequestParams:
        params = DCRequestParams(form_model)

        print("Formulaire: "+form_model["tool_name"])
        for p in form_model['params']:
            print(p+" choices: "+str(form_model['params'][p]))
            params.setP(p, input(p+": "))
        
        return params

    @staticmethod
    def call_api(params: DCRequestParams) -> DCQuery:
        encoded_params = urlencode(params)
        response = DCode.session.post(DCode.API_URL, headers=DCode.HEADER, data=encoded_params)
        
        if not response:
            raise Exception("request failed !")

        try:
            data = response.json()
        except ValueError as error:
            logger.error("Error:", error)
            return None
        
        query: DCQuery = {
            "model": params.model,
            "request": params,
            "response": DCode._response_to_DCResponse(data)
        }
        query["x"] = DCQueryHelper(query)

        return query

    @staticmethod
    def _response_to_DCResponse(data) -> DCResponse:
        dcresponse: DCResponse = {
            "data": {},
            "meta": {},
            "errors": {},
        }
        
        dcresponse["errors"]["captcha"] = data.get("captcha")
        dcresponse["errors"]["fatalerror"] = data.get("fatalerror")
        dcresponse["errors"]["error"] = data.get("error")
        
        res = data.get("results")
        if res and not isinstance(res, str) and not isinstance(res, int) and not isinstance(res, float):
            logger.error("results tablen_html is not implemented in python")
            pprint(res)
            # raise NotImplementedError("NIY: results tablen_html is not implemented in python")
        dcresponse["data"]["results"] = res
        
        res2 = data.get("results2")
        if data.get("results2"):
            logger.error("results2 (and table_html) is not implemented in python")
            pprint(res2)
            # raise NotImplementedError("NIY: results2 (and table_html) is not implemented in python")
        dcresponse["data"]["results2"] = res2

        dcresponse["meta"]["time"] = data.get("time")
        dcresponse["meta"]["html"] = data.get("html")
        dcresponse["meta"]["display"] = data.get("display")
        dcresponse["meta"]["fullscreen"] = data.get("fullscreen")
        
        return dcresponse

    @staticmethod
    def format_result(data, post: DCRequestParams, all=False):
        doc: DCFormModel = {
            # "form_id": post.get("form_id"),
            # "tool_id": post.get("tool_id"),
            # "",
            # "request": post,
            # "response": {
            #     "data": {
            #         "caption": data.get("caption"),
            #         "notice": data.get("note"),
            #         "results": data.get("results"),
            #         "results2": data.get("results2"),
            #     },
            # }
        }

        # if all:
        #     err = {
        #         "captcha": data.get("captcha"),
        #         "fatalerror": data.get("fatalerror"),
        #         "error": data.get("error")
        #     }
        #     meta = {
        #         "time": data.get("time"),
        #         "html": data.get("html"),
        #         "display": data.get("display"),
        #         "fullscreen": data.get("fullscreen")
        #     }
        #     doc["response"]["errors"] = err
        #     doc["response"]["meta"] = meta
        
        
        if data.get("captcha"):
            logger.error("Captcha error: " + data.captcha)
            raise Exception("Captcha error: " + data.captcha)
        
        if data.get("fatalerror"):
            logger.error("Fatal error: " + data.fatalerror)
            raise Exception("Fatal error: " + data.fatalerror)
        
        error = None
        if data.get("error"):
            logger.error("error is not implemented in python")
            pprint(data.get("error"))
            error = "NIY: error is not implemented in python"
        
        res = data.get("results")
        if res and not isinstance(res, str) and not isinstance(res, int) and not isinstance(res, float):
            logger.error("results tablen_html is not implemented in python")
            pprint(res)
            results = "NIY: results tablen_html is not implemented in python"
        else:
            results = res
        
        results2 = data.get("results2")
        if data.get("results2"):
            logger.error("results2 (and table_html) is not implemented in python")
            pprint(data.get("results2"))
            results2 = "NIY: results2 (and table_html) is not implemented in python"
        
        time = data.get("time")
        if data.get("time"):
            time = data.get("time")
        
        html = data.get("html", "")
        if data.get("html"):
            html = data.get("html")

        display = data.get("display")
        if data.get("display"):
            display = "display: "+data["display"]
        
        fullscreen = data.get("fullscreen")
        if data.get("fullscreen"):
            fullscreen = "fullscreen: "+data["fullscreen"]
        
        if all:
            return doc
        else:
            return ''.join([f"- {k}: {v}\n" for k,v in doc["response"]["data"].items()])

    @staticmethod
    def scrape_tool_list(only_urls=False) -> list:
        scraped_data = []
        
        try:
            response = requests.get("https://www.dcode.fr/liste-outils")
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching url: {e}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        if only_urls:
            for detail in soup.select('#forms > details'):
                scraped_data += [DCode.DCODE_URL+el['href'] for el in detail.select('a')]
            return scraped_data

        for detail in soup.select('#forms > details'):
            model = {"cat_id": '', "cat_name": '', "sub_cats": [], "tools": []}
            if detail.name == 'details':
                model["cat_id"] = detail.get("id")
                model = DCode.__crawl_details(detail, model)
                scraped_data.append(model)
        return scraped_data

    
    def __crawl_details(categ:BeautifulSoup, parent_model) :
        for detail in categ.children:
            if detail.name == 'summary':
                parent_model['cat_name'] = detail.get_text()
            elif detail.name == 'details':
                model = {"cat_id": '', "cat_name": '', "sub_cats": [], "tools": []}
                model["cat_id"] = detail.get("id")
                parent_model['sub_cats'].append(model)
                DCode.__crawl_details(detail, model)
            else:
                parent_model['tools'] = [DCode.DCODE_URL+el['href'] for el in detail.select('a')]
        return parent_model
            


    def scrape_a_tool(url) -> list[DCFormModel]:
        """
        Scrapes the keyboard change form data from dcode.fr.

        Returns:
            dict: A dictionary containing the scraped form data, or None if an error occurs.
        """
        def get_label(form_soup: BeautifulSoup, input: BeautifulSoup) -> str:
            label = form_soup.find_one('label', {'for': input.get('id')})
            if label:
                return label.get_text()
            return None


        scraped_data = []

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching url: {e}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        tool_id = soup.select_one("&>body[id]")["id"]
        tool_name = soup.select_one("h1#title").get_text()
        for form in soup.select('#forms form[id]'):
            form_model: DCFormModel = {
                "tool_id": tool_id,
                "tool_url": DCode.DCODE_URL+tool_id,
                "tool_name": tool_name,
                "form_id": None,
                "method": None,
                "params": {},
            }

            if not form:
                print("Form not found.")
                return form_model # Return partially filled or empty data

            form_model["form_id"] = form.get('id')
            form_model["method"] = form.get('method')

            btns = form.select("button[data-post]")
            if len(btns) != 1: 
                logger.error("Multiple buttons found: ", btns)
                return None

            for param_name in btns[0].get('data-post').split(','):
                if param_name is None: continue
                
                options = None
                if param_name == "autorefresh":
                    options = datetime.now()
                    logger.warning("autorefresh not supported yet")
                    # scraped_data['params'][param_name] = value
                    continue
                
                eq_pos = param_name.find("=")
                if eq_pos != -1:
                    options = param_name[eq_pos + 1:]
                    param_name = param_name[:eq_pos]
                    form_model['params'][param_name] = {"options": options, "desc": None, "id": None}
                    continue
                
                input_array = form.select_one('[name^="{param_name}[]"]')
                if input_array and len(input_array) > 0:
                    options = [el.get('value') for el in input_array]
                    form_model['params'][param_name] = {"options": {""}}#options
                    continue
                
                input = form.select_one(f'[name="{param_name}"]')
                if(input is None):
                    logger.error(f"Input {param_name} not found on {url}")
                    continue
                if input.name == "input":
                    if input.get('type') == 'checkbox':
                        options = [True, False]
                    elif input.get("type") == "radio":
                        options = [el.get('value') for el in form.select(f'input[name="{param_name}"]')]
                    elif input.get('type') == "file":
                        options = "@file"
                    elif input.get('type') == "text":
                        options = "@text"
                elif input.name == "textarea":
                    options = "@textarea"
                elif input.name == "select":
                    options = [el.get('value') for el in input.select("option")]
                if options == None: options = input.get("value", True)
                
                form_model['params'][param_name] = options

            scraped_data.append(form_model)

        return scraped_data

    HEADER = {
        # "Accept": "*/*",
        # !!!! ne surtout pas envoyer cela !!!! # "Accept-Encoding": "gzip, deflate, br, zstd",
        # "Accept-Language": "en-US,en;q=0.7,fr-FR;q=0.3",
        # "Connection": "keep-alive",
        # "Content-Length": "126",
        "Content-Type": "application/x-www-form-urlencoded;",
        "Cookie": "PHPSESSID=53f9d4835d46e8ee7f2010a70a0a7e92",
        # "DNT": "1",
        # "Host": "www.dcode.fr",
        # "Origin": "https://www.dcode.fr",
        # "Priority": "u=4",
        "Referer": "https://www.dcode.fr/",
        # "Sec-Fetch-Dest": "empty",
        # "Sec-Fetch-Mode": "cors",
        # "Sec-Fetch-Site": "same-origin",
        # "Sec-GPC": "1",
        # "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0",
        "X-Requested-With": "XMLHttpRequest",
    }