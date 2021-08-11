import fitz

def read_pdf(filename):
    doc = fitz.open(filename, stream=filename.read())
    text = ''
    for page in range(doc.page_count):
        current_page = doc.load_page(page)
        text += current_page.get_text('text') # not the best method
    # print(text)
    return text
