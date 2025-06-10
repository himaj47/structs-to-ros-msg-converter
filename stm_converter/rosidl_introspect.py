from rosidl_adapter.parser import MessageSpecification, Type, Field

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


def parse_msg_struct(msg_struct: dict):
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


def main():
    msg_struct = {"point_msg": {"x": "int64", "y": "int64", "z": "int64"}}
    msg = parse_msg_struct(msg_struct)
    print(msg)

if __name__ == "__main__":
    main()