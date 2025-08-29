import streamlit as st
import openai
import os


st.set_page_config(page_title="FichaXpress AI", page_icon="🛒")


openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")


st.title("🛒 FichaXpress AI")
st.write("Generá fichas de producto claras y optimizadas para tu e‑commerce.")


with st.expander("ℹ️ Cómo funciona"):
    st.markdown("""
- **Entrada:** Nombre del producto y características.
- **IA de texto:** Genera título, descripción y bullets optimizados.
- **Uso recomendado:** Usá el copy generado y adaptalo a tu tienda.
- **Costos:** Cada ejecución consume 1 llamada a la API de texto.
    """)


nombre = st.text_input("Nombre del producto")
caracteristicas = st.text_area("Características")
generar = st.button("Generar ficha")


if generar:
    if nombre and caracteristicas:
        with st.spinner("Generando ficha con IA..."):
            prompt = f"""
            Genera una ficha de producto para e‑commerce en formato:
            - Título llamativo
            - Descripción breve y persuasiva
            - 3 bullets con características

            Producto: {nombre}
            Características: {caracteristicas}
            Idioma: Español
            """
            try:
                respuesta = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  
                    messages=[
                        {"role": "system", "content": "Sos un experto en redacción de fichas de producto para e‑commerce."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5
                )
                salida = respuesta.choices[0].message.content
                st.subheader("📄 Ficha generada:")
                st.markdown(salida)
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
    else:
        st.warning("Por favor completá el nombre y las características.")

# --- Footer ---
st.write("---")
st.caption("Hecho con Streamlit. © 2025 FichaXpress AI")
