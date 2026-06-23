from fpdf import FPDF

class PaathsalaPDF(FPDF):
    def __init__(self, target_class, subject, topic):
        super().__init__()
        self.target_class = target_class
        self.subject = subject
        self.topic = topic

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
    
    # Section A (MCQs)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Section A: Multiple Choice Questions', ln=1)
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
