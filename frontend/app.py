import streamlit as st
from datetime import datetime

# -------------------------------------------------------------------
# Fonctions utilitaires
# -------------------------------------------------------------------


def init_session_state():
    """
    Initialise toutes les variables de session dont nous avons besoin.
    """
    if "patients" not in st.session_state:
        # Trois patients fictifs avec date de création
        now = datetime.now().timestamp()
        st.session_state["patients"] = [
            {
                "id": 1,
                "nom": "Doe",
                "prenom": "John",
                "date_naissance": "1990-01-15",
                "genre": "Male",
                "poids": 70,
                "created_at": now - 300,  # exemple : il y a 5 min
                "entretiens": []
            },
            {
                "id": 2,
                "nom": "Smith",
                "prenom": "Jane",
                "date_naissance": "1995-05-20",
                "genre": "Female",
                "poids": 60,
                "created_at": now - 200,  # exemple : il y a ~3 min
                "entretiens": []
            },
            {
                "id": 3,
                "nom": "Brown",
                "prenom": "Michael",
                "date_naissance": "1980-11-30",
                "genre": "Male",
                "poids": 80,
                "created_at": now - 100,  # exemple : il y a ~2 min
                "entretiens": []
            },
        ]
    if "selected_patient_id" not in st.session_state:
        st.session_state["selected_patient_id"] = None

    if "selected_interview_id" not in st.session_state:
        st.session_state["selected_interview_id"] = None

    # Pour la création d'un nouveau patient
    if "show_new_patient_form" not in st.session_state:
        st.session_state["show_new_patient_form"] = False


def get_patient_by_id(patient_id):
    for p in st.session_state["patients"]:
        if p["id"] == patient_id:
            return p
    return None


def get_next_patient_id():
    """
    Trouve le prochain ID disponible pour un nouveau patient.
    """
    existing_ids = [p["id"] for p in st.session_state["patients"]]
    return max(existing_ids) + 1 if existing_ids else 1


def get_next_interview_id(patient):
    """
    Trouve le prochain ID disponible pour un nouvel entretien d'un patient donné.
    """
    if not patient["entretiens"]:
        return 1
    existing_ids = [e["id"] for e in patient["entretiens"]]
    return max(existing_ids) + 1


def create_new_patient(nom, prenom, date_naissance, genre, poids):
    """
    Crée un nouveau patient dans la liste de session_state.
    """
    new_id = get_next_patient_id()
    new_patient = {
        "id": new_id,
        "nom": nom,
        "prenom": prenom,
        "date_naissance": date_naissance,
        "genre": genre,
        "poids": poids,
        "created_at": datetime.now().timestamp(),
        "entretiens": []
    }
    st.session_state["patients"].append(new_patient)
    st.session_state["show_new_patient_form"] = False
    st.session_state["selected_patient_id"] = new_id


def create_new_interview(patient_id):
    """
    Crée un nouvel entretien pour le patient sélectionné.
    Inclut automatiquement les informations du patient dans la transcription.
    """
    patient = get_patient_by_id(patient_id)
    if patient:
        new_id = get_next_interview_id(patient)

        # Calculer l'âge actuel du patient
        age = calculate_age(patient['date_naissance'])

        # Créer l'en-tête de la transcription avec les informations du patient
        initial_transcription = f"""Patient Information:
- Age: {age} years old
- Gender: {patient['genre']}
- Weight: {patient['poids']} kg

Transcription:
"""

        # Entretien avec transcription pré-remplie
        new_interview = {
            "id": new_id,
            "titre": f"Interview {new_id}",
            "date": datetime.now().strftime("%d/%m/%Y"),
            "transcription": initial_transcription,
            "transcription_active": True,
            "editable": True,
            "chat_history": [
                ("IA", "I will analyze the interview with the patient.")
            ]
        }
        patient["entretiens"].append(new_interview)
        st.session_state["selected_interview_id"] = new_id


