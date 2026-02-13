import streamlit as st
from openai import OpenAI
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="NutriSmart AI - Elite", layout="centered", page_icon="🥗")

# --- 2. CSS (CURSOR PRETO + TEXTO ORIENTADOR) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #051c10 0%, #0d3321 100%); font-family: 'Segoe UI', sans-serif; }
    h1 { color: #00e676 !important; text-align: center; font-weight: 700; }
    
    .stButton>button { 
        background: linear-gradient(90deg, #00c853 0%, #00e676 100%); 
        color: #003300; font-weight: 800; border: none; height: 3.5em; width: 100%; border-radius: 12px;
    }

    /* Caixa de Texto com Placeholder Cinza */
    .stTextArea textarea { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        caret-color: #000000 !important; 
        border: 2px solid #00c853; 
        border-radius: 8px; 
        font-size: 16px;
    }
    
    /* Estilizando o texto de exemplo (placeholder) */
    .stTextArea textarea::placeholder {
        color: #a0a0a0 !important;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO NUVEM ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Erro: Chave API não configurada.")
    st.stop()

client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)

# --- 4. CLASSE PDF ELITE ---
class PDF(FPDF):
    def header(self):
        self.set_draw_color(0, 150, 50)
        self.set_line_width(0.8)
        self.set_font('Arial', 'B', 22)
        self.set_text_color(0, 100, 30)
        self.cell(0, 10, 'NUTRI SMART CLINIC', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Relatório de Performance Alimentar', 0, 1, 'C')
        self.ln(5)
        self.line(10, 32, 200, 32)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Documento gerado por IA - NutriSmart Cloud.', 0, 0, 'C')

# --- 5. LÓGICA IA (PROMPT PARA NOME E OBESIDADE) ---
def gerar_dieta_ia(texto_entrada):
    prompt = f"""
    VOCÊ É UM NUTRICIONISTA ESPORTIVO E CLÍNICO.
    
    TAREFA: Gerar um plano alimentar focado no paciente abaixo.
    
    REGRAS CRÍTICAS:
    1. IDENTIFIQUE O NOME: Comece o PDF com "PACIENTE: [NOME ENCONTRADO]".
    2. DIAGNÓSTICO OBRIGATÓRIO: Calcule o IMC e descreva explicitamente o grau de obesidade (Grau I, II ou III/Mórbida) se for o caso.
    3. SEM CONVERSA FIADA: Vá direto aos títulos e listas.
    
    ESTRUTURA:
    PACIENTE: [Nome]
    
    1. AVALIAÇÃO METABÓLICA
    - IMC: [Valor] - [Classificação/Grau]
    - Gasto Energético: [Valor] kcal
    
    2. PLANO ALIMENTAR (CAFÉ, ALMOÇO, LANCHE, JANTAR com opções)
    
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

        # Destaque para o Nome do Paciente no início
        if "PACIENTE:" in linha_limpa.upper():
            pdf.set_font("Arial", 'B', 14)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, txt=linha_limpa, ln=True)
            pdf.ln(2)
        # Títulos
        elif (linha[0].isdigit() and linha[1] == '.') or (linha.isupper() and len(linha) < 40):
            pdf.ln(4)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 100, 0)
            pdf.cell(0, 8, txt=linha_limpa, ln=True)
            pdf.ln(1)
        # Refeições
        elif any(x in linha.upper() for x in ["CAFÉ", "ALMOÇO", "JANTA", "LANCHE"]):
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(0, 128, 64)
            pdf.ln(2)
            pdf.cell(0, 6, txt=linha_limpa, ln=True)
        # Itens
        else:
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 5, txt=linha_limpa)
            
    return pdf.output(dest='S').encode('latin-1')

# --- 7. INTERFACE ---
st.title("NUTRI SMART CLOUD 🥗")

# Placeholder com o roteiro que você pediu
placeholder_text = "Nome:\nIdade:\nPeso:\nAltura:\nObjetivo:\nRestrições:"

texto_usuario = st.text_area(
    "Dados para a Ficha:", 
    height=200,
    placeholder=placeholder_text
)

if st.button("🚀 GERAR FICHA E PLANO"):
    if texto_usuario:
        with st.spinner("Analisando dados e gerando diagnóstico..."):
            conteudo = gerar_dieta_ia(texto_usuario)
            with st.expander("Prévia do Plano"):
                st.write(conteudo)
            pdf_bytes = criar_pdf_nutri(conteudo)
            st.download_button("📥 BAIXAR PDF PROFISSIONAL", data=pdf_bytes, file_name="Plano_Nutricional.pdf")
    else:
        st.warning("Por favor, preencha os dados do paciente.")
