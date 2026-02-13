import streamlit as st
from openai import OpenAI
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="NutriSmart AI - Cloud", layout="centered", page_icon="🥗")

# --- 2. CSS PERSONALIZADO (Visual Clínico/Saúde) ---
st.markdown("""
<style>
    /* Fundo Dark Clean */
    .stApp {
        background: linear-gradient(135deg, #051c10 0%, #0d3321 100%);
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Títulos */
    h1 {
        color: #00e676 !important;
        text-align: center;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    /* Botões */
    .stButton>button {
        border-radius: 12px;
        height: 3.5em;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
        width: 100%;
    }
    
    /* Botão Gerar (Verde Brilhante) */
    .stButton>button {
        background: linear-gradient(90deg, #00c853 0%, #00e676 100%);
        color: #003300;
        text-transform: uppercase;
        font-weight: 800;
        box-shadow: 0 4px 15px rgba(0, 230, 118, 0.4);
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        filter: brightness(1.1);
    }
    
    /* Área de Texto */
    .stTextArea textarea {
        background-color: #f1f8e9;
        color: #1b5e20;
        border: 2px solid #00c853;
    }
    
    /* Esconder menus padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO COM A NUVEM (GROQ) ---
# Pega a senha dos "Secrets" do Streamlit
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Erro: Chave da API não encontrada nos Secrets.")
    st.stop()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

# --- 4. CLASSE PDF PROFISSIONAL (Igual ao Local) ---
class PDF(FPDF):
    def header(self):
        # Cor Verde Clínica
        self.set_draw_color(0, 150, 50) 
        self.set_line_width(0.5)
        
        # Logo Texto
        self.set_font('Arial', 'B', 22)
        self.set_text_color(0, 100, 30) # Verde Escuro
        self.cell(0, 10, 'NUTRI SMART CLINIC', 0, 1, 'C')
        
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Planejamento Alimentar Personalizado & Metabólico', 0, 1, 'C')
        
        self.ln(5)
        self.line(10, 30, 200, 30) # Linha divisória elegante
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'Gerado via NutriSmart Cloud - Uso exclusivo para referência.', 0, 0, 'C')

# --- 5. LÓGICA DE INTELIGÊNCIA (GROQ) ---
def gerar_dieta_ia(texto_entrada):
    prompt = f"""
    VOCÊ É UM NUTRICIONISTA CLÍNICO BRASILEIRO DE ELITE.
    
    TAREFA: Criar um Plano Alimentar Completo e Profissional.
    
    REGRAS DE OURO (ANTI-PORTUNHOL):
    1. USE APENAS PORTUGUÊS DO BRASIL.
    2. USE MEDIDAS BRASILEIRAS (colher de sopa, concha, escumadeira, unidade, fatia).
    3. PROIBIDO usar termos em inglês como "cup", "slice", "oz".
    4. Seja técnico mas acolhedor.
    
    ESTRUTURA OBRIGATÓRIA (TÍTULOS NUMERADOS):
    1. DIAGNÓSTICO NUTRICIONAL (IMC e Estimativas)
    2. ESTRATÉGIA DA DIETA
    3. PLANO ALIMENTAR (Café, Almoço, Lanche, Jantar - Com opções)
    4. HIDRATAÇÃO E SUPLEMENTAÇÃO
    5. ORIENTAÇÕES GERAIS
    
    DADOS DO PACIENTE:
    "{texto_entrada}"
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Modelo Rápido e Inteligente da Groq
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# --- 6. GERADOR DE PDF COM FORMATAÇÃO RICA ---
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
        
        # Detecta Títulos (Começa com número e ponto, ou tudo maiúsculo curto)
        eh_titulo = (linha[0].isdigit() and linha[1] == '.') or (linha.isupper() and len(linha) < 50 and len(linha) > 3)
        
        try:
            # Tratamento de caracteres especiais (Acentuação)
            linha_limpa = linha.encode('latin-1', 'replace').decode('latin-1')
        except:
            linha_limpa = linha

        if eh_titulo:
            # Título Verde e Negrito
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 128, 64) # Verde Título
            pdf.ln(6)
            pdf.cell(0, 8, txt=linha_limpa, ln=True)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y()) # Linha fina embaixo do título
            pdf.ln(2)
        else:
            # Texto Comum Cinza Escuro
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 5, txt=linha_limpa)
            
    return pdf.output(dest='S').encode('latin-1')

# --- 7. INTERFACE ---
st.title("NUTRI SMART ONLINE ☁️")
st.markdown('<p style="text-align:center; color:#a3d9c5;">Planejamento Dietético Inteligente (Powered by Groq)</p>', unsafe_allow_html=True)

if 'texto_paciente' not in st.session_state:
    st.session_state['texto_paciente'] = ""

# Layout do Formulário
with st.container():
    texto_final = st.text_area(
        "Anamnese do Paciente:", 
        value=st.session_state['texto_paciente'], 
        height=200,
        placeholder="""Exemplo:
- Nome: Ana Souza
- Idade: 29 anos
- Peso: 70kg | Altura: 1.65m
- Objetivo: Definição muscular
- Restrições: Nenhuma
- Rotina: Treina Crossfit as 18h"""
    )
    if texto_final != st.session_state['texto_paciente']:
        st.session_state['texto_paciente'] = texto_final

st.write("") # Espaço

if st.button("📝 GERAR DIETA PROFISSIONAL (NUVEM)"):
    if texto_final:
        with st.spinner("A IA está calculando macros e montando o cardápio..."):
            conteudo = gerar_dieta_ia(texto_final)
            
            # Mostra na tela (Expander)
            with st.expander("✅ Ver Dieta na Tela", expanded=True):
                st.write(conteudo)
            
            # Gera PDF
            pdf_bytes = criar_pdf_nutri(conteudo)
            
            st.download_button(
                label="📥 BAIXAR PLANO ALIMENTAR (PDF)",
                data=pdf_bytes,
                file_name=f"Dieta_{datetime.now().strftime('%d%m%Y')}.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("⚠️ Por favor, preencha os dados do paciente.")
