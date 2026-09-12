import streamlit as st
import random
import json
import time
from database import (
    init_database, create_user, get_user_by_username, add_vocabularies,
    get_vocabularies_by_language, get_all_languages, record_learning,
    get_user_learned_count, save_quiz_result, get_ranking, get_user_rank,
    get_user_learned_by_language, get_user_best_quiz_score,
    add_grammars, get_grammars_by_language, add_user_vocabulary,
    get_user_vocabularies, add_user_grammar, get_user_grammars,
    get_all_grammars_by_language
)
from vocabularies import VOCABULARIES, GRAMMARS

init_database()

for language, words in VOCABULARIES.items():
    add_vocabularies(language, words)

for language, grammars in GRAMMARS.items():
    add_grammars(language, grammars)

st.set_page_config(
    page_title="온어 - 언어 학습",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap');

    * {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        color: #333;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }

    .vocab-card {
        background: white;
        border: 2px solid #667eea;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        text-align: center;
    }

    .vocab-card:hover {
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
    }

    .ranking-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-left: 4px solid #667eea;
        padding: 16px;
        margin: 12px 0;
        border-radius: 8px;
    }

    .ranking-card.user {
        background: linear-gradient(135deg, #667eea30 0%, #764ba230 100%);
        border-left-color: #764ba2;
        font-weight: 600;
    }

    .metric-box {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }

    h1, h2, h3 {
        color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None

def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("# 🌍 온어 - 언어 학습 앱")
        st.markdown("---")

        tab1, tab2 = st.tabs(["로그인", "회원가입"])

        with tab1:
            st.subheader("로그인")
            username = st.text_input("사용자명", key="login_username")

            if st.button("로그인", use_container_width=True):
                if username.strip():
                    user = get_user_by_username(username)
                    if user:
                        st.session_state.user_id = user['id']
                        st.session_state.username = username
                        st.success(f"환영합니다, {username}님! 🎉")
                        st.rerun()
                    else:
                        st.error("사용자를 찾을 수 없습니다.")
                else:
                    st.error("사용자명을 입력해주세요.")

        with tab2:
            st.subheader("회원가입")
            new_username = st.text_input("새 사용자명", key="signup_username")

            if st.button("가입하기", use_container_width=True):
                if new_username.strip():
                    user_id = create_user(new_username)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = new_username
                        st.success(f"가입되었습니다, {new_username}님! 🎉")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 사용자명입니다.")
                else:
                    st.error("사용자명을 입력해주세요.")

def show_main_app():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.markdown("---")

        page = st.radio(
            "메뉴",
            ["🏠 대시보드", "📚 단어 학습", "📝 문법", "🎯 퀴즈", "🏆 랭킹", "👥 프로필", "➕ 추가하기"]
        )

        st.markdown("---")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()

    if page == "🏠 대시보드":
        show_dashboard()
    elif page == "📚 단어 학습":
        show_learning()
    elif page == "📝 문법":
        show_grammar()
    elif page == "🎯 퀴즈":
        show_quiz()
    elif page == "🏆 랭킹":
        show_ranking()
    elif page == "👥 프로필":
        show_profile()
    elif page == "➕ 추가하기":
        show_add_content()

def show_dashboard():
    st.title("🏠 대시보드")

    user_id = st.session_state.user_id
    total_learned = get_user_learned_count(user_id)
    user_rank = get_user_rank(user_id)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class='metric-box'>
            <h3 style='color: #667eea;'>📖 배운 단어</h3>
            <h1 style='color: #333; text-align: center;'>{total_learned}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-box'>
            <h3 style='color: #764ba2;'>🏆 현재 순위</h3>
            <h1 style='color: #333; text-align: center;'>{user_rank}위</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        best_score = get_user_best_quiz_score(user_id)
        st.markdown(f"""
        <div class='metric-box'>
            <h3 style='color: #667eea;'>⭐ 최고 점수</h3>
            <h1 style='color: #333; text-align: center;'>{best_score}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🎯 상위 10명")

    ranking = get_ranking()[:10]
    for idx, user in enumerate(ranking, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"#{idx}"
        highlight = "user" if user['id'] == user_id else ""
        st.markdown(f"""
        <div class='ranking-card {highlight}'>
            <strong>{medal} {user['username']}</strong> - 배운 단어: {user['learned_count']}개
        </div>
        """, unsafe_allow_html=True)

def show_grammar():
    st.title("📝 문법")

    languages = get_all_languages()
    selected_language = st.selectbox("언어 선택", languages, key="grammar_language")

    if selected_language:
        grammars = get_all_grammars_by_language(selected_language)
        user_grammars = get_user_grammars(st.session_state.user_id, selected_language)

        all_grammars = list(grammars) + list(user_grammars)

        if not all_grammars:
            st.warning("해당 언어의 문법이 없습니다.")
            return

        st.markdown(f"### {selected_language} 문법 ({len(all_grammars)}개)")

        if 'current_grammar_idx' not in st.session_state:
            st.session_state.current_grammar_idx = 0

        if st.session_state.current_grammar_idx < len(all_grammars):
            current_grammar = all_grammars[st.session_state.current_grammar_idx]
            options = json.loads(current_grammar['options']) if isinstance(current_grammar['options'], str) else current_grammar['options']

            st.markdown(f"""
            <div class='vocab-card'>
                <h3 style='color: #667eea;'>{current_grammar['title']}</h3>
                <h4 style='color: #666;'>문제: {current_grammar['question']}</h4>
            </div>
            """, unsafe_allow_html=True)

            cols = st.columns(2)
            selected_option = None

            for i, option in enumerate(options):
                with cols[i % 2]:
                    if st.button(f"{option}", use_container_width=True, key=f"grammar_opt_{i}"):
                        if option == current_grammar['correct_answer']:
                            st.success("정답! ✅")
                            st.info(f"설명: {current_grammar['explanation']}")
                        else:
                            st.error(f"틀렸습니다. 정답: {current_grammar['correct_answer']}")
                            st.info(f"설명: {current_grammar['explanation']}")

                        st.session_state.current_grammar_idx += 1
                        st.sleep(1.5)
                        st.rerun()

            st.markdown(f"**진행: {st.session_state.current_grammar_idx + 1} / {len(all_grammars)}**")
        else:
            st.success(f"모든 {selected_language} 문법을 학습했습니다! 🎉")
            if st.button("처음부터 다시"):
                st.session_state.current_grammar_idx = 0
                st.rerun()

def show_learning():
    st.title("📚 단어 학습")

    languages = get_all_languages()
    selected_language = st.selectbox("언어 선택", languages)

    if selected_language:
        vocabularies = get_vocabularies_by_language(selected_language)

        if not vocabularies:
            st.warning("해당 언어의 단어가 없습니다.")
            return

        st.markdown(f"### {selected_language} ({len(vocabularies)}개 단어)")

        if 'current_word_idx' not in st.session_state:
            st.session_state.current_word_idx = 0

        if 'learning_complete' not in st.session_state:
            st.session_state.learning_complete = False

        if not st.session_state.learning_complete and st.session_state.current_word_idx < len(vocabularies):
            current_word = vocabularies[st.session_state.current_word_idx]

            st.markdown(f"""
            <div class='vocab-card'>
                <h2 style='color: #667eea;'>{current_word['word']}</h2>
                <h4 style='color: #666;'>뜻: {current_word['definition']}</h4>
                <p style='color: #999; font-style: italic;'>예문: {current_word['example']}</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col2:
                if st.button("✅ 학습 완료", use_container_width=True):
                    user_id = st.session_state.user_id
                    word_id = current_word['id']

                    if record_learning(user_id, word_id):
                        st.success("학습했습니다! 👍")
                    else:
                        st.info("이미 학습한 단어입니다.")

                    st.session_state.current_word_idx += 1

                    if st.session_state.current_word_idx >= len(vocabularies):
                        st.session_state.learning_complete = True
                        st.session_state.word_test_idx = 0
                        st.session_state.word_test_score = 0

                    time.sleep(0.5)
                    st.rerun()

            st.markdown(f"**진행: {st.session_state.current_word_idx + 1} / {len(vocabularies)}**")

        elif st.session_state.learning_complete:
            show_word_test(vocabularies, selected_language)

def show_word_test(vocabularies, language):
    st.markdown("## 📝 단어 테스트")
    st.markdown(f"학습을 완료했습니다! 이제 **{language}** 단어 테스트를 풀어보세요!")
    st.markdown("---")

    num_test_questions = min(len(vocabularies), 10)

    if 'word_test_idx' not in st.session_state:
        st.session_state.word_test_idx = 0

    if 'word_test_score' not in st.session_state:
        st.session_state.word_test_score = 0

    if st.session_state.word_test_idx < num_test_questions:
        test_word = random.choice(vocabularies)
        all_options = random.sample(vocabularies, min(4, len(vocabularies)))

        if test_word not in all_options:
            all_options[0] = test_word

        random.shuffle(all_options)

        st.progress(st.session_state.word_test_idx / num_test_questions)
        st.markdown(f"### 문제 {st.session_state.word_test_idx + 1} / {num_test_questions}")
        st.markdown(f"**'{test_word['word']}'의 뜻은?**")

        cols = st.columns(2)
        for i, option in enumerate(all_options):
            with cols[i % 2]:
                if st.button(f"{option['definition']}", use_container_width=True, key=f"word_test_opt_{i}"):
                    if option['id'] == test_word['id']:
                        st.session_state.word_test_score += 1
                        st.success("정답! ✅")
                    else:
                        st.error(f"틀렸습니다. 정답: {test_word['definition']}")

                    st.session_state.word_test_idx += 1
                    st.sleep(1)
                    st.rerun()
    else:
        score = st.session_state.word_test_score
        total = num_test_questions
        percentage = int(score / total * 100) if total > 0 else 0

        st.markdown(f"""
        <div class='metric-box' style='text-align: center;'>
            <h2>테스트 완료! 🎉</h2>
            <h1 style='color: #667eea;'>{score} / {total}</h1>
            <h3>정답률: {percentage}%</h3>
        </div>
        """, unsafe_allow_html=True)

        if percentage >= 80:
            st.balloons()
            st.success("완벽합니다! 이 언어를 마스터했습니다! 🏆")
        elif percentage >= 60:
            st.info("좋습니다! 조금 더 연습하면 완벽할 거예요! 💪")
        else:
            st.warning("더 많이 연습이 필요합니다. 다시 도전해보세요! 📚")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("다시 풀기", use_container_width=True):
                st.session_state.word_test_idx = 0
                st.session_state.word_test_score = 0
                st.rerun()

        with col2:
            if st.button("다른 언어 학습", use_container_width=True):
                st.session_state.current_word_idx = 0
                st.session_state.learning_complete = False
                st.session_state.word_test_idx = 0
                st.session_state.word_test_score = 0
                st.rerun()

def show_quiz():
    st.title("🎯 퀴즈")

    languages = get_all_languages()
    selected_language = st.selectbox("언어 선택", languages, key="quiz_language")
    num_questions = st.slider("문제 수", 1, 20, 5)

    if st.button("퀴즈 시작", use_container_width=True):
        st.session_state.quiz_active = True
        st.session_state.quiz_language = selected_language
        st.session_state.quiz_questions = num_questions
        st.session_state.quiz_current = 0
        st.session_state.quiz_score = 0
        st.rerun()

    if st.session_state.get('quiz_active', False):
        show_quiz_questions()

def show_quiz_questions():
    language = st.session_state.quiz_language
    vocabularies = get_vocabularies_by_language(language)

    if not vocabularies:
        st.warning("해당 언어의 단어가 없습니다.")
        return

    current_idx = st.session_state.quiz_current
    total = st.session_state.quiz_questions

    if current_idx < total:
        question_word = random.choice(vocabularies)
        all_options = random.sample(vocabularies, min(4, len(vocabularies)))

        if question_word not in all_options:
            all_options[0] = question_word

        random.shuffle(all_options)

        st.progress((current_idx) / total)
        st.markdown(f"### 문제 {current_idx + 1} / {total}")
        st.markdown(f"**'{question_word['word']}'의 뜻은?**")

        cols = st.columns(2)
        for i, option in enumerate(all_options):
            with cols[i % 2]:
                if st.button(f"{option['definition']}", use_container_width=True, key=f"quiz_opt_{i}"):
                    if option['id'] == question_word['id']:
                        st.session_state.quiz_score += 1
                        st.success("정답! ✅")
                    else:
                        st.error(f"틀렸습니다. 정답: {question_word['definition']}")

                    st.session_state.quiz_current += 1
                    st.sleep(1)
                    st.rerun()
    else:
        user_id = st.session_state.user_id
        score = st.session_state.quiz_score
        total = st.session_state.quiz_questions

        save_quiz_result(user_id, language, score, total)

        st.markdown(f"""
        <div class='metric-box' style='text-align: center;'>
            <h2>퀴즈 완료! 🎉</h2>
            <h1 style='color: #667eea;'>{score} / {total}</h1>
            <h3>정답률: {int(score/total*100)}%</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("다시 풀기", use_container_width=True):
            st.session_state.quiz_active = False
            st.rerun()

def show_ranking():
    st.title("🏆 랭킹")

    ranking = get_ranking()
    user_id = st.session_state.user_id

    st.markdown("### 🌍 전체 사용자 랭킹")

    for idx, user in enumerate(ranking, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
        is_current = user['id'] == user_id

        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            st.markdown(f"### {medal}")

        with col2:
            highlight = " **굵게**" if is_current else ""
            st.markdown(f"**{user['username']}{highlight}**")

        with col3:
            st.markdown(f"**📖 {user['learned_count']}**")

def show_profile():
    st.title("👥 프로필")

    user_id = st.session_state.user_id
    username = st.session_state.username

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class='metric-box'>
            <h3>사용자명</h3>
            <h2>{username}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        total_learned = get_user_learned_count(user_id)
        st.markdown(f"""
        <div class='metric-box'>
            <h3>배운 단어 수</h3>
            <h2 style='color: #667eea;'>{total_learned}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📊 언어별 학습 현황")

    languages = get_all_languages()

    for language in languages:
        learned = get_user_learned_by_language(user_id, language)
        total = len(get_vocabularies_by_language(language))
        percentage = int(learned / total * 100) if total > 0 else 0

        col1, col2 = st.columns([2, 1])
        with col1:
            st.progress(percentage / 100)
        with col2:
            st.markdown(f"**{language}: {learned}/{total}**")

def show_add_content():
    st.title("➕ 새 내용 추가")

    tab1, tab2, tab3 = st.tabs(["📚 단어 추가", "📝 문법 추가", "🌍 언어 추가"])

    with tab1:
        st.subheader("단어 추가")
        languages = get_all_languages()
        selected_language = st.selectbox("언어 선택", languages, key="add_vocab_lang")
        word = st.text_input("단어", placeholder="예: Hello")
        definition = st.text_input("뜻", placeholder="예: 인사말")
        example = st.text_area("예문", placeholder="예: Hello, how are you?")

        if st.button("단어 추가", use_container_width=True):
            if word and definition:
                if add_user_vocabulary(st.session_state.user_id, selected_language, word, definition, example):
                    st.success("✅ 단어가 추가되었습니다!")
                else:
                    st.error("❌ 단어 추가에 실패했습니다.")
            else:
                st.error("단어와 뜻을 입력해주세요.")

    with tab2:
        st.subheader("문법 추가")
        selected_language = st.selectbox("언어 선택", languages, key="add_grammar_lang")
        title = st.text_input("문법 제목", placeholder="예: Present Simple")
        question = st.text_input("문제", placeholder="예: He ____ to school.")
        correct_answer = st.text_input("정답", placeholder="예: goes")

        option1 = st.text_input("선택지 1", placeholder="예: go")
        option2 = st.text_input("선택지 2", placeholder="예: goes")
        option3 = st.text_input("선택지 3", placeholder="예: going")
        option4 = st.text_input("선택지 4", placeholder="예: gone")

        explanation = st.text_area("설명", placeholder="왜 이 답이 맞는지 설명해주세요.")

        if st.button("문법 추가", use_container_width=True):
            if title and question and correct_answer:
                options = [option1, option2, option3, option4]
                if add_user_grammar(st.session_state.user_id, selected_language, title, question,
                                   correct_answer, options, explanation):
                    st.success("✅ 문법이 추가되었습니다!")
                else:
                    st.error("❌ 문법 추가에 실패했습니다.")
            else:
                st.error("필수 항목을 모두 입력해주세요.")

    with tab3:
        st.subheader("새로운 언어 추가")
        new_language = st.text_input("언어 이름", placeholder="예: 스페인어, 독일어, 프랑스어")

        if st.button("언어 추가", use_container_width=True):
            if new_language:
                if add_user_vocabulary(st.session_state.user_id, new_language, "start", "새로운 언어 시작", ""):
                    st.success(f"✅ {new_language}이(가) 추가되었습니다!")
                    st.info("이제 '단어 추가'에서 이 언어에 단어를 추가할 수 있습니다.")
                else:
                    st.error("❌ 언어 추가에 실패했습니다.")
            else:
                st.error("언어 이름을 입력해주세요.")

if st.session_state.user_id is None:
    show_login_page()
else:
    show_main_app()
