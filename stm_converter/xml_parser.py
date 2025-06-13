from pygccxml import utils
from pygccxml import declarations
from pygccxml import parser
# from rosidl_parser.definition import 
# from stm_converter.message_specification import MessageSpecification, BasicType, Field, BASIC_TYPES
from rosidl_adapter.parser import MessageSpecification, Type, Field
from rosidl_adapter.parser import PRIMITIVE_TYPES, parse_message_file

from stm_converter.ros_msg_generator import get_msg_fields

import ros2interface.api as interface
from os import getcwd, walk

VECTOR_TYPE_PREFIX = "std::vector<"
VECTOR_TYPE_SUFFIX = ">"
STRUCT_NAME_SEPARATOR = "_"
DECLARATION_PREFIX = "_"
MESSAGE_FILE_EXTENSION = ".msg"
SCOPE_RESOLUTION_OPR = "::"

def generate_msg_name(msg_name: str):
    processed_msg_name = ''

    if msg_name.find(STRUCT_NAME_SEPARATOR) != -1:
        split_msg = msg_name.split(STRUCT_NAME_SEPARATOR)

        for part in split_msg:
            if part:
                processed_msg_name += part.title()
            else:
                print("error: remove first or last underscore")
                return ''
    else:
        processed_msg_name += msg_name.title()

    return processed_msg_name


def find_context_pkg(typename: str):

    context_pkg = ''
    pathToFile = ''
    already_exists = False

    # checks whether interface exists
    interfaces = interface.get_interface_packages()
    pkgs = list(interfaces.keys())

    msg_interfaces = interface.get_message_interfaces(pkgs)   
    for pkg, msgs in msg_interfaces.items():
        if "msg/" + typename in msgs:
            context_pkg += pkg
            pathToFile = interfaces[pkg] + "/share"
            already_exists = True
    
    if not context_pkg:
        msg = typename + MESSAGE_FILE_EXTENSION
        curr_dir = getcwd()
        for root, dirs, files in walk(curr_dir):
            if msg in files:
                context_pkg += "enter_interface_name"
                pathToFile = curr_dir
            else:
                pass # generate msg for it
    
    print(f"pathToFile = {pathToFile}")
    return context_pkg, pathToFile, already_exists


def get_fields(already_exists: bool, pkg_name: str, path:str , name: str):
    filename = ''
    if already_exists:
        filename = f"{path}/{pkg_name}/msg/{name}" + MESSAGE_FILE_EXTENSION
    else:
        filename = f"{path}/{name}" + MESSAGE_FILE_EXTENSION

    print(f"filename = {filename}")

    msg = parse_message_file(pkg_name=pkg_name, interface_filename=filename)
    fields = get_msg_fields(msg)

    return fields


def remove_namespace(typename: str):
    namespace = ''
    type_ = ''

    parts = typename.split(SCOPE_RESOLUTION_OPR)
    print(f"typename = {typename}")

    if len(parts) == 2:
        namespace = parts[0]
        type_ = generate_msg_name(parts[1])
    
    else:
        print("illegal use of '::' operator!!")

    return namespace, type_

def process_non_primitives(typename: str, is_array=False):
    field_type = ''

    if typename in PRIMITIVE_TYPES: 
        field_type += typename

    elif typename + '64' in PRIMITIVE_TYPES: # example 64, it could be 8, 16, 32
        field_type += typename + '64'

    else:
        field_type += typename

        # assuming namespace typed struct
        if field_type.find(SCOPE_RESOLUTION_OPR):
            namespace, field_type = remove_namespace(field_type) 

        context_pkg, path, already_exists = find_context_pkg(field_type)
        msg_fields = get_fields(already_exists=already_exists, pkg_name=context_pkg, path=path, name=field_type)

    if is_array: field_type += "[]"

    return context_pkg, msg_fields, field_type


class xmlParser:
    def __init__(self, filename, namespace=""):
        # Find out the c++ parser
        generator_path, generator_name = utils.find_xml_generator()

        # Configure the xml generator
        xml_generator_config = parser.xml_generator_configuration_t(
            xml_generator_path=generator_path,
            xml_generator=generator_name)
        
        self.filename = filename
        self.namespace = namespace
        self.ns = None
        self.user_ns = ""
        self.struct_name = ""

        self.structs = {}

        self.decls = parser.parse([filename], xml_generator_config)
        self.global_namespace = declarations.get_global_namespace(self.decls)
        self.namespaces = self.global_namespace.namespaces()

        # if namespace provided by the user
        if namespace:
            self.ns = self.global_namespace.namespace(namespace)

        else:
            for ns in self.namespaces:
                # print(f"namespace = {ns.name}")
                self.user_ns = ns.name

            self.ns = self.global_namespace.namespace(self.user_ns)

    def get_decls(self):
        msg_name = ''
        fields = []

        for decl in self.ns.declarations:
            # if decl.name == "MyConfigData":
            # if isinstance(decl, declarations.opaque_type_t):
            #     print("opaque")
            if isinstance(decl, declarations.class_t):
                if str(decl.name).startswith(DECLARATION_PREFIX): continue
                temp = {decl.name: {}}
                self.struct_name = decl.name

                msg_name += generate_msg_name(decl.name)
                context_pkg = None

                for var in decl.variables():
                    var_type = ""

                    field_name = var.name
                    field_type = ''
                    msg_fields = None

                    # use isinstance() instead of type()
                    if type(var.decl_type) == declarations.cpptypes.int_t:
                        field_type += "int64"

                    elif type(var.decl_type) == declarations.cpptypes.float_t:
                        field_type += "float64"

                    elif type(var.decl_type) == declarations.cpptypes.bool_t:
                        field_type += "bool"

                    elif str(var.decl_type).startswith(VECTOR_TYPE_PREFIX):
                        vector_type = str(var.decl_type).strip(VECTOR_TYPE_PREFIX).strip(VECTOR_TYPE_SUFFIX)
                        context_pkg, msg_fields, field_type = process_non_primitives(vector_type, True)

                    else:
                        print(f"weird type found - {var.decl_type}")
                        context_pkg, msg_fields, field_type = process_non_primitives(str(var.decl_type))
                    
                    field_type = Type(field_type, context_package_name=context_pkg)
                    field = Field(type_=field_type, name=field_name)
                    field.msg_fields = msg_fields
                    fields.append(field)

                    # print(type(var.decl_type))
                    temp[decl.name].update({var.name: var_type})
                    # msg.set_field(field)

                self.structs.update(temp)

        msg = MessageSpecification(pkg_name="enter_pkg_name", msg_name=msg_name, fields=fields, constants=[])
        # print(f"structs_found = {self.structs}")
        return self.structs, msg