def delete_interview(patient_id, interview_id):
    """
    Supprime un entretien du patient.
    """
    patient = get_patient_by_id(patient_id)
    if patient:
        patient["entretiens"] = [
            e for e in patient["entretiens"] if e["id"] != interview_id
        ]
        # Si on supprime l'entretien sélectionné, on réinitialise
        if st.session_state["selected_interview_id"] == interview_id:
            st.session_state["selected_interview_id"] = None


def get_selected_interview():
    """
    Récupère l'entretien actuellement sélectionné, ou None s'il n'y en a pas.
    """
    if st.session_state["selected_patient_id"] is None:
        return None
    if st.session_state["selected_interview_id"] is None:
        return None
    patient = get_patient_by_id(st.session_state["selected_patient_id"])
    if not patient:
        return None
    for e in patient["entretiens"]:
        if e["id"] == st.session_state["selected_interview_id"]:
            return e
    return None


# Fonction pour calculer l'âge à partir de la date de naissance
def calculate_age(birth_date_str):
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    today = datetime.now()
    age = today.year - birth_date.year - \
        ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


# -------------------------------------------------------------------
# Mise en page de la page Streamlit
# -------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="HCP Assistant")

# Initialisation de la session
init_session_state()

# Appliquer le style pour les boutons
st.markdown("""
<style>
/* Style de base pour tous les boutons */
div.stButton > button {
    background-color: #1E2A3A !important;
    color: white !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    border-radius: 4px !important;
    border: 1px solid #3D5A80 !important;
    padding: 12px !important;
    margin: 4px 0 !important;
    transition: all 0.3s ease !important;
}

/* Style pour les boutons patients */
div.stButton > button[key*="select_"] {
    background-color: #1E2A3A !important;
    border-left: 4px solid #3D5A80 !important;
    text-align: left !important;
    padding: 12px 15px !important;
    margin: 8px 0 !important;
    width: 100% !important;
    height: 70px !important;
}

div.stButton > button[key*="select_"]:hover {
    background-color: #2C3E50 !important;
    border-left-color: #5A8BBF !important;
    transform: translateX(5px) !important;
}

/* Style pour le bouton Créer patient */
div.stButton > button[key="create_patient"] {
    background-color: #2E4B73 !important;
    border: 2px solid #3D5A80 !important;
    color: white !important;
    font-weight: bold !important;
    font-size: 16px !important;
    width: 100% !important;
    margin: 1em 0 2em 0 !important;
}

div.stButton > button[key="create_patient"]:hover {
    background-color: #3D5A80 !important;
    transform: translateY(-2px) !important;
}

/* Style pour les autres boutons d'action */
div.stButton > button[key*="send_"],
div.stButton > button[key*="new_"],
div.stButton > button[key*="validate_"] {
    background-color: #2E4B73 !important;
    border-color: #3D5A80 !important;
}
</style>
""", unsafe_allow_html=True)

# Organisation en trois colonnes : gauche, centre, droite
col_left, col_center, col_right = st.columns([2, 5, 3])

