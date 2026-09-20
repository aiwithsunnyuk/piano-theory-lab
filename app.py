from database import SessionLocal, init_db
from models import User, SavedProgression

import streamlit as st
import streamlit.components.v1 as components
import music21 as m21

# --- SESSION STATE INITIALIZATION ---
if "override_chord" not in st.session_state:
    st.session_state.override_chord = None
if "current_progression" not in st.session_state:
    st.session_state.current_progression = None
if "movement_label" not in st.session_state:
    st.session_state.movement_label = None
if "autoplay_chord" not in st.session_state:
    st.session_state.autoplay_chord = False

def clear_override():
    st.session_state.override_chord = None

# Sidebar: Controls
st.sidebar.header("Scale & Chord Builder")
root_note = st.sidebar.selectbox("Root Note", ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"], on_change=clear_override)
level = st.sidebar.radio("Skill Level", ["Beginner (Triads)", "Intermediate (7ths)", "Advanced (Extensions & Modes)"], on_change=clear_override)

# Compute chord notes using music21
chord_types = {
    "Beginner (Triads)": ["major", "minor", "diminished"],
    "Intermediate (7ths)": ["maj7", "m7", "7", "m7b5"],
    "Advanced (Extensions & Modes)": ["maj9", "m9", "13", "7alt"]
}

selected_type = st.sidebar.selectbox("Chord Quality", chord_types[level], on_change=clear_override)


# Convert friendly dropdown names to standard music notation
m21_suffix = selected_type
if selected_type == "major": 
    m21_suffix = ""
elif selected_type == "minor": 
    m21_suffix = "m"
elif selected_type == "diminished": 
    m21_suffix = "dim"
elif selected_type == "maj9":
    m21_suffix = "M9"
elif selected_type == "7alt":
    m21_suffix = "7#5#9"

# --- SIDEBAR: PRACTICE HISTORY ---
st.sidebar.divider()
st.sidebar.header("📚 Practice History")

# Open a database session to fetch saved progressions
with SessionLocal() as db:
    # Query all progressions for DemoUser, ordering by newest first
    saved_progs = db.query(SavedProgression).join(User).filter(User.username == "DemoUser").order_by(SavedProgression.id.desc()).all()
    
    if saved_progs:
        for prog in saved_progs:
            # Create a clean dropdown card for each saved progression
            with st.sidebar.expander(f"{prog.root_note} | {prog.movement_label.split('(')[0].strip()}"):
                st.write(f"**Type:** {prog.movement_label}")
                st.write(f"**Chords:** {', '.join([c[0] for c in prog.chord_sequence])}")
                
                # Put Load and Delete buttons side-by-side
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Load", key=f"load_{prog.id}", use_container_width=True):
                        st.session_state.movement_label = prog.movement_label
                        st.session_state.current_progression = prog.chord_sequence
                        st.session_state.override_chord = None
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{prog.id}", use_container_width=True):
                        db.delete(prog)
                        db.commit()
                        st.rerun()
    else:
        st.sidebar.info("No saved progressions yet. Generate and save one to see it here!")
    
chord_symbol = f"{root_note}{m21_suffix}"

# OVERRIDE: If user clicked a progression chord, analyze that instead
if st.session_state.override_chord:
    chord_symbol = st.session_state.override_chord

st.subheader(f"Analyzing: **{chord_symbol}**")
if st.session_state.override_chord:
    st.info("💡 Showing chord from your generated practice progression. Change the sidebar controls to clear this.")

try:
    c = m21.harmony.ChordSymbol(chord_symbol)
    notes_in_chord = [p.nameWithOctave for p in c.pitches]
    intervals = [p.name for p in c.pitches]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Pitches:** `{', '.join(notes_in_chord)}`")
        st.markdown(f"**Interval Structure:** `{', '.join(intervals)}`")
    with col2:
        st.markdown(f"**Common Usage:** Used heavily in progressions resolving to {m21.pitch.Pitch(root_note).transpose('P4').name}.")
    
    st.divider()

    # SVG 88-Key Piano Representation (Now with MIDI mapping)
    def render_88_keyboard(active_pitches):
        white_key_width = 16
        white_key_height = 80
        black_key_width = 10
        black_key_height = 50
        
        # Build 88 notes with corresponding MIDI numbers (A0 = 21)
        notes = []
        midi_val = 21
        for oct in range(0, 9):
            for n in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']:
                if oct == 0 and n not in ['A', 'A#', 'B']: continue
                if oct == 8 and n != 'C': continue
                notes.append((n, oct, '#' in n, midi_val))
                midi_val += 1
                
        svg_white, svg_black = [], []
        white_x = 0
        
        active_set = [p.nameWithOctave for p in active_pitches]
        
        for note, oct, is_black, midi_num in notes:
            name_octave = f"{note}{oct}"
            is_active = name_octave in active_set
            
            if not is_black:
                fill = "#4CAF50" if is_active else "#FFFFFF"
                # Added id and data-default so JS can find and reset the keys
                svg_white.append(f'<rect id="midi-{midi_num}" data-default="{fill}" x="{white_x}" y="0" width="{white_key_width}" height="{white_key_height}" fill="{fill}" stroke="#333" stroke-width="1" rx="2" style="transition: fill 0.05s;"/>')
                
                if note == 'C':
                    text_x = white_x + (white_key_width / 2)
                    text_y = white_key_height - 6
                    text_color = "#FFFFFF" if is_active else "#666666"
                    svg_white.append(f'<text x="{text_x}" y="{text_y}" font-family="sans-serif" font-size="7" font-weight="bold" fill="{text_color}" text-anchor="middle" pointer-events="none">C{oct}</text>')
                
                white_x += white_key_width
            else:
                fill = "#81C784" if is_active else "#222222"
                bx = white_x - (black_key_width / 2)
                svg_black.append(f'<rect id="midi-{midi_num}" data-default="{fill}" x="{bx}" y="0" width="{black_key_width}" height="{black_key_height}" fill="{fill}" stroke="#111" stroke-width="1" rx="1" style="transition: fill 0.05s;"/>')
                
        total_width = 52 * white_key_width
        svg_content = "".join(svg_white) + "".join(svg_black)
        return f'<svg width="100%" height="120px" viewBox="0 -5 {total_width} {white_key_height + 10}" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">{svg_content}</svg>'

    st.markdown(render_88_keyboard(c.pitches), unsafe_allow_html=True)
    
    # Generate the JS array of notes dynamically from the selected chord
    notes_to_play = [p.nameWithOctave for p in c.pitches]
    
    # Check if we should auto-play based on a recent click
    auto_play_js = "true" if st.session_state.get("autoplay_chord") else "false"
    st.session_state.autoplay_chord = False # Reset immediately so it only plays once
    
    # Build Tone.js Audio Engine, Play Button, and Web MIDI Listener
    audio_html = f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
    <div style="display: flex; justify-content: center; gap: 15px; margin-top: 20px;">
        <button id="play-btn" style="background-color: #4CAF50; color: white; border: none; padding: 12px 30px; font-size: 18px; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.2); transition: 0.2s;">
            🔊 Play Chord
        </button>
        <div id="midi-status" style="padding: 12px 20px; font-size: 16px; border-radius: 8px; background-color: #f0f0f0; color: #555; border: 1px solid #ccc; font-family: sans-serif; display: flex; align-items: center;">
            🔌 Waiting for MIDI Keyboard...
        </div>
    </div>
    <script>
        // --- 1. AUDIO SETUP ---
        const piano = new Tone.Sampler({{
            urls: {{ "C2": "C2.mp3", "C3": "C3.mp3", "C4": "C4.mp3", "C5": "C5.mp3", "C6": "C6.mp3" }},
            release: 1,
            baseUrl: "https://tonejs.github.io/audio/salamander/"
        }}).toDestination();

        // Autoplay the chord if triggered by the progression button
        Tone.loaded().then(() => {{
            if ({auto_play_js}) {{
                Tone.start().then(() => {{
                    piano.triggerAttackRelease({notes_to_play}, "2n");
                }});
            }}
        }});

        document.getElementById('play-btn').addEventListener('click', async () => {{
            await Tone.start();
            const notes = {notes_to_play};
            piano.triggerAttackRelease(notes, "2n");
            
            const btn = document.getElementById('play-btn');
            btn.style.transform = "scale(0.95)";
            setTimeout(() => btn.style.transform = "scale(1)", 150);
        }});

        // --- 2. WEB MIDI SETUP ---
        const statusDiv = document.getElementById('midi-status');

        if (navigator.requestMIDIAccess) {{
            navigator.requestMIDIAccess().then(onMIDISuccess, onMIDIFailure);
        }} else {{
            statusDiv.innerHTML = '❌ Web MIDI not supported in this browser';
        }}

        function onMIDISuccess(midiAccess) {{
            const inputs = midiAccess.inputs.values();
            let deviceCount = 0;
            for (let input of inputs) {{
                input.onmidimessage = getMIDIMessage;
                deviceCount++;
            }}
            if (deviceCount > 0) {{
                statusDiv.innerHTML = '🎹 MIDI Connected';
                statusDiv.style.backgroundColor = '#E8F5E9';
                statusDiv.style.color = '#2E7D32';
                statusDiv.style.borderColor = '#A5D6A7';
            }}
            midiAccess.onstatechange = (e) => {{
                if (e.port.type === "input" && e.port.state === "connected") {{
                    e.port.onmidimessage = getMIDIMessage;
                    statusDiv.innerHTML = '🎹 ' + e.port.name + ' Connected';
                    statusDiv.style.backgroundColor = '#E8F5E9';
                    statusDiv.style.color = '#2E7D32';
                    statusDiv.style.borderColor = '#A5D6A7';
                }} else if (e.port.type === "input" && e.port.state === "disconnected") {{
                    statusDiv.innerHTML = '🔌 MIDI Disconnected';
                    statusDiv.style.backgroundColor = '#f0f0f0';
                    statusDiv.style.color = '#555';
                    statusDiv.style.borderColor = '#ccc';
                }}
            }};
        }}

        function onMIDIFailure() {{ statusDiv.innerHTML = '❌ MIDI Access Denied'; }}

        function getMIDIMessage(message) {{
            const command = message.data[0];
            const note = message.data[1];
            const velocity = (message.data.length > 2) ? message.data[2] : 0;
            if (command === 144 && velocity > 0) highlightKey(note, true);
            else if (command === 128 || (command === 144 && velocity === 0)) highlightKey(note, false);
        }}

        function highlightKey(midiNumber, isDown) {{
            const key = window.parent.document.getElementById('midi-' + midiNumber);
            if (key) {{
                if (isDown) key.setAttribute('fill', '#FF9800');
                else key.setAttribute('fill', key.getAttribute('data-default'));
            }}
        }}
    </script>
    """
    
    components.html(audio_html, height=80)

except Exception as e:
    st.info("Select a standard root and quality to inspect harmonic structure.")

# --- AI INSTRUCTOR: PROGRESSION GENERATOR ---
st.divider()
st.subheader("🤖 AI Practice Instructor")
st.markdown("Generate a custom 4-chord progression tailored to your current skill level.")

def mock_llm_chain(root, level):
    import random
    def tr(interval):
        return m21.pitch.Pitch(root).transpose(interval).name
    
    if "Beginner" in level:
        progressions = [
            ("I - IV - V - I (Standard Pop)", [(f"{root}", "I"), (tr('P4'), "IV"), (tr('P5'), "V"), (f"{root}", "I")]),
            ("I - V - vi - IV (Modern Worship)", [(f"{root}", "I"), (tr('P5'), "V"), (tr('M6')+"m", "vi"), (tr('P4'), "IV")]),
            ("vi - IV - I - V (Emotional Worship)", [(tr('M6')+"m", "vi"), (tr('P4'), "IV"), (f"{root}", "I"), (tr('P5'), "V")]),
            ("I - vi - IV - V (50s Ballad)", [(f"{root}", "I"), (tr('M6')+"m", "vi"), (tr('P4'), "IV"), (tr('P5'), "V")]),
            ("I - IV - I - V (Folk/Country)", [(f"{root}", "I"), (tr('P4'), "IV"), (f"{root}", "I"), (tr('P5'), "V")])
        ]
    elif "Intermediate" in level:
        progressions = [
            ("I - vi7 - ii7 - V7 (Jazz Turnaround)", [(f"{root}maj7", "Imaj7"), (tr('M6')+"m7", "vi7"), (tr('M2')+"m7", "ii7"), (tr('P5')+"7", "V7")]),
            ("I - Iaug - vi - IV (Augmented Passing)", [(f"{root}", "I"), (f"{root}aug", "Iaug"), (tr('M6')+"m", "vi"), (tr('P4'), "IV")]),
            ("I - iii - IV - V (Mediant/3rd Movement)", [(f"{root}", "I"), (tr('M3')+"m", "iii"), (tr('P4'), "IV"), (tr('P5'), "V")]),
            ("ii - V7 - I - viidim (Diminished Leading)", [(tr('M2')+"m", "ii"), (tr('P5')+"7", "V7"), (f"{root}", "I"), (tr('M7')+"dim", "viidim")]),
            ("i - iv - V - i (Minor Walk)", [(f"{root}m", "i"), (tr('P4')+"m", "iv"), (tr('P5')+"7", "V7"), (f"{root}m", "i")])
        ]
    else:
        progressions = [
            ("Imaj9 - vi13 - ii9 - V7alt (Extended Jazz)", [(f"{root}maj9", "Imaj9"), (tr('M6')+"13", "vi13"), (tr('M2')+"m9", "ii9"), (tr('P5')+"7#5#9", "V7alt")]),
            ("i9 - bIIImaj7 - iv9 - V13 (Minor to 13th)", [(f"{root}m9", "i9"), (tr('m3')+"maj7", "bIIImaj7"), (tr('P4')+"m9", "iv9"), (tr('P5')+"13", "V13")]),
            ("Imaj13 - bVImaj9 - bIImaj9 - Imaj13 (Tritone Sub)", [(f"{root}maj13", "Imaj13"), (tr('m6')+"maj9", "bVImaj9"), (tr('m2')+"maj9", "bIImaj9"), (f"{root}maj13", "Imaj13")]),
            ("I - vdim - ii9 - V7#9 (Diminished Sub)", [(f"{root}maj7", "Imaj7"), (tr('P5')+"dim", "vdim"), (tr('M2')+"m9", "ii9"), (tr('P5')+"7#9", "V7#9")])
        ]
    return random.choice(progressions)

# 1. Generate & Save to Memory
if st.button("🎲 Generate Practice Progression"):
    with st.spinner("Analyzing theory and building progression..."):
        movement_label, progression = mock_llm_chain(root_note, level)
        st.session_state.movement_label = movement_label
        st.session_state.current_progression = progression
        st.session_state.override_chord = None
        st.rerun()

# 2. Render from Memory
if st.session_state.current_progression:
    st.success(f"**Progression Generated!** You are practicing a **{st.session_state.movement_label}** movement.")
    
    cols = st.columns(4)
    for i, (chord_str, numeral) in enumerate(st.session_state.current_progression):
        with cols[i]:
            st.markdown(
                f"""
                <div style="background-color: #2e2e2e; padding: 20px; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 15px;">
                    <h2 style="margin: 0; color: #4CAF50;">{chord_str}</h2>
                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #aaa;">Bar {i+1}</p>
                    <p style="margin: 8px 0 0 0; font-size: 18px; font-weight: bold; color: #FF9800;">{numeral}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Interactive Button to trigger the visualizer
            if st.button(f"🔍 Analyze Keys", key=f"btn_{i}_{chord_str}", use_container_width=True):
                st.session_state.override_chord = chord_str
                st.rerun()

    st.write("") # Add some vertical spacing
    
    # Place Save and Clear buttons next to each other
    save_col, clear_col = st.columns(2)
    
    with save_col:
        if st.button("💾 Save to Favorites", use_container_width=True):
            with SessionLocal() as db:
                user = db.query(User).filter(User.username == "DemoUser").first()
                if not user:
                    user = User(username="DemoUser", current_skill_level="Beginner")
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                
                new_prog = SavedProgression(
                    user_id=user.id,
                    root_note=root_note,
                    movement_label=st.session_state.movement_label,
                    chord_sequence=list(st.session_state.current_progression) 
                )
                db.add(new_prog)
                db.commit()
                
                st.toast("✅ Progression saved to database!")
                st.rerun() # Refresh so it immediately shows up in the sidebar
                
    with clear_col:
        if st.button("❌ Clear View", use_container_width=True):
            st.session_state.current_progression = None
            st.session_state.movement_label = None
            st.session_state.override_chord = None
            st.rerun()
            
            st.toast("✅ Progression saved to database!")