import argparse
from pathlib import Path
from stm_converter.xml_parser import xmlParser
from stm_converter.ros_msg_generator import ROSMsgGenerator

def main():
    desc = "stm_converter arguments"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("filename", help="header file")
    parser.add_argument("-ns", "--namespace", help="namespace")

    args = parser.parse_args()

    path = Path(str(args.filename))
    filename = path.stem

    namespace = ""

    if args.namespace:
        namespace = args.namespace

    xml_parser = xmlParser(str(args.filename), namespace)
    structs_found = xml_parser.get_decls()
    
    msg_gen = ROSMsgGenerator(structs_found, filename, xml_parser.user_ns)
    msg_gen.gen_msgs()
    msg_gen.gen_type_adapter()

if __name__ == "__main__":
    main()
