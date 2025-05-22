import streamlit as st
from bs4 import BeautifulSoup
import re

# Configuração da página
st.set_page_config(page_title="Extrator de Questões", layout="wide")
st.title("Extrator de Questões de HTML")

st.markdown("""
Cole o código HTML de uma questão de múltipla escolha abaixo e clique em **Extrair**.  
O app retornará:  
- **Cabeçalho da questão** (número e, quando houver, título)  
- **Enunciado da questão**  
- **Alternativas**  
- **Alternativa destacada** (correta)
""")

html_input = st.text_area("HTML da questão", height=450)

if st.button("Extrair"):
    if not html_input.strip():
        st.warning("Por favor, cole o HTML da questão.")
    else:
        soup = BeautifulSoup(html_input, "html.parser")

        # 1) Cabeçalho: primeiro procura <h4 class="modal-title">, senão #QuestionHeader, senão script
        header_info = ""
        # a) modal
        modal_title = soup.select_one(".modal-header h4.modal-title")
        if modal_title:
            txt = modal_title.get_text(strip=True)
            # retira a palavra "Questão"
            header_info = txt[len("Questão"):].strip() if txt.lower().startswith("questão") else txt
        else:
            # b) antigo container
            hdr = soup.select_one(".divQuestao #QuestionHeader")
            if hdr and hdr.get_text(strip=True):
                txt = hdr.get_text(strip=True)
                header_info = txt[len("Questão"):].strip() if txt.lower().startswith("questão") else txt
            else:
                # c) fallback via script
                script_text = " ".join(tag.get_text() for tag in soup.find_all("script"))
                m = re.search(r"preencheHeaderQuestao\((\d+)\)", script_text)
                if m:
                    header_info = m.group(1)

        # 2) Enunciado: todos os <p> dentro de .divQuestao até achar o marcador
        paragraphs = soup.select(".divQuestao > p")
        question_parts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if "Está correto o que se afirma" in text:
                question_parts.append(text)
                break
            if text:
                question_parts.append(text)
        enunciado = "\n\n".join(question_parts)

        # 3) Alternativas e destaque
        alternatives = {}
        highlighted = None
        for div in soup.select(".divQuestao > div"):
            b_tag = div.find("b")
            if b_tag and b_tag.get_text(strip=True).endswith(("A)", "B)", "C)", "D)", "E)")):
                label = b_tag.get_text(strip=True).replace(")", "").strip()
                p_tag = div.find("p")
                alt_text = p_tag.get_text(strip=True) if p_tag else ""
                alternatives[label] = alt_text
                if "alert-success" in div.get("class", []) or div.find(class_="alert-success"):
                    highlighted = label

        # 4) Exibição
        if header_info:
            st.subheader(f"Questão {header_info}")
        else:
            st.subheader("Questão")

        st.write(enunciado)

        st.subheader("Alternativas:")
        for label, alt in alternatives.items():
            st.write(f"**{label})** {alt}")

        if highlighted:
            st.success(f"**Alternativa destacada:** {highlighted})")
        else:
            st.info("Nenhuma alternativa destacada identificada.")
