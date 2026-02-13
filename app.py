import streamlit as st
from openai import OpenAI
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="NutriSmart AI - Elite", layout="centered", page_icon="🥗")

# --- 2. CSS (Visual Limpo e Moderno) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #051c10 0%, #0d3321 100%); font-family: 'Segoe UI', sans-serif; }
    h1 { color: #00e676 !important; text-align: center; font-weight: 700; letter-spacing: 1px; }
    .stButton>button { background: linear-gradient(90deg, #00c853 0%, #00e676 100%); color: #003300; font-weight: 800; border: none; height: 3.5em; width: 100%; border-radius: 12px; text-transform: uppercase; box-shadow: 0 4px 15px rgba(0, 230, 118, 0.4); transition: all 0.3s; }
    .stButton>button:hover { transform: scale(1.02); filter: brightness(1.1); }
    .stTextArea textarea { background-color: #f1f8e9; color: #1b5e20; border: 2px solid #00c853; border-radius: 8px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO NUVEM (GROQ) ---
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
        self.set_font('Arial', 'B', 24)
        self.set_text_color(0, 100, 30)
        self.cell(0, 10, 'NUTRI SMART CLINIC', 0, 1, 'C')
        self.set_font('Arial', 'I', 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Planejamento Alimentar & Estratégia Metabólica', 0, 1, 'C')
        self.ln(5)
        self.line(10, 32, 200, 32)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Gerado via NutriSmart Cloud - Consulte seu médico.', 0, 0, 'C')

# --- 5. LÓGICA IA (PROMPT RIGIDO) ---
def gerar_dieta_ia(texto_entrada):
    prompt = f"""
    VOCÊ É UM NUTRICIONISTA DE ELITE.
    OBJETIVO: Gerar um plano alimentar visualmente limpo e direto.
    
    REGRAS VISUAIS (IMPORTANTE):
    1. NÃO use frases introdutórias (Ex: "Aqui está o plano", "Com base no peso"). VÁ DIRETO AOS DADOS.
    2. Use listas com marcadores (-) para opções.
    3. Use APENAS Português BR.
    
    ESTRUTURA OBRIGATÓRIA:
    1. DIAGNÓSTICO
    - Perfil: [Resumo]
    - IMC: [Valor] ([Classificação])
    - Gasto Calórico Basal: [Valor] kcal (Estimativa)
    
    2. ESTRATÉGIA
    - [Descreva a estratégia em bullets curtos]
    
    3. PLANO ALIMENTAR
    CAFÉ DA MANHÃ:
    - Opção 1: [Alimentos e quantidades caseiras]
    - Opção 2: [Alimentos e quantidades caseiras]
    
    ALMOÇO:
    - Opção 1: [Alimentos e quantidades caseiras]
    - Opção 2: [Alimentos e quantidades caseiras]
    
    LANCHE DA TARDE:
    - Opção 1: [Alimentos e quantidades caseiras]
    - Opção 2: [Alimentos e quantidades caseiras]
    
    JANTAR:
    - Opção 1: [Alimentos e quantidades caseiras]
    - Opção 2: [Alimentos e quantidades caseiras]
    
    4. SUPLEMENTAÇÃO E DICAS
    - [Lista curta de dicas]

    PACIENTE: "{texto_entrada}"
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2 # Baixa temperatura para seguir a estrutura rigidamente
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro IA: {e}"

# --- 6. GERADOR DE PDF VISUAL ---
def criar_pdf_nutri(texto_dieta):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    linhas = texto_dieta.split('\n')
    for linha in linhas:
        linha = linha.strip().replace('*', '') # Limpa asteriscos do markdown
        if not linha:
            pdf.ln(2)
            continue
        
        try:
            linha_limpa = linha.encode('latin-1', 'replace').decode('latin-1')
        except:
            linha_limpa = linha

        # DETECÇÃO INTELIGENTE DE FORMATAÇÃO
        
        # 1. Títulos Principais (1., 2., 3...)
        if (linha[0].isdigit() and linha[1] == '.') or (linha.isupper() and len(linha) < 40 and "OPÇÃO" not in linha):
            pdf.ln(4)
            pdf.set_font("Arial", 'B', 14)
            pdf.set_text_color(0, 100, 0) # Verde Escuro
            pdf.cell(0, 8, txt=linha_limpa, ln=True)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 100, pdf.get_y()) # Linha curta abaixo
            pdf.ln(2)
            
        # 2. Refeições (Café, Almoço...)
        elif any(x in linha.upper() for x in ["CAFÉ", "ALMOÇO", "JANTA", "LANCHE"]) and len(linha) < 50:
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 128, 64) # Verde Médio
            pdf.cell(0, 6, txt=linha_limpa, ln=True)
            
        # 3. Opções e Itens (Começam com -)
        elif linha.startswith("-") or linha.startswith("•"):
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(50, 50, 50)
            pdf.set_x(15) # Recuo para direita (Indentação)
            pdf.multi_cell(0, 5, txt=linha_limpa)
            
        # 4. Texto Normal
        else:
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(40, 40, 40)
            pdf.set_x(10)
            pdf.multi_cell(0, 5, txt=linha_limpa)
            
    return pdf.output(dest='S').encode('latin-1')

# --- 7. INTERFACE ---
st.title("NUTRI SMART ONLINE ☁️")
st.markdown('<p style="text-align:center; color:#a3d9c5;">Planejamento Dietético Profissional</p>', unsafe_allow_html=True)

if 'texto_paciente' not in st.session_state:
    st.session_state['texto_paciente'] = ""

with st.container():
    texto_final = st.text_area(
        "Informações do Paciente:", 
        value=st.session_state['texto_paciente'], 
        height=200,
        placeholder="Ex: Carlos, 45 anos, 90kg, 1.80m. Objetivo: Perda de peso. Restrição: Lactose."
    )
    if texto_final != st.session_state['texto_paciente']:
        st.session_state['texto_paciente'] = texto_final

st.write("")
if st.button("📝 GERAR PROTOCOLO ALIMENTAR"):
    if texto_final:
        with st.spinner("Processando dados metabólicos..."):
            conteudo = gerar_dieta_ia(texto_final)
            with st.expander("Ver Prévia", expanded=True):
                st.write(conteudo)
            pdf_bytes = criar_pdf_nutri(conteudo)
            st.download_button("📥 BAIXAR PDF FINAL", data=pdf_bytes, file_name=f"Dieta_{datetime.now().strftime('%d%m')}.pdf", mime="application/pdf")
    else:
        st.warning("⚠️ Preencha os dados do paciente.")

