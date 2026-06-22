from xml.dom.minidom import Document
class PDFParseError(Exception):
    """PDF文件解析失败"""
    pass
import fitz #pymupdf
import re
#pdf本地加载解析
def parse_local_pdf(file_path:str):
    try:
        pdf=fitz.open(file_path)
    except FileNotFoundError as e:
        raise  Exception ("未能正确打开文件")
    text=""
    try:
        for page in pdf:
            text +=page.get_text()
        pdf.close()
        cleaned_text = re.sub(r'(?<=[\u4e00-\u9fa5])\n(?=[\u4e00-\u9fa5])', '', text)
        return cleaned_text
    except PDFParseError as e:
        raise PDFParseError(f"pdf解析失败:{e}")
