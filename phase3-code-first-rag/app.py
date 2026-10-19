import streamlit as st
from rag_chain import get_rag_response

st.set_page_config(page_title="AutoSpec - Fase 3 (LangChain + Gemini)")
st.title("AutoSpec - Consultas Automotrices (LangChain)")

input_text = st.text_area("Input text", label_visibility="collapsed")
go_button = st.button("Go", type="primary")

if go_button:
    with st.spinner("Working..."):
        respuesta, resultados = get_rag_response(input_text)
        st.write(respuesta)
        with st.expander("Fragmentos recuperados"):
            for doc, distancia in resultados:
                st.caption(f"distancia = {distancia:.3f}")
                st.text(doc.page_content)