# -------------------------------------------------------------------
# Colonne de gauche : liste des patients, recherche, création patient
# -------------------------------------------------------------------
with col_left:
    st.header("Patient List")

    # Choix du critère de tri
    sort_option = st.selectbox(
        "Sort by:",
        ["Name", "First name", "Creation date"],
        index=0
    )

    # Barre de recherche
    search_query = st.text_input("🔍 Search patient (name/first name):", "")

    # Bouton de création
    if st.button("➕ New Patient", key="create_patient"):
        st.session_state["show_new_patient_form"] = True

    # Tri des patients
    if sort_option == "Name":
        sorted_patients = sorted(
            st.session_state["patients"], key=lambda x: x["nom"].lower())
    elif sort_option == "First name":
        sorted_patients = sorted(
            st.session_state["patients"], key=lambda x: x["prenom"].lower())
    else:  # "Creation date"
        sorted_patients = sorted(
            st.session_state["patients"], key=lambda x: x["created_at"])

    # Filtrer en fonction de la recherche
    filtered_patients = []
    for p in sorted_patients:
        if (search_query.lower() in p["nom"].lower()) or (search_query.lower() in p["prenom"].lower()):
            filtered_patients.append(p)

    # Boutons de sélection des patients
    for patient in filtered_patients:
        if st.button(f"{patient['prenom']} {patient['nom']}", key=f"select_{patient['id']}"):
            st.session_state["selected_patient_id"] = patient["id"]
            st.session_state["selected_interview_id"] = None

    # Formulaire de création
    if st.session_state["show_new_patient_form"]:
        st.subheader("New Patient")
        nom_new = st.text_input("Last name")
        prenom_new = st.text_input("First name")
        date_naissance_new = st.date_input("Birth date", format="YYYY-MM-DD")
        genre_new = st.selectbox("Gender", ["Male", "Female", "Other"])
        poids_new = st.number_input(
            "Weight (kg)", min_value=0, max_value=300, step=1)

        if st.button("Create", key="validate_new_patient"):
            create_new_patient(
                nom_new,
                prenom_new,
                date_naissance_new.strftime("%Y-%m-%d"),
                genre_new,
                poids_new
            )

