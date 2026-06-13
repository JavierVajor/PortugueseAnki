import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

# Configuración de la página
st.set_page_config(page_title="Profesor de Portugués Anki", page_icon="🇵🇹")

st.title("🇵🇹 Generador de Tarjetas Anki (Portugal)")
st.write("Sube una foto o PDF de tus apuntes subrayados y generaré el mazo.")

# Sidebar para la API Key
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# El Prompt Optimizado
OPTIMIZED_PROMPT = """Actúa como un experto profesor de Portugués de Portugal con más de 20 años de experiencia. 
Tu misión es crear un mazo de Anki exhaustivo a partir del material proporcionado.

INSTRUCCIONES DE PROCESAMIENTO (Prioridad Crítica):
1. Prioridad Absoluta a Marcas Visuales: Identifica CADA UNA de las palabras o frases subrayadas, resaltadas con marcador o rodeadas por un círculo. Es obligatorio crear una tarjeta por cada elemento marcado.
2. Tratamiento de Verbos: Si ves tablas de conjugación o verbos irregulares, crea tarjetas con la conjugación completa en Presente de Indicativo.
3. Lógica de Preguntas: De Español a Portugués con frase de contexto obligatoria.
4. Enfoque Contrastivo: Énfasis en falsos amigos y reglas de transformación (Z -> Ç, etc.).

FORMATO DE SALIDA:
- Una sola línea por tarjeta.
- Separador ';'. 
- Usa <b> para negrita, <i> para cursiva y <br> para saltos de línea."""

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

if api_key:
    client = OpenAI(api_key=api_key)
    uploaded_file = st.file_uploader("Elige una imagen o PDF...", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption='Archivo subido', use_column_width=True)
        
        if st.button("Generar Tarjetas"):
            with st.spinner("El profesor está analizando tus marcas..."):
                base64_image = encode_image(uploaded_file)
                
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": OPTIMIZED_PROMPT},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        },
                                    },
                                ],
                            }
                        ],
                        max_tokens=2000,
                    )
                    
                    result = response.choices[0].message.content
                    st.success("¡Tarjetas listas!")
                    st.text_area("Resultado para Anki:", result, height=400)
                    
                    st.download_button(
                        label="Descargar archivo .txt",
                        data=result,
                        file_name="mazo_portugues.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Hubo un error: {e}")
else:
    st.warning("Introduce tu API Key de OpenAI en la barra lateral para empezar.")
