import streamlit as st
from openai import OpenAI
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="NutriSmart AI - Single Page", layout="centered", page_icon="🥗")

# --- 2. CSS (ESTILIZAÇÃO) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #051c10 0%, #0d3321 100%); font-family: 'Segoe UI', sans-serif; }
    h1 { color: #00e676 !important; text-align: center; font-weight: 700; margin-bottom: 0px; }
    .stButton>button { background: linear-gradient(90deg, #00c853 0%, #00e676 100%); color: #003300; font-weight: 800; border: none; height: 3em; width: 100%; border-radius: 10px; }
    .stTextArea textarea { background-color: #ffffff !important; color: #000000 !important; caret-color: #000000 !important; border: 2px solid #00c853; border-radius: 8px; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO NUVEM ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Erro: Chave API não configurada.")
    st.stop()

client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)

# --- 4. CLASSE PDF COMPACTA (1 PÁGINA) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 100, 30)
        self.cell(0, 8, 'NUTRI SMART CLINIC', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 4, 'Plano Alimentar e Guia de Treino Compacto', 0, 1, 'C')
        self.set_draw_color(0, 150, 50)
        self.line(10, 24, 200, 24)
        self.ln(5)

    def footer(self):
        self.set_y(-10)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'Documento Informativo - NutriSmart Cloud.', 0, 0, 'C')

# --- 5. LÓGICA IA (PROMPT CONCISO) ---
def gerar_dieta_ia(texto_entrada):
    prompt = f"""
    VOCÊ É UM NUTRICIONISTA E PREPARADOR FÍSICO.
    OBJETIVO: Gerar um plano completo mas MUITO CONCISO para caber em 1 página.
    
    ESTRUTURA:
    PACIENTE: [Nome]
    1. DIAGNÓSTICO: IMC, Grau de Obesidade e Gasto Calórico.
    2. ESTRATÉGIAS: 3 pontos chave.
    3. PLANO ALIMENTAR: Café, Almoço, Lanche, Jantar (apenas 2 opções curtas cada).
    4. TREINO: Sugestão direta de tipo e frequência.

    DADOS: "{texto_entrada}"
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro: {e}"

# --- 6. GERADOR DE PDF ---
def criar_pdf_nutri(texto_dieta):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    
    linhas = texto_dieta.split('\n')
    for linha in linhas:
        linha = linha.strip().replace('*', '')
        if not linha:
            continue # Pula linhas vazias para economizar espaço
        
        try:
            linha_limpa = linha.encode('latin-1', 'replace').decode('latin-1')
        except:
            linha_limpa = linha

        if "PACIENTE:" in linha_limpa.upper():
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, txt=linha_limpa, ln=True)
            
        elif (linha[0].isdigit() and linha[1] == '.') or (linha.isupper() and len(linha) < 40):
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(0, 100, 0)
            pdf.cell(0, 6, txt=linha_limpa, ln=True, fill=False)
            
        elif any(x in linha.upper() for x in ["CAFÉ", "ALMOÇO", "JANTA", "LANCHE"]):
            pdf.set_font("Arial", 'B', 9)
            pdf.set_text_color(0, 128, 64)
            pdf.cell(0, 5, txt=linha_limpa, ln=True)
            
        else:
            pdf.set_font("Arial", size=9)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 4, txt=linha_limpa)
            
    return pdf.output(dest='S').encode('latin-1')

# --- 7. INTERFACE ---
st.title("NUTRI SMART COMPACT 🥗")

placeholder_text = "Nome:\nIdade:\nPeso:\nAltura:\nObjetivo:"

texto_usuario = st.text_area("Dados do Paciente:", height=150, placeholder=placeholder_text)

if st.button("🚀 GERAR PLANO (1 PÁGINA)"):
    if texto_usuario:
        with st.spinner("Otimizando espaço e gerando plano..."):
            conteudo = gerar_dieta_ia(texto_usuario)
            pdf_bytes = criar_pdf_nutri(conteudo)
            st.download_button("📥 BAIXAR PDF 1 PÁGINA", data=pdf_bytes, file_name="Plano_Compacto_NutriSmart.pdf")
            st.success("Plano gerado com foco em concisão!")
    else:
        st.warning("Preencha os dados.")
