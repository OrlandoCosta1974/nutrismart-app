import streamlit as st
from openai import OpenAI
from fpdf import FPDF
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="NutriSmart AI", layout="centered", page_icon="🥗")

# --- CSS (Visual Limpo) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #051c10 0%, #0d3321 100%); font-family: 'Segoe UI', sans-serif; }
    h1 { color: #00e676 !important; text-align: center; }
    .stButton>button { background: linear-gradient(90deg, #00c853 0%, #00e676 100%); color: #003300; font-weight: 800; border: none; height: 3em; width: 100%; border-radius: 10px; }
    .stTextArea textarea { background-color: #f1f8e9; color: #1b5e20; border: 2px solid #00c853; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM GROQ (NUVEM) ---
# O Streamlit vai buscar a chave nos "Segredos" do servidor
api_key = st.secrets["GROQ_API_KEY"]

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

# --- CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_draw_color(0, 150, 50)
        self.set_line_width(0.5)
        self.set_font('Arial', 'B', 22)
        self.set_text_color(0, 100, 30)
        self.cell(0, 10, 'NUTRI SMART CLINIC', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'Gerado via NutriSmart AI (Groq Cloud)', 0, 0, 'C')

# --- LÓGICA ---
def gerar_dieta_ia(texto_entrada):
    prompt = f"""
    VOCÊ É UM NUTRICIONISTA BRASILEIRO.
    Crie um Plano Alimentar em Português do Brasil.
    Use medidas caseiras (colher, xícara).
    
    ESTRUTURA:
    1. DIAGNÓSTICO (IMC e Calorias)
    2. ESTRATÉGIA
    3. PLANO ALIMENTAR (Café, Almoço, Lanche, Jantar)
    4. DICAS
    
    PACIENTE: "{texto_entrada}"
    """
    try:
        response = client.chat.completions.create(
            # Usando Llama 3.3 Versátil (Rápido e Inteligente)
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na Nuvem: {e}"

def criar_pdf_nutri(texto_dieta):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    linhas = texto_dieta.split('\n')
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            pdf.ln(2)
            continue
        try:
            linha_limpa = linha.encode('latin-1', 'replace').decode('latin-1')
        except:
            linha_limpa = linha
            
        if (linha[0].isdigit() and linha[1] == '.') or (linha.isupper() and len(linha) < 40):
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 128, 64)
            pdf.ln(4)
            pdf.cell(0, 8, txt=linha_limpa, ln=True)
        else:
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 5, txt=linha_limpa)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE ---
st.title("NUTRI SMART ONLINE ☁️")

if 'texto_paciente' not in st.session_state:
    st.session_state['texto_paciente'] = ""

texto_final = st.text_area(
    "Dados do Paciente:", 
    value=st.session_state['texto_paciente'], 
    height=200,
    placeholder="Nome, Idade, Peso, Altura, Objetivo, Restrições..."
)

if st.button("📝 GERAR DIETA (NUVEM)"):
    if texto_final:
        with st.spinner("A IA da Groq está calculando... (É muito rápido!)"):
            conteudo = gerar_dieta_ia(texto_final)
            with st.expander("Ver Dieta", expanded=True):
                st.write(conteudo)
            pdf_bytes = criar_pdf_nutri(conteudo)
            st.download_button("📥 BAIXAR PDF", data=pdf_bytes, file_name="Dieta.pdf", mime="application/pdf")
    else:
        st.warning("Preencha os dados.")
