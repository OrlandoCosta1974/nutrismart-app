import streamlit as st
from openai import OpenAI
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="NutriSmart AI - Full Strategy", layout="centered", page_icon="🥗")

# --- 2. CSS (ESTILIZAÇÃO) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #051c10 0%, #0d3321 100%); font-family: 'Segoe UI', sans-serif; }
    h1 { color: #00e676 !important; text-align: center; font-weight: 700; }
    .stButton>button { background: linear-gradient(90deg, #00c853 0%, #00e676 100%); color: #003300; font-weight: 800; border: none; height: 3.5em; width: 100%; border-radius: 12px; }
    .stTextArea textarea { background-color: #ffffff !important; color: #000000 !important; caret-color: #000000 !important; border: 2px solid #00c853; border-radius: 8px; font-size: 16px; }
    .stTextArea textarea::placeholder { color: #a0a0a0 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO NUVEM ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Erro: Chave API não configurada.")
    st.stop()

client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)

# --- 4. CLASSE PDF PROFISSIONAL ---
class PDF(FPDF):
    def header(self):
        self.set_draw_color(0, 150, 50)
        self.set_line_width(0.8)
        self.set_font('Arial', 'B', 22)
        self.set_text_color(0, 100, 30)
        self.cell(0, 10, 'NUTRI SMART CLINIC', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Plano Alimentar e Guia de Treino Personalizado', 0, 1, 'C')
        self.ln(5)
        self.line(10, 32, 200, 32)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Este plano e orientacoes sao gerados por IA. Consulte profissionais de saude.', 0, 0, 'C')

# --- 5. LÓGICA IA (PROMPT COM TREINO E ESTRATÉGIA) ---
def gerar_dieta_ia(texto_entrada):
    prompt = f"""
    VOCÊ É UM NUTRICIONISTA E PREPARADOR FÍSICO BRASILEIRO.
    
    TAREFA: Gerar um plano completo de emagrecimento.
    
    ESTRUTURA OBRIGATÓRIA DO PDF:
    
    PACIENTE: [Nome]
    
    1. DIAGNÓSTICO METABÓLICO
    - IMC: [Valor] - [Classificação de Obesidade e Grau]
    - Gasto Energético: [Valor] kcal
    
    2. ESTRATÉGIAS PARA EMAGRECIMENTO
    - [Liste 3 a 4 estratégias claras: ex: Déficit Calórico, Proteínas, Hidratação, Sono]
    
    3. PLANO ALIMENTAR (DIRETO AO PONTO)
    - CAFÉ DA MANHÃ (Opções)
    - ALMOÇO (Opções)
    - LANCHE (Opções)
    - JANTAR (Opções)
    
    4. RECOMENDAÇÕES DE TREINO
    - [Sugira tipos de exercícios de acordo com a idade e peso do paciente]
    - [Frequência semanal sugerida]
    - [Dicas de segurança para evitar lesões]

    DADOS: "{texto_entrada}"
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro: {e}"

# --- 6. GERADOR DE PDF ---
def criar_pdf_nutri(texto_dieta):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    linhas = texto_dieta.split('\n')
    for linha in linhas:
        linha = linha.strip().replace('*', '')
        if not linha:
            pdf.ln(2)
            continue
        
        try:
            linha_limpa = linha.encode('latin-1', 'replace').decode('latin-1')
        except:
            linha_limpa = linha

        # Destaque PACIENTE
        if "PACIENTE:" in linha_limpa.upper():
            pdf.set_font("Arial", 'B', 14)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, txt=linha_limpa, ln=True)
            pdf.ln(2)
            
        # Títulos Principais (1., 2., 3., 4.)
        elif (linha[0].isdigit() and linha[1] == '.') or (linha.isupper() and len(linha) < 45):
            pdf.ln(4)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 100, 0)
            pdf.cell(0, 8, txt=linha_limpa, ln=True)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.ln(2)
            
        # Refeições
        elif any(x in linha.upper() for x in ["CAFÉ", "ALMOÇO", "JANTA", "LANCHE"]):
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(0, 128, 64)
            pdf.ln(1)
            pdf.cell(0, 6, txt=linha_limpa, ln=True)
            
        # Listas e Conteúdo
        else:
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 5, txt=linha_limpa)
            
    return pdf.output(dest='S').encode('latin-1')

# --- 7. INTERFACE ---
st.title("NUTRI SMART CLOUD 🥗")

placeholder_text = "Nome:\nIdade:\nPeso:\nAltura:\nObjetivo:\nRestrições:"

texto_usuario = st.text_area(
    "Dados para a Ficha:", 
    height=200,
    placeholder=placeholder_text
)

if st.button("🚀 GERAR PLANO COMPLETO"):
    if texto_usuario:
        with st.spinner("IA calculando dieta e recomendações de treino..."):
            conteudo = gerar_dieta_ia(texto_usuario)
            with st.expander("Prévia"):
                st.write(conteudo)
            pdf_bytes = criar_pdf_nutri(conteudo)
            st.download_button("📥 BAIXAR PDF PROFISSIONAL", data=pdf_bytes, file_name="Plano_Elite_NutriSmart.pdf")
    else:
        st.warning("Preencha os dados do paciente.")
