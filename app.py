import base64
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load environment variables from .env file
load_dotenv()

# 2. Initialize OpenAI Client (automatically reads OPENAI_API_KEY from .env)
client = OpenAI()

st.set_page_config(
    page_title="Biomedical Waste Assistant",
    layout="centered"
)

st.title("🏥 Biomedical Waste Assistant")
st.caption("Upload, capture, or ask where to dispose medical waste safely.")

# Waste classification rules
bin_mapping = {
    "gloves": {
        "bin": "Blue Bin",
        "reason": "Contaminated recyclable plastic waste",
        "instruction": "Dispose in the Blue Bin as per hospital biomedical waste rules."
    },
    "face mask": {
        "bin": "Blue Bin",
        "reason": "Contaminated recyclable waste",
        "instruction": "Dispose in the Blue Bin after use."
    },
    "surgical mask": {
        "bin": "Blue Bin",
        "reason": "Contaminated recyclable waste",
        "instruction": "Dispose in the Blue Bin after use."
    },
    "ppe kit": {
        "bin": "Blue Bin",
        "reason": "Contaminated protective equipment",
        "instruction": "Dispose in the Blue Bin as per hospital process."
    },
    "syringe": {
        "bin": "Yellow Bin",
        "reason": "Sharp biomedical waste",
        "instruction": "Dispose in a puncture-resistant sharps container before final disposal."
    },
    "needle": {
        "bin": "Yellow Bin",
        "reason": "Sharp biomedical waste",
        "instruction": "Dispose in a puncture-resistant sharps container or sharp box/Yellow Bin after use."
    },
    "iv set": {
        "bin": "Yellow Bin",
        "reason": "Infectious biomedical waste",
        "instruction": "Dispose in the Yellow Bin after use."
    },
    "catheter": {
        "bin": "Yellow Bin",
        "reason": "Infectious biomedical waste",
        "instruction": "Dispose in the Yellow Bin."
    },
    "blood bag": {
        "bin": "Yellow Bin",
        "reason": "Biomedical infectious waste",
        "instruction": "Dispose in the Yellow Bin following hospital safety procedure."
    },
    "glass vial": {
        "bin": "Red Bin",
        "reason": "Contaminated glass waste",
        "instruction": "Dispose in the Red Bin after disinfection/autoclaving as per rules."
    },
    "medicine bottle": {
        "bin": "Black Bin",
        "reason": "Pharmaceutical or general medical waste",
        "instruction": "Dispose as per hospital pharmaceutical waste guidelines."
    },
    "tablet strip": {
        "bin": "Black Bin",
        "reason": "Pharmaceutical packaging waste",
        "instruction": "Dispose in the Black Bin as per local hospital rules."
    }
}


def classify_item(text):
    text = text.lower().strip()

    for item in bin_mapping:
        if item in text:
            return item, bin_mapping[item]
    return None, None


def show_result(item, result):
    st.subheader("✅ Disposal Recommendation")

    st.write(f"**Item Identified:** {item.title()}")

    bin_name = result["bin"]

    if bin_name == "Yellow Bin":
        st.warning(f"🟡 **Recommended Bin:** {bin_name}")
    elif bin_name == "Blue Bin":
        st.info(f"🔵 **Recommended Bin:** {bin_name}")
    elif bin_name == "Red Bin":
        st.error(f"🔴 **Recommended Bin:** {bin_name}")
    elif bin_name == "Black Bin":
        st.success(f"⚫ **Recommended Bin:** {bin_name}")
    else:
        st.write(f"**Recommended Bin:** {bin_name}")

    st.write(f"**Reason:** {result['reason']}")
    st.write(f"**Disposal Instruction:** {result['instruction']}")


def identify_image(image_file):
    image_bytes = image_file.getvalue()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """You are a biomedical waste classification assistant.

Identify the medical waste item in this image.

Return only one item name from this list:
Gloves
Face Mask
Surgical Mask
PPE Kit
Syringe
Needle
Glass Vial
Medicine Bottle
Tablet Strip

Return only the item name. No explanation."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content.strip()


st.markdown("""
### 👋 Hello!
I can help you identify biomedical waste and suggest the correct disposal bin.

You can:
- Type a question
- Upload an image
- Take a photo using camera
""")

st.divider()

# Chat section
st.subheader("💬 Ask the Assistant")

user_input = st.chat_input("Example: Which bin for syringe?")

if user_input:
    st.chat_message("user").write(user_input)

    item, result = classify_item(user_input)

    if result:
        with st.chat_message("assistant"):
            show_result(item, result)
    else:
        with st.chat_message("assistant"):
            st.error("Item not found in current waste classification rules.")
            st.write("Please check with the hospital waste management team.")

st.divider()

# Image upload and camera section
st.subheader("📷 Upload or Capture Image")

uploaded_file = st.file_uploader(
    "Upload medical waste image",
    type=["jpg", "jpeg", "png"]
)

# Camera toggle to stop camera stream when not needed
use_camera = st.checkbox("Turn on Camera")

camera_image = None
if use_camera:
    camera_image = st.camera_input("Or take a photo using camera")

# Prioritize uploaded file; if none, use camera image
image_file = uploaded_file or camera_image

if image_file:
    st.image(image_file, width=300)

    with st.spinner("Analyzing image using AI..."):
        identified_item = identify_image(image_file)

    st.write(f"AI identified this item as: **{identified_item}**")

    item, result = classify_item(identified_item)

    if result:
        show_result(item, result)
    else:
        st.error("Item not found in current waste classification rules.")
        st.write("Please check with the hospital waste management team.")