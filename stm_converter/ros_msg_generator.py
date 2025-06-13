from jinja2 import Environment, FileSystemLoader
import importlib.resources as pkg_resources

import stm_converter
import ros2interface.api as interface

from rosidl_adapter.parser import MessageSpecification

def get_msg_fields(msg: MessageSpecification):
    all_fields = {}

    for field in msg.fields:
        all_fields[field.name] = [field.type.type, field.type.is_array, field.type.array_size, field.type.pkg_name]

        try:
            all_fields[field.name].append(field.msg_fields)
        except:
            field.msg_fields = {}
            all_fields[field.name].append(field.msg_fields)

    return all_fields


class ROSMsgGenerator:
    def __init__(self, structs_found, struct_name, header:str, namespace, msg: MessageSpecification=None):
        pathToTemplates = pkg_resources.files(stm_converter) / "resources/jinja_templates"
        self.env_ = Environment(loader=FileSystemLoader(pathToTemplates))

        self.structs_found_ = structs_found
        self.header_name_ = header
        self.ns = namespace

        self.msg_filename_ = msg.msg_name 
        self.msg_content_ = tuple()
        self.interface_type_ = None
        self.msg = msg
        self.struct_name = struct_name

    def gen_msgs(self):
        template = self.env_.get_template("message.txt")
        
        filename = self.msg.msg_name + ".msg"
        self.msg_content_ = get_msg_fields(self.msg)

        context = {"msg": self.msg_content_}

        with open(filename, mode="w", encoding="utf-8") as output:
                output.write(template.render(context))

    def gen_type_adapter(self): # use struct name from xmlParser class
        template = self.env_.get_template("type_adapter.txt")
        context = {"header": self.header_name_, 
                   "msg_file_name": self.msg.msg_name,
                   "struct_name": self.struct_name,
                   "msg": self.msg_content_,
                   "namespace": self.ns
                   }
        
        temp_file_name = f"{self.header_name_}_type_adapter.hpp"
        
        with open(temp_file_name, mode="w", encoding="utf-8") as output:
                output.write(template.render(context))

    def check_existance(self): # use find_content_pkg function from xml_parser
        is_present = False
        pkgs = list(interface.get_interface_packages().keys())

        msg_interfaces = interface.get_message_interfaces(pkgs)   
        for pkg, msgs in msg_interfaces.items():
            if "msg/" + self.msg_filename_ in msgs:
                # print(pkg) 
                is_present = True
                self.interface_type_ = f"{pkg}/msg/{self.msg_filename_}"
        # print(msg_interfaces)
        if not is_present:
            print(f"{self.msg_filename_}.msg does not exist")

        return is_present


                    