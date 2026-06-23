import os
import urllib.request
from fpdf import FPDF

# 🤖 AUTO FONT DOWNLOADER
def download_math_font():
    font_path = "DejaVuSans.ttf"
    font_url = "https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/master/ttf/DejaVuSans.ttf"
    
    # Agar app ke background mein font nahi hai, toh download karega
    if not os.path.exists(font_path):
        try:
            urllib.request.urlretrieve(font_url, font_path)
        except Exception as e:
            pass
    return font_path

class PaathsalaPDF(FPDF):
    def __init__(self, target_class, subject, topic):
        super().__init__()
        self.target_class = target_class
        self.subject = subject
        self.topic = topic
        
        # Setup DejaVu Font for math symbols
        self.font_path = download_math_font()
        if os.path.exists(self.font_path):
            self.add_font('DejaVu', '', self.font_path)

    def header(self):
        try:
            self.image('watermark.png', x=30, y=60, w=150)
        except:
            pass
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'Class: {self.target_class} | Subject: {self.subject}', ln=1)
        self.set_y(10)
        self.set_font('Arial', 'B', 18)
        self.cell(0, 8, 'PAATHSALA PRIVATE TUITIONS', align='C', ln=1)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 8, self.topic.upper() + ' (DPP)', align='C', ln=1)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'B', 9)
        self.cell(0, 10, '+91 8116230505 | Raniganj Only', align='C')

def create_pdf_from_json(dpp_data, filename="Paathsala_DPP.pdf"):
    header_info = dpp_data['header']
    pdf = PaathsalaPDF(target_class=header_info['class'], subject=header_info['subject'], topic=header_info['topic'])
    pdf.add_page()
    
    # Section A (MCQs) - Headings ke liye purana Arial
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Section A: Multiple Choice Questions', ln=1)
    
    # 👇 Questions ke liye Naya Math Font (DejaVu) laga rahe hain 👇
    if os.path.exists(pdf.font_path):
        pdf.set_font('DejaVu', '', 11)
    else:
        pdf.set_font('Arial', '', 11)
        
    for q in dpp_data['section_a']:
        pdf.multi_cell(0, 6, f"{q['q_no']}. {q['question']}")
        pdf.cell(90, 6, f"a) {q['options']['a']}")
        pdf.cell(90, 6, f"b) {q['options']['b']}", ln=1)
        pdf.cell(90, 6, f"c) {q['options']['c']}")
        pdf.cell(90, 6, f"d) {q['options']['d']}", ln=1)
        pdf.ln(4)
        
    pdf.output(filename)
    return filename
