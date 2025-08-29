import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import replicate


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN") or st.secrets.get("REPLICATE_API_TOKEN")


if not OPENAI_API_KEY:
    st.stop()
if not REPLICATE_API_TOKEN:
    st.stop()


client = OpenAI(api_key=OPENAI_API_KEY)
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN


st.set_page_config(page_title="FichaXpress AI", page_icon="🛍️", layout="centered")
st.title("🛍️ FichaXpress AI")
st.write("Generá descripciones de producto consistentes y una imagen conceptual en segundos.")


with st.form("input_form"):
    nombre = st.text_input("Nombre del producto", placeholder="Zapatillas Urban Runner Pro")
    bullets = st.text_area("Características clave (una por línea)", height=120,
                           placeholder="Amortiguación de alta densidad\nTela respirable\nSuela antideslizante")
    categoria = st.selectbox("Categoría", ["Calzado", "Indumentaria", "Electrónica", "Hogar", "Belleza", "Deportes", "Otro"])
    tono = st.selectbox("Tono", ["Profesional", "Amigable", "Técnico", "Premium", "Minimalista"])
    idioma = st.selectbox("Idioma", ["Español", "English", "Português"])
    generar_img = st.checkbox("Generar imagen conceptual", value=True)
    submit = st.form_submit_button("⚡ Generar ficha e imagen")

def build_prompt(nombre, bullets, categoria, tono, idioma):
    return f"""
Actuá como un especialista en contenidos de e-commerce. Generá una ficha de producto clara y persuasiva en {idioma}.
Producto: {nombre}
Categoría: {categoria}
Tono: {tono}
Características (bullets): 
{bullets}

Entregá la salida EXCLUSIVAMENTE en este formato Markdown:

# Título
[un título atractivo, 6-10 palabras]

## Descripción
[2-3 párrafos breves, sin relleno, con beneficios claros]

## Atributos clave
- Material:
- Medidas/Peso:
- Color/Variantes:
- Garantía:
- Uso recomendado:

## Bullets para la ficha
- [5 bullets concretos, 8-12 palabras c/u]

## SEO
- Keywords: [5-8]
- Meta description: [máx. 150 caracteres]

## CTA
[una sola frase persuasiva]
""".strip()

def generate_copy(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
        messages=[
            {"role": "system", "content": "Sos un experto en contenido de e-commerce, conciso y orientado a conversiones."},
            {"role": "user", "content": prompt},
        ],
    )
    return completion.choices[0].message.content

def generate_image(nombre, bullets, categoria, tono):
    
    bullet_list = ", ".join([b.strip() for b in bullets.splitlines() if b.strip()][:5])
    visual_prompt = (
        f"{nombre}, {categoria.lower()} product studio shot, clean white background, "
        f"hero view, {bullet_list}, modern lighting, high contrast, aesthetic product photography"
    )
    output = replicate.run(
        "black-forest-labs/flux-schnell:9d17bb0c9c9f7b4ee1c0e9f3ab5b0bde9a7a44a9b6b7b0f9d88f53c2e34f5f4b",
        input={
            "prompt": visual_prompt,
            "num_inference_steps": 4,   
            "guidance": 1.2,
            "width": 768,
            "height": 768,
        },
    )
    
    return output[0] if isinstance(output, list) else output

if submit:
    if not nombre.strip():
        st.error("Ingresá al menos el nombre del producto.")
        st.stop()

    st.subheader("Salida dirigida")
    with st.spinner("Generando contenido..."):
        prompt = build_prompt(nombre, bullets, categoria, tono, idioma)
        copy_md = generate_copy(prompt)
        st.markdown(copy_md)

    if generar_img:
        with st.spinner("Generando imagen conceptual..."):
            try:
                img_url = generate_image(nombre, bullets, categoria, tono)
                st.image(img_url, caption="Imagen conceptual generada (no contractual).", use_container_width=True)
            except Exception as e:
                st.warning("No se pudo generar la imagen en este momento. Probá nuevamente.")

# Sección: Cómo funciona
with st.expander("ℹ️ Cómo funciona"):
    st.markdown("""
- **Entrada:** Nombre del producto, características, categoría, tono e idioma.
- **IA de texto:** Estructura la ficha con descripción, atributos, bullets y SEO.
- **IA de imagen:** Genera un hero conceptual para inspirar la estética de la ficha.
- **Uso recomendado:** Usá el copy tal cual y sustituí la imagen por fotos reales cuando las tengas.
- **Costos:** Ver abajo; cada ejecución consume 1 llamada de texto y, si activás, 1 de imagen.
""")

# Footer
st.write("---")
st.caption("Hecho con Streamlit. © 2025 FichaXpress AI")
