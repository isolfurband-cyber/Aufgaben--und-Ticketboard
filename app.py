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

# --- KONFIGURATION & LOGIN ---
# Benutzer und Passwörter (können hier angepasst werden)
USER_CREDENTIALS = {
    "kare": "kare2026",
    "admin": "immobilien32",
}

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
                st.error(
                    "Falscher Benutzername oder falsches Passwort!"
                )
    st.stop()  # Stoppt die Ausführung, solange nicht eingeloggt

# --- DATENPERSISTENZ (JSON DATEI) ---
TICKETS_FILE = "tickets.json"


def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_tickets(tickets):
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=4)


if "tickets" not in st.session_state:
    st.session_state.tickets = load_tickets()

# --- HAUPTAPP (NACH LOGIN) ---
st.title("📋 KARE-Immobilien – Internes Aufgaben- & Ticketboard")
st.markdown(
    f"Eingeloggt als: **{st.session_state.user}** | Talstr. 32, 07545 Gera"
)

# Sidebar für Navigation / Aktionen
menu = st.sidebar.selectbox(
    "Menü",
    ["📊 Dashboard & Tickets", "➕ Neues Ticket erstellen", "🚪 Abmelden"],
)

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

        # Dokumente / Dateien Upload
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
                # Dateien für JSON aufbereiten (Base64 speichern)
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
                    "id": len(st.session_state.tickets) + 1,
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
                st.success(
                    "Ticket erfolgreich erstellt und gespeichert! Du kannst"
                    " es im Dashboard einsehen."
                )

elif menu == "📊 Dashboard & Tickets":
    st.setHeader = st.header("Aktive Tickets & Aufgaben")

    # Filter-Optionen
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_status = st.selectbox(
            "Nach Status filtern",
            ["Alle", "Offen", "In Bearbeitung", "Erledigt"],
        )
    with col_f2:
        filter_prio = st.selectbox(
            "Nach Priorität filtern",
            ["Alle", "Niedrig", "Mittel", "Hoch", "🚨 Dringend"],
        )
    with col_f3:
        filter_kat = st.selectbox(
            "Nach Kategorie filtern",
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

    # Filter anwenden
    if filter_status != "Alle":
        tickets = [t for t in tickets if t["status"] == filter_status]
    if filter_prio != "Alle":
        tickets = [t for t in tickets if t["priorität"] == filter_prio]
    if filter_kat != "Alle":
        tickets = [t for t in tickets if t["kategorie"] == filter_kat]

    if not tickets:
        st.info("Keine Tickets gefunden, die den Filterkriterien entsprechen.")
    else:
        for idx, t in enumerate(reversed(tickets)):
            # Farbliche Kennzeichnung je nach Priorität
            prio_color = (
                "🔴"
                if "Dringend" in t["priorität"]
                else "🟠"
                if t["priorität"] == "Hoch"
                else "🟡"
                if t["priorität"] == "Mittel"
                else "🟢"
            )

            with st.expander(
                f"{prio_color} [#{t['id']}] {t['titel']} — Objekt: {t['objekt']} ({t['status']})"
            ):
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write(f"**Kategorie:** {t['kategorie']}")
                    st.write(f"**Erstellt am:** {t['datum']} von {t['ersteller']}")
                    st.write(f"**Fällig bis:** {t['faellig']}")
                with col_info2:
                    st.write(f"**Aktueller Status:** {t['status']}")
                    st.write(f"**Priorität:** {t['priorität']}")

                st.markdown(f"**Beschreibung:**\n> {t['beschreibung']}")

                # Anhänge anzeigen / herunterladen
                if t.get("anhaenge"):
                    st.markdown("**Angehängte Dokumente:**")
                    for anhang in t["anhaenge"]:
                        file_bytes = base64.b64decode(anhang["data"])
                        st.download_button(
                            label=f"📥 Herunterladen: {anhang['name']}",
                            data=file_bytes,
                            file_name=anhang["name"],
                            mime=anhang["type"],
                            key=f"dl_{t['id']}_{anhang['name']}_{idx}",
                        )

                # Status direkt ändern oder Ticket löschen
                st.markdown("---")
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    neuer_status = st.selectbox(
                        "Status ändern",
                        ["Offen", "In Bearbeitung", "Erledigt"],
                        index=[
                            "Offen",
                            "In Bearbeitung",
                            "Erledigt",
                        ].index(t["status"]),
                        key=f"status_select_{t['id']}_{idx}",
                    )
                    if neuer_status != t["status"]:
                        t["status"] = neuer_status
                        save_tickets(st.session_state.tickets)
                        st.success("Status aktualisiert!")
                        st.rerun()

                with col_act2:
                    if st.button(
                        "🗑️ Ticket löschen", key=f"del_{t['id']}_{idx}"
                    ):
                        st.session_state.tickets = [
                            item
                            for item in st.session_state.tickets
                            if item["id"] != t["id"]
                        ]
                        save_tickets(st.session_state.tickets)
                        st.success("Ticket gelöscht!")
                        st.rerun()
