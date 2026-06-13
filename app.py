import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io
from pdf2image import convert_from_bytes

st.set_page_config(page_title="Profesor de Portugués Anki", page_icon="🇵🇹")

st.title("🇵🇹 Generador de Tarjetas Anki")
st.write("Sube una foto o PDF con tus marcas de color.")

api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# Prompt optimizado
OPTIMIZED_PROMPT = """Actúa como un experto profesor de Portugués de Portugal. 
Tu misión es crear un mazo de Anki exhaustivo.
Prioridad Crítica: Identifica CADA palabra o frase subrayada o resaltada. 
Es obligatorio crear una tarjeta por cada elemento marcado.
Formato: Una sola línea por tarjeta; Pregunta; Respuesta (con frase de contexto)."""

def process_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        # Convertimos solo la primera página para este ejemplo
        images = convert_from_bytes(uploaded_file.read(), first_page=1, last_page=1)
        return images[0]
    else:
        return Image.open(uploaded_file)

if api_key:
    client = OpenAI(api_key=api_key)
    uploaded_file = st.file_uploader("Elige una imagen o PDF...", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file is not None:
        # Procesar el archivo para obtener una imagen compatible
        image = process_file(uploaded_file)
        st.image(image, caption='Archivo listo para procesar', use_container_width=True)
        
        if st.button("Generar Tarjetas"):
            with st.spinner("Analizando marcas..."):
                # Convertir imagen a base64
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
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
                    st.success("¡Tarjetas generadas!")
                    st.text_area("Resultado:", result, height=400)
                    
                    st.download_button(
                        label="Descargar .txt",
                        data=result,
                        file_name="mazo_portugues.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Error de API: {e}")
else:
    st.warning("Introduce tu API Key en la barra lateral.")
