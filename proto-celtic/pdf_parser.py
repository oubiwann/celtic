#!/usr/bin/env python2.7
from collections import defaultdict
from cStringIO import StringIO  
import sys

from pdfminer.converter import LTChar, TextConverter    #<-- changed
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFDocument, PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter


def pdf_to_csv(filename):

    class TabbedConverter(TextConverter):
        def __init__(self, *args, **kwargs):
            TextConverter.__init__(self, *args, **kwargs)

        def end_page(self, i):
            lines = defaultdict(lambda : {})
            children = []
            if hasattr(self.cur_item, "_objs"):
                children = self.cur_item._objs
            for child in children:
                if child and isinstance(child, LTChar):
                    (_,_,x,y) = child.bbox                   
                    line = lines[int(-y)]
                    line[x] = child.get_text().encode(self.codec)

            for y in sorted(lines.keys()):
                line = lines[y]
                text = "".join(line[x] for x in sorted(line.keys()))
                if text.startswith("*"):
                    text = text.ljust(40, " ")
                elif text.startswith("Proto-Celtic"):
                    continue
                elif "of 103" in text:
                    continue
                else:
                    text += "\n"
                self.outfp.write(text)

    rsrc = PDFResourceManager()
    outfp = StringIO()
    device = TabbedConverter(rsrc, outfp, codec="utf-8", laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrc, device)

    doc = PDFDocument()
    fp = open(filename, 'rb')
    parser = PDFParser(fp)       
    parser.set_document(doc)     
    doc.set_parser(parser)       
    doc.initialize('')

    #for i, page in enumerate(list(doc.get_pages())[0:1]):
    for i, page in enumerate(doc.get_pages()):
        if page is not None:
            interpreter.process_page(page)
    device.close()
    fp.close()

    return outfp.getvalue()


filename = "ProtoCelticEnglishWordlist.pdf"
if len(sys.argv) > 1:
    filename = sys.argv[1]
print pdf_to_csv(filename)
