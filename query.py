from bs4 import BeautifulSoup
from form import FormModel, Param
from typing import TypedDict, Any, override
from pprint import pprint
from urllib.parse import urlencode
import requests
from util import static_init, dict_to_list2d, list2d_to_str
from logging import getLogger
from dataclasses import dataclass

logger = getLogger(__name__)

class Payload(TypedDict):
    tool: str

@dataclass
class Response:
    @dataclass
    class Data:
        caption: str
        notice: str
        results: str|int|float
        results2: Any
    @dataclass
    class Meta:
        time: Any
        html: str
        display: Any
        fullscreen: Any
    @dataclass
    class Errors:
        captcha: str
        fatalerror: str
        error: str
    data: 'Data'
    meta: 'Meta'
    errors: 'Errors'

    def __init__(self, data: dict) -> None:
        self.errors = Response.Errors(
            captcha=data.get("captcha"),
            fatalerror=data.get("fatalerror"),
            error=data.get("error")
        )

        res = data.get("results")
        if res:
            if isinstance(res, dict):
                res = dict_to_list2d(res)
            if isinstance(res, list) and len(res) > 0:
                if not isinstance(res[0], list):
                    res = [res]
                else:
                    for i, row in enumerate(res):
                        for j, cell in enumerate(row):
                            if isinstance(cell, str):
                                res[i][j] = BeautifulSoup(cell, 'html.parser').get_text()
                            else: raise NotImplementedError("NIY: results is a 3 or more dimensions array !?")
            elif not isinstance(res, str) and not isinstance(res, int) and not isinstance(res, float):
                logger.error("results tablen_html is not implemented in python")
                pprint(res)
                raise NotImplementedError("NIY: results tablen_html is not implemented in python")
        
        res2 = data.get("results2")
        if data.get("results2"):
            logger.error("results2 (and table_html) is not implemented in python")
            pprint(res2)
            raise NotImplementedError("NIY: results2 (and table_html) is not implemented in python")

        self.data = Response.Data(
            caption=None if not data.get("caption") else BeautifulSoup(data.get("caption"), 'html.parser').get_text(),
            notice=data.get("notice"),
            results=res,
            results2=res2
        )

        self.meta = Response.Meta(
            time=data.get("time"),
            html=data.get("html"),
            display=data.get("display"),
            fullscreen=data.get("fullscreen")
        )

    @override
    def __str__(self) -> str:
        s = "\nRESPONSE bellow:\n"
        if self.errors.captcha:
            return s+f"[ERROR] captcha: {self.errors.captcha}"
        if self.errors.fatalerror:
            return s+f"[ERROR] fatalerror: {self.errors.fatalerror}"
        if self.errors.error:
            return s+f"[ERROR] error: {self.errors.error}"

        if self.data.caption:
            s += f"Caption: {self.data.caption}\n"
        if self.data.notice:
            s += f"Notice: {self.data.notice}\n"
        if self.data.results:
            s += "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~\n"
            if isinstance(self.data.results, list):
                s += f"<<< Result >>> --------------\n"
                s += list2d_to_str(self.data.results)+"\n"
            else:
                s += f"Result: {self.data.results}\n"
            s += "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~\n"
        if self.data.results2:
            s += "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~\n"
            s += f"Results2:\n{self.data.results2}\n"
            s += "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~\n"
        return s


@static_init
class Query:
    _DCODE_URL = "https://www.dcode.fr/"
    _API_URL = "https://www.dcode.fr/api/"
    _DFT_HEADER = {
        # "Accept": "*/*",
        # !!!! ne surtout pas envoyer cela !!!! # "Accept-Encoding": "gzip, deflate, br, zstd",
        # "Accept-Language": "en-US,en;q=0.7,fr-FR;q=0.3",
        # "Connection": "keep-alive",
        # "Content-Length": "126",
        "Content-Type": "application/x-www-form-urlencoded;",
        #### "Cookie": "PHPSESSID=53f9d4835d46e8ee7f2010a70a0a7e92",
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

    _dft_session: requests.Session|None = None

    @classmethod
    def static_init(cls):
        cls._dft_session = cls._get_new_session()

    def __init__(self, form: FormModel = None):
        self.form: FormModel = form
        self.payload: Payload = None
        self.response: Response = None
        self._session = self._dft_session

    def load_session(self, force_new: bool = False):
        if force_new or self._session is None or self._session.headers == self._dft_session.headers:
            self._session = self._get_new_session()
        else:
            self._session = self._dft_session

    @classmethod
    def change_default_session(cls):
        cls._dft_session = cls._get_new_session()

    @classmethod
    def _get_new_session(cls):
        session = requests.Session()
        session.headers.update(cls._DFT_HEADER)
        session.get(cls._DCODE_URL)
        if not 'PHPSESSID' in session.cookies:
            raise Exception("Failed to obtain php session ID")
        return session
        
    
    def fetch_form(self, id: str):
        self.form = FormModel.fetch_by_id(id)

    @staticmethod
    def send_query(query: 'Query', return_raw_data=False) -> Response|dict:
        encoded_params = urlencode(query.payload)
        response = query._session.post(Query._API_URL, data=encoded_params)
        
        if not response:
            raise Exception("request failed !")

        try:
            data = response.json()
        except ValueError as error:
            logger.error("Error:", error)
            return None
        if not data:
            logger.error("No data returned!")
            return None

        if return_raw_data:
            return data
        return Response(data)

    def send(self):
        self.response = Query.send_query(self, return_raw_data=False)


    def fill_form(self):
        self.payload = {
            "tool": self.form.page_id
        }

        print("\n---------------------------------------------------------------")
        print("Formulaire: "+self.form.page_name+f" ({self.form.page_url})")
        print(self.form.page_desc)
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

        for p in self.form.params:
            self.ask_input(p)

    def ask_input(self, p: Param, indent: int = 0):
        for line in str(p).splitlines():
            print("\t"*indent + line)
        while not p.validate(self.payload.get(p.name)):
            self.payload[p.name] = input(f"{p.name}: ")
        
        related = p.get_related_for(self.payload[p.name])
        if related:
            for r in related: self.ask_input(r, indent+1)