# -------------------------------------------------------------------
# Colonne centrale : informations patient, liste d'entretiens, détails
# -------------------------------------------------------------------
with col_center:
    st.header("Patient Details")

    # Récupérer le patient sélectionné
    selected_patient = None
    if st.session_state["selected_patient_id"] is not None:
        selected_patient = get_patient_by_id(
            st.session_state["selected_patient_id"])

    if selected_patient is None:
        st.write("No patient selected.")
    else:
        # Ajouter un toggle pour le mode édition
        edit_mode = st.checkbox("Edit patient information", value=False)

        # Affichage des infos avec possibilité de modification
        col1, col2 = st.columns(2)

        with col1:
            if edit_mode:
                new_lastname = st.text_input(
                    "Last name", value=selected_patient['nom'])
                new_firstname = st.text_input(
                    "First name", value=selected_patient['prenom'])
                new_birth_date = st.date_input(
                    "Birth date",
                    value=datetime.strptime(
                        selected_patient['date_naissance'], "%Y-%m-%d"),
                    format="YYYY-MM-DD"
                )
            else:
                st.write(f"**Last name** : {selected_patient['nom']}")
                st.write(f"**First name** : {selected_patient['prenom']}")
                birth_date = datetime.strptime(
                    selected_patient['date_naissance'], "%Y-%m-%d")
                age = calculate_age(selected_patient['date_naissance'])
                st.write(
                    f"**Birth date** : {birth_date.strftime('%Y-%m-%d')} ({age} years old)")

        with col2:
            if edit_mode:
                new_gender = st.selectbox("Gender",
                                          ["Male", "Female", "Other"],
                                          index=["Male", "Female", "Other"].index(selected_patient['genre']))
                new_weight = st.number_input("Weight (kg)",
                                             min_value=0,
                                             max_value=300,
                                             value=selected_patient['poids'])
            else:
                st.write(f"**Gender** : {selected_patient['genre']}")
                st.write(f"**Weight** : {selected_patient['poids']} kg")

        # Bouton de sauvegarde en mode édition
        if edit_mode:
            if st.button("Save changes", type="primary"):
                selected_patient['nom'] = new_lastname
                selected_patient['prenom'] = new_firstname
                selected_patient['date_naissance'] = new_birth_date.strftime(
                    "%Y-%m-%d")
                selected_patient['genre'] = new_gender
                selected_patient['poids'] = new_weight
                st.success("Patient information updated successfully!")
                st.rerun()

        st.write("---")

        # Zone scrollable horizontale pour les entretiens
        st.subheader("Interviews")

        # On va construire manuellement un conteneur horizontal en HTML/CSS
        st.markdown(
            """
            <style>
            .scroll-container {
                display: flex;
                flex-wrap: nowrap;
                overflow-x: auto;
            }
            .scroll-item {
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 10px;
                margin-right: 10px;
                min-width: 150px;
                text-align: center;
                cursor: pointer;
            }
            .scroll-item:hover {
                background-color: #e6e6e6;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

        # Bouton "Nouveau" (grand +) pour créer un entretien
        if st.button("New +", key="new_interview_button"):
            create_new_interview(selected_patient["id"])

        # Pour chaque entretien, on crée un "bouton"
        for entretien in selected_patient["entretiens"]:
            if st.button(f"{entretien['titre']} - {entretien['date']}", key=f"open_{entretien['id']}"):
                st.session_state["selected_interview_id"] = entretien["id"]

        st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")

        # Afficher les détails de l'entretien sélectionné
        selected_interview = get_selected_interview()

        if selected_interview:
            # Toggle pour activer/désactiver la modification
            editable = st.checkbox(
                "Edit mode", value=selected_interview.get("editable", True))
            selected_interview["editable"] = editable

            # Titre de l'entretien
            new_title = st.text_input(
                "Interview title",
                value=selected_interview["titre"],
                disabled=not editable
            )
            # Zone de texte pour la transcription
            new_transcription = st.text_area(
                "Interview transcription",
                value=selected_interview["transcription"],
                disabled=not editable,
                height=200
            )

            # Toggle transcription active ou non
            transcription_active = st.checkbox(
                "Active transcription",
                value=selected_interview["transcription_active"],
                disabled=not editable
            )

            # Boutons d'action
            col_save, col_delete = st.columns(2)
            with col_save:
                if st.button("Save", disabled=not editable):
                    selected_interview["titre"] = new_title
                    selected_interview["transcription"] = new_transcription
                    selected_interview["transcription_active"] = transcription_active
                    st.success("Interview saved!")

            with col_delete:
                if st.button("Delete"):
                    delete_interview(
                        selected_patient["id"], selected_interview["id"])
                    st.warning("Interview deleted!")

# -------------------------------------------------------------------
# Colonne de droite : Chat avec l'assistant IA
# -------------------------------------------------------------------
with col_right:
    st.header("AI Assistant")

    # On récupère l'entretien sélectionné
    current_interview = get_selected_interview()

    # On prépare du style CSS pour aligner IA à gauche et Médecin à droite
    st.markdown("""
    <style>
    .chat-bubble {
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        max-width: 80%;
        color: #000000;  /* Texte en noir */
    }
    .chat-bubble-ia {
        background-color: #e1e1e1;  /* Fond gris plus foncé pour l'IA */
        margin-right: auto;  /* aligne à gauche */
        text-align: left;
    }
    .chat-bubble-user {
        background-color: #c7d7ff;  /* Fond bleu plus foncé pour l'utilisateur */
        margin-left: auto;  /* aligne à droite */
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

    # Si un entretien est ouvert, on affiche l'historique
    if current_interview:
        for role, message in current_interview["chat_history"]:
            if role == "IA":
                # IA à gauche
                st.markdown(
                    f"<div class='chat-bubble chat-bubble-ia'><strong>AI:</strong> {message}</div>",
                    unsafe_allow_html=True
                )
            else:
                # Médecin à droite
                st.markdown(
                    f"<div class='chat-bubble chat-bubble-user'><strong>You:</strong> {message}</div>",
                    unsafe_allow_html=True
                )
    else:
        st.write(
            "No interview selected. Please select or create an interview to start the conversation.")

    # Barre de saisie de question
    user_input = st.text_input("Ask your question to the AI:")

    # Bouton "Envoyer"
    if st.button("Send", key="send_message"):
        if not current_interview:
            st.warning(
                "No interview selected. Please select or create an interview first.")
        else:
            if user_input.strip():
                current_interview["chat_history"].append(
                    ("Doctor", user_input))
                ia_response = "Thank you for your question"
                current_interview["chat_history"].append(("IA", ia_response))
                st.rerun()
