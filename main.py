# main.py
import streamlit as st
from fpdf import FPDF
import io
import time

# -----------------------------
# Irregular verbs
IRREGULAR_VERBS = {
    "be": {"past": ["was", "were"], "pp": "been"},
    "have": {"past": "had", "pp": "had"},
    "do": {"past": "did", "pp": "done"},
    "say": {"past": "said", "pp": "said"},
    "go": {"past": "went", "pp": "gone"},
    "get": {"past": "got", "pp": "got"},
    "make": {"past": "made", "pp": "made"},
    "know": {"past": "knew", "pp": "known"},
    "think": {"past": "thought", "pp": "thought"},
    "take": {"past": "took", "pp": "taken"},
    "see": {"past": "saw", "pp": "seen"},
    "come": {"past": "came", "pp": "come"},
    "give": {"past": "gave", "pp": "given"},
    "find": {"past": "found", "pp": "found"},
    "tell": {"past": "told", "pp": "told"},
    "begin": {"past": "began", "pp": "begun"},
    "bring": {"past": "brought", "pp": "brought"},
    "hold": {"past": "held", "pp": "held"},
    "run": {"past": "ran", "pp": "run"},
    "write": {"past": "wrote", "pp": "written"},
}

# Regular verbs
REGULAR_VERBS = [
    "walk", "play", "talk", "work", "call", "try",
    "ask", "use", "look", "love", "need", "move",
    "open", "close", "start", "stop", "live", "help", "wash", "study"
]

ALL_VERBS = sorted(list(IRREGULAR_VERBS.keys()) + REGULAR_VERBS)

PERSONS = [
    ("I", "am", "was", False),
    ("You", "are", "were", False),
    ("He/She/It", "is", "was", True),
    ("We", "are", "were", False),
    ("You (pl)", "are", "were", False),
    ("They", "are", "were", False),
]

# -----------------------------
# Helpers for regular verbs
def ends_with_cvc(word):
    vowels = "aeiou"
    if len(word) < 3:
        return False
    return word[-1] not in vowels and word[-2] in vowels and word[-3] not in vowels

def make_third_person_s(verb):
    if verb.endswith(("s", "sh", "ch", "x", "z", "o")):
        return verb + "es"
    if verb.endswith("y") and verb[-2] not in "aeiou":
        return verb[:-1] + "ies"
    return verb + "s"

def make_past_and_pp(verb):
    if verb.endswith("e"):
        past = verb + "d"
    elif verb.endswith("y") and verb[-2] not in "aeiou":
        past = verb[:-1] + "ied"
    elif ends_with_cvc(verb) and verb[-1] not in ("w","x","y"):
        past = verb + verb[-1] + "ed"
    else:
        past = verb + "ed"
    return past, past

def make_ing(verb):
    if verb.endswith("ie"):
        return verb[:-2] + "ying"
    if verb.endswith("e") and not verb.endswith("ee"):
        return verb[:-1] + "ing"
    if ends_with_cvc(verb) and verb[-1] not in ("w","x","y"):
        return verb + verb[-1] + "ing"
    return verb + "ing"

# -----------------------------
# Conjugation functions
def present_simple(subject, verb, is_third):
    return f"{subject} {make_third_person_s(verb) if is_third else verb}"

def past_simple(subject, verb):
    if verb in IRREGULAR_VERBS:
        p = IRREGULAR_VERBS[verb]["past"]
        if isinstance(p, list):
            return f"{subject} {p[0]}" if subject in ("I","He/She/It") else f"{subject} {p[1]}"
        return f"{subject} {p}"
    else:
        past, _ = make_past_and_pp(verb)
        return f"{subject} {past}"

def future_simple(subject, verb):
    return f"{subject} will {verb}"

def present_continuous(subject, be_form, ing):
    return f"{subject} {be_form} {ing}"

def past_continuous(subject, was_or_were, ing):
    return f"{subject} {was_or_were} {ing}"

def future_continuous(subject, ing):
    return f"{subject} will be {ing}"

def present_perfect(subject, pp, is_third):
    aux = "has" if is_third else "have"
    return f"{subject} {aux} {pp}"

def past_perfect(subject, pp):
    return f"{subject} had {pp}"

def future_perfect(subject, pp):
    return f"{subject} will have {pp}"

