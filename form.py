from dataclasses import dataclass
from typing import List, override
from logging import getLogger
from enum import StrEnum
from util import chunks, list2d_to_str

from bs4 import BeautifulSoup
import requests
            
logger = getLogger(__name__)

def process_not_implemented(param_name: str, form: BeautifulSoup):
    if param_name == "autorefresh": raise NotImplementedError("autorefresh not supported yet")
        # options = datetime.now()
        # logger.warning("autorefresh not supported yet")
        # # scraped_data['params'][param_name] = value
        # continue

    eq_pos = param_name.find("=")
    if eq_pos != -1: raise NotImplementedError("param_name with = not supported yet")
        # options = param_name[eq_pos + 1:]
        # param_name = param_name[:eq_pos]
        # form_model['params'][param_name] = {"options": options, "desc": None, "id": None}
        # continue

    input_array = form.select_one('[name^="{param_name}[]"]')
    if input_array and len(input_array) > 0: raise NotImplementedError("param_name with [] not supported yet")
        # options = [el.get('value') for el in input_array]
        # form_model['params'][param_name] = {"options": {""}}#options
        # continue

def get_label(form_soup: BeautifulSoup, el: BeautifulSoup) -> str:
    id = el.get('id')
    if id is None: id = el.get("aria-labelledby")
    
    label = form_soup.select_one(f'label[for="{id}"]')
    if label:
        return label.get_text()
    return None

@dataclass
class Input:
    id: str
    value: str
    desc: str
    related: List['Param'] = None



@dataclass
class Param:
    class Type(StrEnum):
        checkbox = "checkbox"
        radio = "radio"
        file = "file"
        text = "text"
        textarea = "textarea"
        select = "select"
    name: str
    type: Type
    desc: str = None
    options: List[Input] = None

    def validate(self, value):
        match self.type:
            case Param.Type.file:
                raise NotImplementedError("params of type file is not implemented yet")
            case Param.Type.text|Param.Type.textarea:
                return value is not None
            case _:
                return value in self._option_values
    
    def get_related_for(self, option_value: str):
        try:
            opt = self.option(option_value)
        except ValueError: return None
        return opt.related

    def option(self, value: str):
        if self.type != Param.Type.select and self.type != Param.Type.radio: raise ValueError("option can only be called on select or radio params")
        for opt in self.options:
            if opt.value == value: return opt

    @property
    def _option_values(self):
        for opt in self.options: yield opt.value

    @override
    def __str__(self) -> str:
        s = f"<<<{self.name}>>> --- {self.desc}:        ({self.type.value})"
        if len(self.options) == 1:
            s += f"\n{self.options[0].value}"
        if self.type == Param.Type.select or self.type == Param.Type.radio:
            s += "\n"
            s += list2d_to_str(chunks([f"[{opt.value}]: {opt.desc}" for opt in self.options], 3))
        elif len(self.options) > 1: 
            s += f"\n{[opt.value for opt in self.options]}"
        return s
        

    @classmethod
    def root_param(cls, name: str, form: BeautifulSoup):
        if name in ["show_remaining", "show_blockers"]:
            dodebug = 1
        root_param = Param(name=name, type=None)

        input_els = form.select(f'[name="{name}"]')
        if len(input_els) == 0: raise ValueError(f"Input {name} not found")
        # if len(input_els) == 1:

        first_el = input_els[0]
        match first_el.name:
            case "input":
                match first_el.get('type'):
                    case 'checkbox': root_param.type = Param.Type.checkbox
                    case "radio": root_param.type = Param.Type.radio
                    case "file": root_param.type = Param.Type.file
                    case "text": root_param.type = Param.Type.text
                    case _: raise NotImplementedError(f"no type supported yet for iput {name} of name {first_el.name} and type {first_el.get('type')} ")
            case "textarea": root_param.type = Param.Type.textarea
            case "select": root_param.type = Param.Type.select
            case _: raise NotImplementedError(f"no type supported yet for iput {name} of name {first_el.name} and type {first_el.get('type')}\naccording to the js code, i should get the input value or True if the input value in None")


        
            

        match root_param.type:
            case Param.Type.checkbox:
                root_param.desc = get_label(form, first_el)
                root_param.options = [
                    Input(first_el.get('id'), val, None)
                    for val in ["true", "false"]
                    ]
            case Param.Type.text|Param.Type.textarea:
                root_param.desc = get_label(form, first_el)
                root_param.options = [
                    Input(first_el.get('id'), "... some text ...", None)
                    ]
            case Param.Type.file:
                raise NotImplementedError(f"file input type not supported yet")
            case Param.Type.select:
                root_param.desc = get_label(form, first_el)
                root_param.options = [
                    Input(first_el.get('id'), el.get('value'), el.get_text(strip=True))
                    for el in first_el.select(f'option')
                    ]
            case Param.Type.radio:
                label_group = form.select_one(f'[role="radiogroup"][aria-labelledby]:has([name="{name}"])')
                if label_group: 
                    desc = form.select_one(f'label#{label_group.get("aria-labelledby")}').get_text()
                    if desc: root_param.desc = desc
                root_param.options = [
                    Input(first_el.get('id'), el.get('value'), get_label(form, el))
                    for el in form.select(f'input[name="{name}"]')
                    ]
        return root_param
            


