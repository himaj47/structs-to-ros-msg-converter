from jinja2 import Environment, FileSystemLoader
import importlib.resources as pkg_resources
import stm_converter

class ROSMsgGenerator:
    def __init__(self, structs_found, header:str):
        pathToTemplates = pkg_resources.files(stm_converter) / "resources/jinja_templates"
        self.env_ = Environment(loader=FileSystemLoader(pathToTemplates))
        self.structs_found_ = structs_found
        self.header_name_ = header
        self.filename_without_ext = ""
        # template = None

    def gen_msgs(self):
        template = self.env_.get_template("multi_struct.txt")
        # context = {"data_json": self.structs_found_}

        for msg in self.structs_found_.items():
            filename = f"{msg[0].title()}.msg"
            self.filename_without_ext = msg[0].title()

            context = {"msg": msg[1]}

            with open(filename, mode="w", encoding="utf-8") as output:
                output.write(template.render(context))

    def gen_type_adapter(self): # use struct name from xmlParser class
        template = self.env_.get_template("type_adapter.txt")
        context = {"header": self.header_name_, 
                   "msg_file_name": self.filename_without_ext,
                   "struct_name": list(self.structs_found_.keys())[0]}
        
        temp_file_name = f"{list(self.structs_found_.keys())[0]}_type_adapter.hpp"
        
        with open(temp_file_name, mode="w", encoding="utf-8") as output:
                output.write(template.render(context))