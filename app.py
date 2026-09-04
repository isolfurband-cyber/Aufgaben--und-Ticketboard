from datetime import datetime
import json
import os
import base64
import streamlit as st

st.set_page_config(
    page_title="KARE-Immobilien Ticketboard",
    page_icon="📋",
    layout="wide",
)

# --- SICHERE AUTHENTIFIZIERUNG VIA STREAMLIT SECRETS ---
try:
    USER_CREDENTIALS = dict(st.secrets["credentials"])
except Exception:
    st.error("Fehler: Keine Zugangsdaten in den Streamlit Secrets gefunden. Bitte trage sie im Cloud-Dashboard ein.")
    st.stop()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 KARE-Immobilien – Interner Login")
    st.markdown("Bitte logge dich ein, um auf das Ticketboard zuzugreifen.")

    with st.form("login_form"):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        login_btn = st.form_submit_button("Einloggen")

        if login_btn:
            if (
                username in USER_CREDENTIALS
                and USER_CREDENTIALS[username] == password
            ):
                st.session_state.authenticated = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Falscher Benutzername oder falsches Passwort!")
    st.stop()

# --- DATENPERSISTENZ (JSON DATEIEN) ---
TICKETS_FILE = "tickets.json"


def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "r", encoding="utf-8") as f:
            try:
                tickets = json.load(f)
                for t in tickets:
                    t.setdefault("id", 1)
                    t.setdefault("titel", "Ohne Titel")
                    t.setdefault("objekt", "Talstr. 32, 07545 Gera")
                    t.setdefault("kategorie", "Hausverwaltung Allgemein")
                    t.setdefault("priorität", "Mittel")
                    t.setdefault("status", "Offen")
                    t.setdefault(
                        "datum", datetime.now().strftime("%d.%m.%Y %H:%M")
                    )
                    t.setdefault("faellig", datetime.now().strftime("%d.%m.%Y"))
                    t.setdefault("beschreibung", "")
                    t.setdefault("ersteller", "Unbekannt")
                    t.setdefault("anhaenge", [])
                return tickets
            except json.JSONDecodeError:
                return []
    return []


def save_tickets(tickets):
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=4)


if "tickets" not in st.session_state:
    st.session_state.tickets = load_tickets()

