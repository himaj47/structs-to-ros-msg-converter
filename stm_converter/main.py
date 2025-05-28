import argparse
from stm_converter.xml_parser import xmlParser
from stm_converter.ros_msg_generator import ROSMsgGenerator

def main():
    desc = "create simple file based on command line arguments"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("filename", help="header file")
    parser.add_argument("-ns", "--namespace", help="namespace")

    args = parser.parse_args()

    print(f"file name = {args.filename}")

    namespace = ""

    if args.namespace:
        print(f"main.py - namespace = {namespace}")
        namespace = args.namespace

    xml_parser = xmlParser(str(args.filename), namespace)
    structs_found = xml_parser.get_decls()

    msg_gen = ROSMsgGenerator(structs_found)
    msg_gen.gen_msgs()

    print("main.py - successfully generated ros msg files")

if __name__ == "__main__":
    main()
