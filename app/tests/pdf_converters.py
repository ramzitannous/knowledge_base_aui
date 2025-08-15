import time

import pytesseract
from PIL import Image
from docling_core.transforms.chunker import DocChunk
from haystack import Document
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner, RecursiveDocumentSplitter
from haystack.dataclasses import ByteStream

from app.components.converters.pdf_resource import PDFResourceToDocument
from app.schemas.metadata import FileResourceMetadata

SPLIT_SIZE = 400  # 300 words (approximate)
SPLIT_OVERLAP = 40
SEPARATORS = ["\n\n", "\n", " "]
SPLIT_UNIT = "token"

def print_documents(documents: list[Document]):
    for doc in documents:
        doc_chunk = DocChunk.model_validate(doc.meta["dl_meta"])
        print(f"- text: {doc_chunk.text!r}")
        if doc_chunk.meta.origin:
            print(f"  file: {doc_chunk.meta.origin.filename}")
        if doc_chunk.meta.headings:
            print(f"  section: {' / '.join(doc_chunk.meta.headings)}")
        bbox = doc_chunk.meta.doc_items[0].prov[0].bbox
        print(
            f"  page: {doc_chunk.meta.doc_items[0].prov[0].page_no}, "
            f"bounding box: [{int(bbox.l)}, {int(bbox.t)}, {int(bbox.r)}, {int(bbox.b)}]"
        )
        print("-" * 80)

def check_docling_pdf_converter(enable_ocr=False):
    with open("./app/tests/files/4.pdf", "rb") as f:
        pdf_bytes = f.read()

    streams = [ByteStream(data=pdf_bytes)]
    metadata = FileResourceMetadata(
        filename="4.pdf",
        version=1,
        knowledge_base_id="1234235",
        file_resource_id="14534534",
        s3_key="my_s3_key.pdf"
    )
    converter = PDFResourceToDocument([metadata], enable_ocr)
    t1 = time.time()
    documents = converter.run(streams=streams)["documents"]
    t2 = time.time()
    print(f"total time: {t2 - t1}")
    # print_documents(documents)


def check_py_pdf_converter():
    converter = PyPDFToDocument()
    with open("./app/tests/files/4.pdf", "rb") as f:
        pdf_bytes = f.read()
    streams = [ByteStream(data=pdf_bytes)]
    pdf_cleaner = DocumentCleaner()
    pdf_splitter = RecursiveDocumentSplitter(
        split_length=SPLIT_SIZE,
        split_overlap=SPLIT_OVERLAP,
        separators=SEPARATORS,
        split_unit=SPLIT_UNIT
    )
    pdf_splitter.warm_up()
    t1 = time.time()
    documents = converter.run(sources=streams)["documents"]
    cleaned_documents = pdf_cleaner.run(documents=documents)["documents"]
    split_documents = pdf_splitter.run(documents=cleaned_documents)["documents"]
    t2 = time.time()
    print(f"total time: {t2 - t1}")
    # print_documents(split_documents)


def extract_text_using_textract():
    image = Image.open("./files/img.png")
    extracted_text = pytesseract.image_to_string(image)
    print(extracted_text)


if __name__ == "__main__":
    check_docling_pdf_converter()
    check_docling_pdf_converter(True)
    check_py_pdf_converter()