# --- HAUPTAPP (NACH LOGIN) ---
st.markdown(
    """
    <div style='font-size: 1.5rem; font-weight: bold; margin-bottom: 0px;'>
        📋 KARE-Immobilien – Internes Aufgaben- & Ticketboard
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f"Eingeloggt als: **{st.session_state.user}** | Talstr. 32, 07545 Gera"
)

# --- SEITENLEISTE (SIDEBAR) ---
st.sidebar.title("Navigation")
menu = st.sidebar.selectbox(
    "Menü",
    [
        "📊 Dashboard & Tickets",
        "➕ Neues Ticket erstellen",
        "🚪 Abmelden",
    ],
)

# BEREICH: PROTOKOLLE & APPS IN DER SIDEBAR (Inkl. Quittungen)
st.sidebar.markdown("---")
st.sidebar.subheader("🌐 KARE-Protokolle & Apps")
st.sidebar.markdown(
    """
- [🏗️ Baustellenprotokoll](https://baustellenprotokoll-nwka229yyd9brp6zkbtwal.streamlit.app/)
- [💥 Schadenprotokoll](https://schadenprotokoll-ge8xt8a7tkjcb44m4te8zo.streamlit.app/)
- [🏠 Wohnungsprotokoll](https://wohnungsprotokoll-aoectc2n5tvphcg5eevjsm.streamlit.app/)
- [📂 Ordnungs- & Verstoßprotokoll](https://qyzzw9sm7htvbfuj6sc8k6.streamlit.app/)
- [🧾 Quittungen](https://aufgaben--und-ticketboard-jago3m8goqpy2vbmkg4wza.streamlit.app/)
- [🏢 Expose](https://appexposepy-3eut7yixhwmlkm6nvaebvz.streamlit.app/)
- [🔐 Zählerprotokoll](https://hfytg3in6ulhl7b3dzafrq.streamlit.app/)
""",
    unsafe_allow_html=True,
)


# --- SEITEN-LOGIK (HAUPTBEREICH) ---

if menu == "🚪 Abmelden":
    st.session_state.authenticated = False
    st.rerun()

elif menu == "➕ Neues Ticket erstellen":
    st.header("Neues Ticket / Aufgabe anlegen")

    with st.form("new_ticket_form"):
        col1, col2 = st.columns(2)
        with col1:
            titel = st.text_input("Titel der Aufgabe / des Tickets")
            objekt = st.text_input(
                "Objekt / Adresse", "Talstr. 32, 07545 Gera"
            )
            kategorie = st.selectbox(
                "Kategorie",
                [
                    "Reparatur / Handwerker",
                    "Mieteranfrage",
                    "Buchhaltung / Miete",
                    "Hausverwaltung Allgemein",
                    "Behörden / Rechtliches",
                ],
            )
        with col2:
            priorität = st.selectbox(
                "Priorität", ["Niedrig", "Mittel", "Hoch", "🚨 Dringend"]
            )
            status = st.selectbox(
                "Status", ["Offen", "In Bearbeitung", "Erledigt"]
            )
            faelligkeitsdatum = st.date_input(
                "Fälligkeitsdatum", datetime.now()
            )

        beschreibung = st.text_area(
            "Beschreibung & Details",
            placeholder="Genaue Beschreibung des Sachverhalts...",
        )

        uploaded_files = st.file_uploader(
            "Dokumente / Fotos anhängen (PDF, JPG, PNG)",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )

        submit_ticket = st.form_submit_button(
            label="Ticket im System speichern"
        )

        if submit_ticket:
            if not titel:
                st.error("Bitte gib mindestens einen Titel für das Ticket ein!")
            else:
                anhänge = []
                if uploaded_files:
                    for file in uploaded_files:
                        bytes_data = file.read()
                        b64_encoded = base64.b64encode(bytes_data).decode(
                            "utf-8"
                        )
                        anhänge.append(
                            {
                                "name": file.name,
                                "data": b64_encoded,
                                "type": file.type,
                            }
                        )

                neues_ticket = {
                    "id": (
                        max([t["id"] for t in st.session_state.tickets]) + 1
                        if st.session_state.tickets
                        else 1
                    ),
                    "titel": titel,
                    "objekt": objekt,
                    "kategorie": kategorie,
                    "priorität": priorität,
                    "status": status,
                    "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "faellig": faelligkeitsdatum.strftime("%d.%m.%Y"),
                    "beschreibung": beschreibung,
                    "ersteller": st.session_state.user,
                    "anhaenge": anhänge,
                }

                st.session_state.tickets.append(neues_ticket)
                save_tickets(st.session_state.tickets)
                st.success("Ticket erfolgreich erstellt und gespeichert!")

elif menu == "📊 Dashboard & Tickets":
    st.header("Aktive Tickets & Aufgaben")

    suchbegriff = st.text_input(
        "🔍 Volltextsuche (durchsucht Titel, Objekt & Beschreibung)", ""
    )

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_status = st.selectbox(
            "Status", ["Alle", "Offen", "In Bearbeitung", "Erledigt"]
        )
    with col_f2:
        filter_prio = st.selectbox(
            "Priorität", ["Alle", "Niedrig", "Mittel", "Hoch", "🚨 Dringend"]
        )
    with col_f3:
        filter_kat = st.selectbox(
            "Kategorie",
            [
                "Alle",
                "Reparatur / Handwerker",
                "Mieteranfrage",
                "Buchhaltung / Miete",
                "Hausverwaltung Allgemein",
                "Behörden / Rechtliches",
            ],
        )

    tickets = st.session_state.tickets

    if suchbegriff:
        query = suchbegriff.lower()
        tickets = [
            t
            for t in tickets
            if query in t.get("titel", "").lower()
            or query in t.get("beschreibung", "").lower()
            or query in t.get("objekt", "").lower()
        ]

    if filter_status != "Alle":
        tickets = [t for t in tickets if t.get("status") == filter_status]
    if filter_prio != "Alle":
        tickets = [t for t in tickets if t.get("priorität") == filter_prio]
    if filter_kat != "Alle":
        tickets = [t for t in tickets if t.get("kategorie") == filter_kat]

    if not tickets:
        st.info("Keine Tickets gefunden, die den Filterkriterien entsprechen.")
    else:
        for idx, t in enumerate(reversed(tickets)):
            prio_color = (
                "🔴"
                if "Dringend" in t.get("priorität", "")
                else "🟠"
                if t.get("priorität") == "Hoch"
                else "🟡"
                if t.get("priorität") == "Mittel"
                else "🟢"
            )

            with st.expander(
                f"{prio_color} [#{t.get('id', 0)}] {t.get('titel', 'Unbenannt')} — Objekt: {t.get('objekt', '')} ({t.get('status', 'Offen')})"
            ):
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write(f"**Kategorie:** {t.get('kategorie', '')}")
                    st.write(
                        f"**Erstellt am:** {t.get('datum', '')} von"
                        f" {t.get('ersteller', '')}"
                    )
                    st.write(f"**Fällig bis:** {t.get('faellig', '')}")
                with col_info2:
                    st.write(f"**Aktueller Status:** {t.get('status', '')}")
                    st.write(f"**Priorität:** {t.get('priorität', '')}")

                st.markdown("---")

                edit_key = f"edit_desc_mode_{t.get('id', 0)}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False

                st.markdown("**Beschreibung:**")
                if st.session_state[edit_key]:
                    new_desc = st.text_area(
                        "Beschreibung bearbeiten",
                        value=t.get("beschreibung", ""),
                        key=f"desc_area_{t.get('id', 0)}",
                    )
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button(
                            "💾 Ändern speichern",
                            key=f"save_desc_{t.get('id', 0)}",
                        ):
                            t["beschreibung"] = new_desc
                            save_tickets(st.session_state.tickets)
                            st.session_state[edit_key] = False
                            st.success("Beschreibung aktualisiert!")
                            st.rerun()
                    with col_b2:
                        if st.button(
                            "Abbrechen", key=f"cancel_desc_{t.get('id', 0)}"
                        ):
                            st.session_state[edit_key] = False
                            st.rerun()
                else:
                    st.markdown(f"> {t.get('beschreibung', '')}")
                    if st.button(
                        "✏️ Beschreibung bearbeiten",
                        key=f"btn_edit_{t.get('id', 0)}",
                    ):
                        st.session_state[edit_key] = True
                        st.rerun()

                st.markdown("---")
                st.markdown("**Angehängte Dokumente & Dateien:**")

                if t.get("anhaenge"):
                    for f_idx, anhang in enumerate(t["anhaenge"]):
                        file_bytes = base64.b64decode(anhang["data"])
                        col_fn, col_fv, col_fd = st.columns([4, 1.5, 1])
                        with col_fn:
                            st.write(f"📄 {anhang['name']}")
                        with col_fv:
                            show_key = f"show_{t.get('id', 0)}_{f_idx}"
                            if st.button(
                                "👁️ Ansehen",
                                key=f"btn_prev_{t.get('id', 0)}_{f_idx}",
                            ):
                                st.session_state[show_key] = not st.session_state.get(
                                    show_key, False
                                )
                        with col_fd:
                            del_file_key = f"confirm_del_file_{t.get('id', 0)}_{f_idx}"
                            if st.session_state.get(del_file_key, False):
                                st.warning("Datei löschen?")
                                c_y, c_n = st.columns(2)
                                with c_y:
                                    if st.button(
                                        "Ja",
                                        key=f"yes_file_{t.get('id', 0)}_{f_idx}",
                                    ):
                                        t["anhaenge"].pop(f_idx)
                                        save_tickets(st.session_state.tickets)
                                        st.session_state[del_file_key] = False
                                        st.success("Gelöscht!")
                                        st.rerun()
                                with c_n:
                                    if st.button(
                                        "Nein",
                                        key=f"no_file_{t.get('id', 0)}_{f_idx}",
                                    ):
                                        st.session_state[del_file_key] = False
                                        st.rerun()
                            else:
                                if st.button(
                                    "🗑️ Löschen",
                                    key=f"del_file_{t.get('id', 0)}_{f_idx}",
                                ):
                                    st.session_state[del_file_key] = True
                                    st.rerun()

                        if st.session_state.get(
                            f"show_{t.get('id', 0)}_{f_idx}", False
                        ):
                            if "image" in anhang["type"] or anhang[
                                "name"
                            ].lower().endswith((".png", ".jpg", ".jpeg")):
                                st.image(
                                    file_bytes,
                                    caption=anhang["name"],
                                    use_container_width=True,
                                )
                            elif "pdf" in anhang["type"] or anhang[
                                "name"
                            ].lower().endswith(".pdf"):
                                b64_pdf = base64.b64encode(file_bytes).decode(
                                    "utf-8"
                                )
                                pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                            else:
                                st.download_button(
                                    label=(
                                        f"📥 Herunterladen: {anhang['name']}"
                                    ),
                                    data=file_bytes,
                                    file_name=anhang["name"],
                                    mime=anhang["type"],
                                    key=(
                                        f"dl_fallback_{t.get('id', 0)}_{f_idx}"
                                    ),
                                )
                else:
                    st.write("Keine Dateien angehängt.")

                with st.form(key=f"add_more_form_{t.get('id', 0)}"):
                    more_files = st.file_uploader(
                        "Weitere Dateien hinzufügen",
                        type=["pdf", "png", "jpg", "jpeg"],
                        accept_multiple_files=True,
                        key=f"more_upload_{t.get('id', 0)}",
                    )
                    add_more_btn = st.form_submit_button("Dateien hinzufügen")

                    if add_more_btn:
                        if more_files:
                            for file in more_files:
                                bytes_data = file.read()
                                b64_encoded = base64.b64encode(bytes_data).decode(
                                    "utf-8"
                                )
                                t["anhaenge"].append(
                                    {
                                        "name": file.name,
                                        "data": b64_encoded,
                                        "type": file.type,
                                    }
                                )
                            save_tickets(st.session_state.tickets)
                            st.success("Dateien erfolgreich hinzugefügt!")
                            st.rerun()
                        else:
                            st.warning("Bitte wähle erst Dateien aus.")
