from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_resume():
    # Ye file 'my_resume.pdf' naam se banayega jo app.py khoj raha hai
    c = canvas.Canvas("my_resume.pdf", pagesize=letter)
    c.drawString(100, 750, "Rahul Sharma - Backend Developer")
    c.drawString(100, 730, "Skills: Python, SQL, FastAPI, Git, Docker")
    c.drawString(100, 710, "Experience: 3 years building scalable microservices.")
    c.drawString(100, 690, "Projects: Integrated REST APIs and optimized database queries.")
    c.save()
    print("Sahi hai! 'my_resume.pdf' successfully ban gayi hai.")

create_sample_resume()