from bs4 import BeautifulSoup
import logging


class PythonTag:
    def __init__(self, tag, document, g={}):
        self.tag = tag
        self.document = document
        self.globals = {"this": self, **g}
    
    def echo(self, tag, content, attr, parent=None):
        tag = self.document.new_tag(tag)
        tag.attrs = attr
        tag.string = content
        self.tag.insert_before(tag)
        return tag

    def execute(self):
        contents = str(self.tag.decode_contents())
        fixed_content = []
        ident = ""

        lines = contents.split("\n")

        if len(lines) > 1:
            index = 1
        else: 
            index = 0

        for i in lines[index]:
            if i in [" ", "\t"]:
                ident += i
            else:
                break

        for line in lines:
            fixed_content.append(line.removeprefix(ident))
        fixed_content = "\n".join(fixed_content)

        exec(fixed_content, self.globals)
        self.tag.extract()


def eval_document(document, shared_global={}):
    logging.debug("Parsing HTML document")
    soup = BeautifulSoup(document, "html.parser")
    for tag in soup.find_all("python"):
        wrapped_tag = PythonTag(tag, soup, shared_global)
        wrapped_tag.execute()
    return soup.prettify()