# -----------------------------
# Build conjugation list
def conjugate_and_return_lines(verb):
    lines = []
    verb = verb.strip().lower()
    if verb not in ALL_VERBS:
        return [f"⚠️ Το ρήμα '{verb}' δεν υπάρχει στη λίστα."]

    if verb == "be":
        for subj, be_pres, be_past, is_third in PERSONS:
            lines.append(f"**{subj}**")
            lines.append(f"Present Simple: {subj} {be_pres}")
            lines.append(f"Past Simple: {subj} {be_past}")
            lines.append(f"Future Simple: {subj} will be\n")
        return lines

    if verb in IRREGULAR_VERBS:
        irr = IRREGULAR_VERBS[verb]
        past = irr["past"]
        pp = irr["pp"]
    else:
        past, pp = make_past_and_pp(verb)
    
    ing = make_ing(verb)

    for subj, be_pres, be_past, is_third in PERSONS:
        lines.append(f"**{subj}**")
        lines.append(f"Present Simple: {present_simple(subj, verb, is_third)}")
        lines.append(f"Past Simple: {past_simple(subj, verb)}")
        lines.append(f"Future Simple: {future_simple(subj, verb)}")
        lines.append(f"Present Continuous: {present_continuous(subj, be_pres, ing)}")
        lines.append(f"Past Continuous: {past_continuous(subj, be_past, ing)}")
        lines.append(f"Future Continuous: {future_continuous(subj, ing)}")
        lines.append(f"Present Perfect: {present_perfect(subj, pp, is_third)}")
        lines.append(f"Past Perfect: {past_perfect(subj, pp)}")
        lines.append(f"Future Perfect: {future_perfect(subj, pp)}\n")

    return lines

# -----------------------------
# PDF generation
def build_pdf_bytes(verb, lines, progress_callback=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Conjugation of '{verb}'", ln=True, align='C')
    pdf.ln(5)
    total = max(1, len(lines))
    for i, line in enumerate(lines):
        pdf.multi_cell(0, 8, line)
        time.sleep(0.01)
        if progress_callback:
            progress_callback(int((i + 1) / total * 100))
    s = pdf.output(dest='S').encode('latin-1')
    return s

# -----------------------------
# Streamlit UI
st.set_page_config(page_title="English Verb Conjugator", layout="wide")
st.title("English Verb Conjugator — Streamlit Web App")

st.sidebar.header("Search & controls")
start_letter = st.sidebar.selectbox("Filter by starting letter:", ["All"] + sorted({w[0].upper() for w in ALL_VERBS}))
filtered = ALL_VERBS if start_letter == "All" else [w for w in ALL_VERBS if w.startswith(start_letter.lower())]

with st.sidebar.expander("Available verbs"):
    st.write(", ".join(filtered))

col1, col2 = st.columns([2, 1])
with col1:
    verb_input = st.text_input("Type a verb:", value="", placeholder="e.g. go")
    chosen = st.selectbox("Or pick from list:", [""] + filtered)
    verb = (verb_input.strip() or chosen).strip().lower()
with col2:
    conjugate_btn = st.button("Conjugate")
    list_btn = st.button("List verbs")
    clear_btn = st.button("Clear")

results_area = st.empty()

if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "last_lines" not in st.session_state:
    st.session_state.last_lines = []
if "last_verb" not in st.session_state:
    st.session_state.last_verb = ""

if list_btn:
    results_area.markdown("**📘 Available verbs:**\n\n" + ", ".join(filtered))
elif clear_btn:
    st.session_state.last_lines = []
    st.session_state.pdf_bytes = None
    st.session_state.last_verb = ""
    results_area.empty()
elif conjugate_btn:
    if not verb:
        st.warning("Please type or select a verb first.")
    else:
        lines = conjugate_and_return_lines(verb)
        st.session_state.last_lines = lines
        st.session_state.last_verb = verb
        st.session_state.pdf_bytes = None
        results_area.markdown("\n".join(lines))

if st.session_state.last_lines:
    st.markdown("---")
    st.write(f"Selected verb: **{st.session_state.last_verb}**")

    save_col1, save_col2 = st.columns([1, 3])
    with save_col1:
        save_clicked = st.button("Save to PDF")

    if save_clicked:
        prog = st.progress(0)
        def cb(p):
            prog.progress(p)
        pdf_bytes = build_pdf_bytes(st.session_state.last_verb, st.session_state.last_lines, cb)
        st.session_state.pdf_bytes = pdf_bytes
        prog.progress(100)
        time.sleep(0.3)
        prog.empty()
        st.success("✅ PDF ready to download!")

    if st.session_state.pdf_bytes:
        st.download_button(
            label="Download PDF",
            data=st.session_state.pdf_bytes,
            file_name=f"{st.session_state.last_verb}_conjugation.pdf",
            mime="application/pdf",
        )
        if st.button("Done (clear)"):
            st.session_state.last_lines = []
            st.session_state.pdf_bytes = None
            st.session_state.last_verb = ""
            results_area.empty()
            st.experimental_rerun()
