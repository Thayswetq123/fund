import streamlit as st
import io
import numpy as np
from PIL import Image, ImageOps
from keras.models import load_model

from startup_db import (
    init_db,
    register_user,
    check_login,
    save_item,
    get_connection
)

# DB starten
init_db()

st.set_page_config(layout="wide")
st.title("🏢 Real Startup Fundbüro KI Platform")

# Model laden
@st.cache_resource
def load_model_cached():
    return load_model("keras_model.h5", compile=False)

model = load_model_cached()

with open("labels.txt") as f:
    labels = [x.strip() for x in f]

# Prediction Engine
def predict_image(image):

    img = ImageOps.fit(image,(224,224))

    arr = np.asarray(img)
    arr = (arr.astype(np.float32)/127.5)-1

    data = np.expand_dims(arr,0)

    pred = model.predict(data,verbose=0)

    index = np.argmax(pred)

    return labels[index], float(pred[0][index])

# Session State
if "user" not in st.session_state:
    st.session_state.user = None

# ===========================
# Login / Register UI
# ===========================

if st.session_state.user is None:

    tab_login, tab_register = st.tabs(["Login","Register"])

    with tab_login:

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login Starten"):

            if check_login(username,password):

                st.session_state.user = username
                st.rerun()

            else:
                st.error("Login Fehler")

    with tab_register:

        new_user = st.text_input("Neuer Username")
        new_pass = st.text_input("Neues Passwort", type="password")

        if st.button("Registrieren"):

            if register_user(new_user,new_pass):
                st.success("Registrierung erfolgreich")
            else:
                st.error("User existiert")

    st.stop()

# ===========================
# Dashboard
# ===========================

tab1, tab2, tab3 = st.tabs([
    "📤 Fundstück Upload",
    "🔍 Suche",
    "📷 Kamera"
])

# Upload
with tab1:

    uploaded = st.file_uploader(
        "Fundstück Bild hochladen",
        type=["jpg","jpeg","png"]
    )

    if uploaded:

        image = Image.open(uploaded).convert("RGB")

        label, conf = predict_image(image)

        st.image(image, width=400)

        st.success(f"Erkannt → {label}")
        st.info(f"Sicherheit → {round(conf*100,2)}%")

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        save_item(
            st.session_state.user,
            buffer.getvalue(),
            label,
            conf
        )

        st.success("In Funddatenbank gespeichert")

# Suche
with tab2:

    st.subheader("🔎 Fundbüro Suche")

    search = st.text_input("Suche")

    conn = get_connection()

    rows = conn.execute(
        "SELECT id,username,prediction,confidence,timestamp,image FROM fund_items"
    ).fetchall()

    conn.close()

    if search:
        rows = [r for r in rows if search.lower() in str(r).lower()]

    cols = st.columns(3)

    for i,row in enumerate(rows):

        with cols[i%3]:

            st.image(row[5], width=250)
            st.caption(f"{row[2]}")
            st.caption(f"{row[4]}")

# Kamera
with tab3:

    cam = st.camera_input("Foto aufnehmen")

    if cam:

        image = Image.open(cam).convert("RGB")

        label, conf = predict_image(image)

        st.image(image, width=400)

        st.success(f"Erkannt → {label}")
        st.info(f"Sicherheit → {round(conf*100,2)}%")

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        save_item(
            st.session_state.user,
            buffer.getvalue(),
            label,
            conf
        )
