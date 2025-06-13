from rosidl_adapter.parser import MessageSpecification, Type, Field, PRIMITIVE_TYPES, parse_message_file
import ros2interface.api as interface
from os import getcwd, walk
import os

def find_context_pkg(typename: str):

    context_pkg = ''
    pathToFile = ''

    # checks whether interface exists
    interfaces = interface.get_interface_packages()
    pkgs = list(interfaces.keys())

    msg_interfaces = interface.get_message_interfaces(pkgs)   
    for pkg, msgs in msg_interfaces.items():
        if "msg/" + typename in msgs:
            context_pkg += pkg
            pathToFile = interfaces[pkg] + f"/share"
    
    if not context_pkg:
        msg = typename + ".msg"
        curr_dir = getcwd()
        for root, dirs, files in walk(curr_dir):
            if msg in files:
                context_pkg += "enter_interface_name"
                pathToFile = curr_dir
            else:
                pass # generate msg for it

    return context_pkg, pathToFile


def generate_msg_name(msg_name: str):
    processed_msg_name = ''

    if msg_name.find('_') != -1:
        split_msg = msg_name.split('_')

        for part in split_msg:
            if part:
                processed_msg_name += part.title()
            else:
                print("error: remove first or last underscore")
                return ''
    else:
        processed_msg_name += msg_name.title()

    return processed_msg_name


def parse_msg_struct(msg_struct: dict) -> MessageSpecification: 
    fields = []
    msg_name = ""
    for msg in msg_struct.items():
        msg_name = generate_msg_name(msg[0])
        msg_content = msg[1].items()

        for field_name, field_type in msg_content:
            # print(f"field_name = {field_name}, field_type = {field_type}")

            typename = Type(field_type)
            field = Field(type_=typename, name=field_name)
            fields.append(field)

    msg = MessageSpecification(pkg_name="my_custom_interface", msg_name=msg_name, fields=fields, constants=[])
    return msg

def get_msg_fields(msg: MessageSpecification):
    all_fields = {}

    for field in msg.fields:
        all_fields[field.name] = (field.name, field.type.is_array, field.type.array_size, field.type.pkg_name)

    return all_fields


def get_field_names(pkg_name: str, path:str , name: str):
    filename = ''
    if pkg_name:
        filename = f"{path}/{pkg_name}/msg/{name}.msg"
    else:
        filename = f"{path}/{name}.msg"

    msg = parse_message_file(pkg_name=pkg_name, interface_filename=filename)
    fields = get_msg_fields(msg)

    return fields



def main():
    msg_struct = {"point_msg": {"x": "int64[]", "y": "int64", "z": "int64"}}
    msg = parse_msg_struct(msg_struct)
    print(*msg.fields)

    typename = Type("int64", context_package_name=None)
    field = Field(type_=typename, name="msg")
    print(field)

    msg_string = 'int64[] arr' \
    'float32 var'

    msg = parse_message_file("enter_pkg_name", "/home/himaj/stm_converter/stm_converter/Num.msg")
    # msg = parse_message_file("geometry_msgs", "Transform.msg")
    print(msg)

    # c, p = find_context_pkg("Transform")
    # print(p)

    # field_names = get_field_names(pkg_name="geometry_msgs", path="/opt/ros/humble/share", name="Transform")
    # print(field_names)

if __name__ == "__main__":
    main()