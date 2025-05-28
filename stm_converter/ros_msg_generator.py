from jinja2 import Environment, FileSystemLoader
import importlib.resources as pkg_resources
import stm_converter

class ROSMsgGenerator:
    def __init__(self, structs_found):
        pathToTemplates = pkg_resources.files(stm_converter) / "resources/jinja_templates"
        self.env_ = Environment(loader=FileSystemLoader(pathToTemplates))
        self.structs_found_ = structs_found
        # template = None

    def gen_msgs(self):
        template = self.env_.get_template("multi_struct.txt")
        context = {"data_json": self.structs_found_}

        for msg in self.structs_found_.items():
            filename = f"{msg[0]}.msg"
            context = {"msg": msg[1]}

            with open(filename, mode="w", encoding="utf-8") as output:
                output.write(template.render(context))