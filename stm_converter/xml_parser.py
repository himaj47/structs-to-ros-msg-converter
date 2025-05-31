from pygccxml import utils
from pygccxml import declarations
from pygccxml import parser

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
        self.ns = ""
        self.stuct_name = ""

        self.structs = {}

        self.decls = parser.parse([filename], xml_generator_config)
        self.global_namespace = declarations.get_global_namespace(self.decls)
        self.namespaces = self.global_namespace.namespaces()

        if namespace:
            self.ns = self.global_namespace.namespace(namespace)

        else:
            user_ns = None
            for ns in self.namespaces:
                # print(f"namespace = {ns.name}")
                user_ns = ns.name

            self.ns = self.global_namespace.namespace(user_ns)

    def get_decls(self):
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
                self.stuct_name = decl.name

                for var in decl.variables():
                    # print(decl.variables())
                    # print("decl_name: " + decl.name)
                    # print("My name is: " + var.name)
                    # print("My type is: " + str(var.decl_type))
                    var_type = ""

                    if type(var.decl_type) == declarations.cpptypes.int_t:
                        # declarations.is_integral(var.decl_type)
                        var_type = "Int"
                    elif type(var.decl_type) == declarations.cpptypes.float_t:
                        var_type = "Float"
                    elif str(var.decl_type).startswith("std::vector<"):
                        var_type = str(var.decl_type).strip("std::vector<").strip(">") + "[]"

                    # print(type(var.decl_type))
                    temp[decl.name].update({var.name: var_type})

                self.structs.update(temp)

        # print(f"structs_found = {self.structs}")
        return self.structs