from bs4 import BeautifulSoup
import logging


class PythonTag:
    def __init__(self, tag, document, g={}):
        self.tag = tag
        self.document = document
        self.globals = {"this": self, **g}
    
    def echo(self, tag, content, attr):
        tag = self.document.new_tag(tag)
        tag.attrs = attr
        tag.string = content
        self.tag.insert_before(tag)
    
    def execute(self):
        exec(str(self.tag.decode_contents()), self.globals)
        self.tag.extract()
    
def eval_document(document, shared_global={}):
    logging.debug("Parsing HTML document")
    soup = BeautifulSoup(document, "html.parser")
    for tag in soup.find_all("python"):
        wrapped_tag = PythonTag(tag, soup, shared_global)
        wrapped_tag.execute()
    return soup.prettify()