@dataclass
class FormModel:
    DCODE_URL = "https://www.dcode.fr/"

    page_id: str
    page_url: str 
    page_name: str
    page_desc: str
    id: str
    method: str
    params: List[Param] = None

    def param(self, name: str):
         for param in self.params:
            if param.name == name:
                return param
    
    

    @classmethod
    def fetch_by_id(cls, id: str):
        try:
            response = requests.get( cls.DCODE_URL+id )
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching url: {e}")
            return None
        soup = BeautifulSoup(response.content, 'html.parser')

        forms = soup.select('#forms form[id]')
        if not forms:
            raise ValueError("No forms found on page")
            logger.warning("No forms found on page")
            return None
        if len(forms) > 1:
            raise ValueError("Multiple forms found on page")
            logger.warning("Multiple forms found on page")
        
        page_id = soup.select_one("&>body[id]")["id"]
        page_name = soup.select_one("h1#title").get_text()
        page_desc = soup.select_one("p#overview").get_text() 
        scraped_forms = []
        for form in forms:
            form_model = FormModel(
                page_id=page_id,
                page_name=page_name,
                page_desc=page_desc,
                page_url=cls.DCODE_URL+page_id,
                id=form.get('id'),
                method=form.get('method'),
                params=[]
            )

            btns = form.select("button[data-post]")
            if len(btns) != 1: raise ValueError("Multiple buttons found: ", btns)

            labelledby_inputs: List[BeautifulSoup] = []

            for param_name in btns[0].get('data-post').split(','):
                if param_name is None: raise ValueError("param_name is None")
                process_not_implemented(param_name, form)

                input = form.select_one(f'[name="{param_name}"]')
                if input.get('aria-labelledby'):
                    labelledby_inputs.append(input)
                    continue # skip aria-labelledby
            
                form_model.params.append(
                    Param.root_param(name=param_name, form=form)
                )
                    

            for input in labelledby_inputs:
                label = form.select_one(f'#{input.get("aria-labelledby")}')
                
                related_param = Param.root_param(name=input.get('name'), form=form)
                related_param.desc = label.get_text()

                parent_input_tag = form.select_one(f'#{label.get("for")}')
                prt_in_name = parent_input_tag.get('name')
                prt_in_value = parent_input_tag.get('value')
                parent_input = form_model.param(prt_in_name).option(prt_in_value)
                
                if not parent_input.related: 
                    parent_input.related = []
                parent_input.related.append(related_param)
                
                
            scraped_forms.append(form_model)

        return scraped_forms[0]
