import PyPDF2
'''
pdf = open('1.pdf', 'rb')
pdfreader = PyPDF2.PdfFileReader(pdf)
x = pdfreader.numPages
pageobj = pdfreader.getPage(100)
text = pageobj.extractText()
print(text)
file1 = open(r"dictionary.txt", 'a')
file1.writelines(text)
file1.close()
'''
with open('1.pdf', 'rb') as f:
    pdf = PyPDF2.PdfFileReader(f)
    page = pdf.getPage(10)
    print(page)
    text = page.extractText()
    print(text)