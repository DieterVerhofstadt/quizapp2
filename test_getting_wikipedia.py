import streamlit as st
import requests

def get_pages_from_category(category_name, limit=50):
    S = requests.Session()
    URL = "https://nl.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Categorie:{category_name}",
        "cmlimit": limit,
        "format": "json"
    }
    response = S.get(url=URL, params=params)
    data = response.json()
    members = data.get("query", {}).get("categorymembers", [])
    return [item["title"] for item in members]

def get_summary(title):
    safe_title = title.replace(" ", "_")
    url = f"https://nl.wikipedia.org/api/rest_v1/page/summary/{safe_title}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("extract")
    return None

categorie = "Winnaar_van_de_Nobelprijs_voor_Literatuur"
pagina_titels = get_pages_from_category(categorie)
if st.button("Go"):
    for titel in pagina_titels:
        samenvatting = get_summary(titel)
        st.subheader(titel)
        st.write(samenvatting)
