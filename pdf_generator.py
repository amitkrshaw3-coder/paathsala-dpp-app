import os
import urllib.request
import tempfile
from fpdf import FPDF

# 🤖 ROBUST FONT DOWNLOADER (With VIP Mask)
def download_math_font():
    # Streamlit ke temporary folder mein save karenge taaki permission ka error na aaye
    temp_dir = tempfile.gettempdir()
    font_path = os.path.join(temp_dir, "DejaVuSans.ttf")
    font_url = "https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/master/ttf/DejaVuSans.ttf"
    
    if not os.path.exists(font_path):
        try:
            # VIP Mask taaki GitHub block na kare
            req = urllib.request.Request(font_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(font_path, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as e:
            pass
    return font_path

# 🛡️ SAFETY NET: Agar font nahi mila, toh symbols ko English me badal do taaki crash na ho
def clean_text(text, font_loaded):
    if font_loaded:
        return text
    replacements = {"∫": "Integral of ", "²": "^2", "³": "^3", "θ": "theta", "π": "pi", "α": "alpha", "β": "beta"}
    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)
    return text

class PaathsalaPDF(FPDF):
    def __init__(self, target_class, subject, topic):
        super().__init__()
        self.target_class = target_class
        self.subject = subject
        self.topic = topic
        
        # Font setup
        self.font_path = download_math_font()
        self.font_loaded = False
        if os.path.exists(self.font_path):
            try:
                self.add_font('DejaVu', '', self.font_path)
                self.font_loaded = True
            except:
                pass

    def header(self):
        try:
            self.image('watermark.png', x=30, y=60, w=150)
        except:
            pass
        self.set_font('helvetica', '', 10)
        self.cell(0, 5, f'Class: {self.target_class} | Subject: {self.subject}', ln=1)
        self.set_y(10)
        self.set_font('helvetica', 'B', 18)
        self.cell(0, 8, 'PAATHSALA PRIVATE TUITIONS', align='C', ln=1)
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 8, self.topic.upper() + ' (DPP)', align='C', ln=1)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'B', 9)
        self.cell(0, 10, '+91 8116230505 | Raniganj Only', align='C')

def create_pdf_from_json(dpp_data, filename="Paathsala_DPP.pdf"):
    header_info = dpp_data['header']
    pdf = PaathsalaPDF(target_class=header_info['class'], subject=header_info['subject'], topic=header_info['topic'])
    pdf.add_page()
    
    # Section A Heading
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, 'Section A: Multiple Choice Questions', ln=1)
    
    # Naya math font set karna
    if pdf.font_loaded:
        pdf.set_font('DejaVu', '', 11)
    else:
        pdf.set_font('helvetica', '', 11)
        
    for q in dpp_data['section_a']:
        # Agar font nahi hai, toh yeh text ko clean kar dega, par error nahi aane dega
        q_text = clean_text(f"{q['q_no']}. {q['question']}", pdf.font_loaded)
        opt_a = clean_text(f"a) {q['options']['a']}", pdf.font_loaded)
        opt_b = clean_text(f"b) {q['options']['b']}", pdf.font_loaded)
        opt_c = clean_text(f"c) {q['options']['c']}", pdf.font_loaded)
        opt_d = clean_text(f"d) {q['options']['d']}", pdf.font_loaded)
        
        pdf.multi_cell(0, 6, q_text)
        pdf.cell(90, 6, opt_a)
        pdf.cell(90, 6, opt_b, ln=1)
        pdf.cell(90, 6, opt_c)
        pdf.cell(90, 6, opt_d, ln=1)
        pdf.ln(4)
        
    pdf.output(filename)
    return filename
