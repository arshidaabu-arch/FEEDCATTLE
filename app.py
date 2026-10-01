import streamlit as st
import numpy as np
import cv2
from PIL import Image

st.set_page_config(page_title="FEEDWISE Camera Prototype", page_icon="🌾", layout="wide")
st.title("🌾 FEEDWISE")
st.subheader("Camera-assisted feed & silage quality screening")
st.caption("Prototype • Visual screening + user-entered protein assessment")
st.warning("Demo only: the camera flags broad visual anomalies; it does not identify fungi or detect mycotoxins. A low score does not prove feed is safe. Confirm suspected contamination using validated tests.")

def screen(img):
    a=np.array(img.convert("RGB"))
    h,w=a.shape[:2]
    scale=min(1,700/max(h,w))
    if scale<1: a=cv2.resize(a,(int(w*scale),int(h*scale)))
    hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV)
    gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
    dark=(gray<55).mean()
    pale=((hsv[:,:,2]>165)&(hsv[:,:,1]<45)).mean()
    green=((hsv[:,:,0]>=25)&(hsv[:,:,0]<=95)&(hsv[:,:,1]>45)&(hsv[:,:,2]>35)).mean()
    texture=cv2.Laplacian(gray,cv2.CV_64F).var()
    score=min(100,100*(.4*min(dark/.2,1)+.3*min(pale/.35,1)+.2*min(green/.2,1)+.1*min(texture/1200,1)))
    return score,{"Dark pixels (%)":dark*100,"Pale low-saturation pixels (%)":pale*100,"Greenish pixels (%)":green*100,"Texture indicator":texture}

cam,protein,about=st.tabs(["📷 Camera screening","🥛 Protein assessment","ℹ️ How it works"])
with cam:
    mode=st.radio("Image source",["Use camera","Upload image"],horizontal=True)
    file=st.camera_input("Take a sample photo") if mode=="Use camera" else st.file_uploader("Upload JPG/PNG",type=["jpg","jpeg","png"])
    if file:
        try:
            img=Image.open(file).convert("RGB")
            c1,c2=st.columns(2)
            c1.image(img,caption="Sample image",use_container_width=True)
            score,features=screen(img)
            c2.metric("Visual anomaly indicator",f"{score:.1f}/100")
            if score>=55: c2.error("Visual review recommended. This is not a fungal diagnosis.")
            elif score>=25: c2.warning("Some image features were flagged. Review and consider testing.")
            else: c2.success("Few features flagged; this does NOT prove the feed is mold-free or safe.")
            with st.expander("Image features used"):
                st.json({k:round(v,3) for k,v in features.items()})
            st.info("If mold-like growth, unusual odour, heating or spoilage is suspected, isolate the batch and arrange appropriate testing.")
        except Exception as e:
            st.error(f"Could not read image: {e}")
with protein:
    st.caption("Enter a target from an applicable feeding standard or nutritionist, and a measured value from a suitable test. Protein is not inferred from the photo.")
    with st.form("protein"):
        animal=st.selectbox("Cattle category",["Lactating dairy cow","Dry cow","Growing heifer","Calf","Other"])
        weight=st.number_input("Body weight (kg)",min_value=0.0,value=400.0,step=10.0)
        milk=st.number_input("Milk yield (litres/day; 0 if not applicable)",min_value=0.0,value=10.0,step=.5)
        target=st.number_input("Target crude protein (% of dry matter)",min_value=0.0,max_value=100.0,value=16.0,step=.5)
        measured=st.number_input("Measured crude protein (% of dry matter)",min_value=0.0,max_value=100.0,value=0.0,step=.5)
        dmi=st.number_input("Dry matter intake (kg/day; optional, 0 if unknown)",min_value=0.0,value=0.0,step=.5)
        go=st.form_submit_button("Compare protein values",type="primary")
    if go:
        if target<=0 or measured<=0:
            st.error("Enter both a positive target and a measured protein value.")
        else:
            delta=measured-target
            a,b,c=st.columns(3)
            a.metric("Target",f"{target:.1f}%")
            b.metric("Measured",f"{measured:.1f}%")
            c.metric("Difference",f"{delta:+.1f} percentage points")
            if abs(delta)<.05: st.success("Measured value matches the entered target.")
            elif delta<0: st.warning(f"Measured protein is {abs(delta):.1f} percentage points below the target.")
            else: st.info(f"Measured protein is {delta:.1f} percentage points above the target.")
            if dmi>0:
                st.write(f"Estimated crude protein intake: **{dmi*measured/100:.2f} kg/day**, assuming both inputs use the same ration dry-matter basis.")
            st.caption("A percentage comparison alone cannot determine whether a ration meets an animal's needs. Requirements depend on weight, production, physiological stage, intake and feed composition. Consult a qualified animal nutritionist.")
with about:
    st.markdown("""
    **Camera basis:** this demo calculates broad dark-pixel, pale/low-saturation, greenish-colour and texture indicators. These features can occur naturally in feed and are not unique to fungi.

    **For a genuine fungal image model:** collect representative images with laboratory-confirmed labels across feed types, lighting and contamination stages; train and test on separate samples; report sensitivity, specificity and false-negative rates. Even a validated model is only a screening aid. It cannot establish mycotoxin concentration.

    **Protein basis:** use a target from an applicable feeding standard or qualified nutritionist. The app compares that target with a measured value; it does not calculate a universal requirement or measure protein.
    """)
