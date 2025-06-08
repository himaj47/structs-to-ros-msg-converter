from pygccxml import utils
from pygccxml import declarations
from pygccxml import parser
# from rosidl_parser.definition import 
from stm_converter.message_specification import MessageSpecification, BasicType, Field, BASIC_TYPES

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
        msg = MessageSpecification("msg")
        not_primitive_type = []
        for decl in self.ns.declarations:
            # if decl.name == "MyConfigData":
            # if isinstance(decl, declarations.opaque_type_t):
            #     print("opaque")
            if isinstance(decl, declarations.class_t):
                # print(f"declaration name = {decl.name}")
                if str(decl.name).startswith("_"): continue
                # print(f"decl type = {decl.decl_type}")
                # MyConfigData = decl
                temp = {decl.name: {}}
                # self.struct_name = decl.name
                msg.msg_name_ = decl.name.title()
                msg.struct_name_ = decl.name

                for var in decl.variables():
                    # print(decl.variables())
                    # print("decl_name: " + decl.name)
                    # print("My name is: " + var.name)
                    # print("My type is: " + str(var.decl_type))
                    var_type = ""
                    field = None

                    # use isinstance() instead of type()
                    if type(var.decl_type) == declarations.cpptypes.int_t:
                        # declarations.is_integral(var.decl_type)
                        var_type = "int64"
                        field = Field(var.name, BasicType('int64'))
                    elif type(var.decl_type) == declarations.cpptypes.float_t:
                        var_type = "float64"
                        field = Field(var.name, BasicType('float64'))
                    elif type(var.decl_type) == declarations.cpptypes.bool_t:
                        var_type = "bool"
                        field = Field(var.name, BasicType('bool'))
                    elif str(var.decl_type).startswith("std::vector<"):
                        var_type = str(var.decl_type).strip("std::vector<").strip(">")
                        if var_type+'64' in BASIC_TYPES:
                            field = Field(var.name, BasicType(var_type+'64'), is_array=True)
                            var_type += "64[]"
                        else:
                            # assuming it to be namespaced typed
                            field = Field(var.name, BasicType(var_type), is_array=True)
                            var_type += "[]"

                    else:
                        print(f"weird type found - {var.decl_type}")

                    # print(type(var.decl_type))
                    temp[decl.name].update({var.name: var_type})
                    msg.set_field(field)

                self.structs.update(temp)

        # print(f"structs_found = {self.structs}")
        return self.structs, msg