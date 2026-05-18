import streamlit as st
import sqlite3
import pandas as pd

from datetime import datetime

from streamlit_option_menu import option_menu

# ====================================
# ページ設定
# ====================================

st.set_page_config(
    page_title="重点項目管理",
    layout="centered"
)

# ====================================
# DB接続
# ====================================

conn = sqlite3.connect(
    "care.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ====================================
# users テーブル
# ====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    role TEXT,

    is_active INTEGER DEFAULT 1

)
""")

# ====================================
# entries テーブル
# ====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_name TEXT,

    month TEXT,

    service1 TEXT,
    service2 TEXT,

    income1 TEXT,
    income2 TEXT,

    expense1 TEXT,
    expense2 TEXT,

    time1 TEXT,
    time2 TEXT,

    proposal TEXT,

    created_at TEXT

)
""")

# ====================================
# messages テーブル
# ====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    sender_name TEXT,

    sender_role TEXT,

    target_user TEXT,

    message TEXT,

    is_read INTEGER DEFAULT 0,

    created_at TEXT

)
""")

conn.commit()

# ====================================
# 初期ユーザー
# ====================================

cursor.execute(
    "SELECT COUNT(*) FROM users"
)

count = cursor.fetchone()[0]

if count == 0:

    users = [

        ("奥村", "leader", 1)

    ]

    cursor.executemany(
        """
        INSERT INTO users (

            name,
            role,
            is_active

        )
        VALUES (?, ?, ?)
        """,
        users
    )

    conn.commit()

# ====================================
# session_state
# ====================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "selected_staff" not in st.session_state:
    st.session_state.selected_staff = None

# ====================================
# CSS
# ====================================

st.markdown("""
<style>

/* ====================================
全体
==================================== */

.stApp {

    background-color: #0f172a;

    color: #f8fafc;

}

.main .block-container {

    max-width: 950px;

    padding-top: 2rem;

}

/* ====================================
タイトル
==================================== */

h1,
h2,
h3 {

    color: #f8fafc;

    font-weight: 700;

}

p,
label,
div {

    color: #f8fafc;

}

/* ====================================
メニュー
==================================== */

.nav {

    background-color: #1e1e2f !important;

    border-radius: 14px;

    padding: 8px;

}

.nav-link {

    border-radius: 12px !important;

    color: #f8fafc !important;

    font-weight: 600 !important;

}

.nav-link.active {

    background-color: #ff4b4b !important;

    color: white !important;

}

/* ====================================
ボタン
==================================== */

.stButton > button {

    width: 100%;

    border-radius: 12px;

    border: none;

    background: #22c55e;

    color: white;

    font-weight: 700;

    padding: 12px;

}

.stButton > button:hover {

    background: #16a34a;

    color: white;

}

/* ====================================
入力欄
==================================== */

.stTextArea textarea {

    background-color: #111827;

    color: white;

    border-radius: 12px;

    border: 1px solid #374151;

}

.stSelectbox > div > div {

    background-color: #111827;

    color: white;

    border-radius: 12px;

    border: 1px solid #374151;

}

/* ====================================
チャット
==================================== */

.chat-left {

    background: #1f2937;

    color: white;

    padding: 14px;

    border-radius: 16px;

    margin-right: 25%;

    margin-bottom: 12px;

}

.chat-right {

    background: #22c55e;

    color: white;

    padding: 14px;

    border-radius: 16px;

    margin-left: 25%;

    margin-bottom: 12px;

}

/* ====================================
区切り線
==================================== */

hr {

    border-color: #374151;

}

/* ====================================
スマホ menu 修正版
==================================== */
@media (max-width: 768px) {

    /* menu 全体 */
    div[data-testid="stHorizontalBlock"] ul {

        display: flex !important;

        justify-content: center !important;

        align-items: center !important;

        gap: 6px !important;

        padding: 6px !important;

        overflow-x: auto !important;

    }

    /* 各ボタン */
    div[data-testid="stHorizontalBlock"] ul li {

        flex: 1 !important;

        min-width: 80px !important;

        max-width: 90px !important;

        text-align: center !important;

    }

    /* ボタン本体 */
    div[data-testid="stHorizontalBlock"] ul li a {

        display: flex !important;

        flex-direction: column !important;

        align-items: center !important;

        justify-content: center !important;

        min-height: 58px !important;

        padding: 8px 4px !important;

        white-space: nowrap !important;

        line-height: 1.1 !important;

        font-size: 11px !important;

    }

    /* アイコン */
    div[data-testid="stHorizontalBlock"] ul li a i {

        font-size: 14px !important;

        margin-bottom: 4px !important;

    }

    /* テキスト */
    div[data-testid="stHorizontalBlock"] ul li a span {

        font-size: 11px !important;

        white-space: nowrap !important;

        display: block !important;

    }

}

</style>
""",
unsafe_allow_html=True)

# ====================================
# ログイン画面
# ====================================

if not st.session_state.logged_in:

    st.title("ログイン")

    users_df = pd.read_sql_query(
        """
        SELECT *
        FROM users
        WHERE is_active = 1
        """,
        conn
    )

    user_options = [
        "職員を選択してください"
    ] + list(users_df["name"])

    selected_user = st.selectbox(
        "職員選択",
        user_options
    )

    if st.button("ログイン"):

        if selected_user == "職員を選択してください":

            st.warning(
                "職員を選択してください"
            )

        else:

            selected_df = users_df[
                users_df["name"]
                == selected_user
            ]

            if len(selected_df) > 0:

                user_data = selected_df.iloc[0]

                st.session_state.logged_in = True

                st.session_state.user_name = (
                    user_data["name"]
                )

                st.session_state.role = (
                    user_data["role"]
                )

                st.rerun()

# ====================================
# ログイン後
# ====================================

else:

    st.title("重点項目管理")

    st.write(
        f"ログイン中：{st.session_state.user_name}"
    )

    st.write(
        f"権限：{st.session_state.role}"
    )

    current_month = datetime.now().strftime(
        "%Y-%m"
    )

    # ====================================
    # 未読数
    # ====================================

    if st.session_state.role == "leader":

        unread_df = pd.read_sql_query(
            """
            SELECT *
            FROM messages
            WHERE target_user = 'leader'
            AND is_read = 0
            """,
            conn
        )

    else:

        unread_df = pd.read_sql_query(
            """
            SELECT *
            FROM messages
            WHERE target_user = ?
            AND is_read = 0
            """,
            conn,
            params=(
                st.session_state.user_name,
            )
        )

    unread_count = len(unread_df)

    # ====================================
    # メニュー
    # ====================================

    if st.session_state.role == "leader":

        menu_options = [
            "個人",
            "入力",
            "履歴",
            "確認",
            "管理"
        ]

    else:

        chat_name = "連絡"

        if unread_count > 0:
            chat_name = "連絡 🔴"

        menu_options = [
            "個人",
            "入力",
            chat_name,
            "履歴"
        ]

    selected = option_menu(

        menu_title=None,

        options=menu_options,

        icons=[
            "house-door",
            "clipboard-check",
            "chat-dots",
            "clock-history",
            "people"
        ][:len(menu_options)],

        default_index=0,

        orientation="horizontal"

    )

    # ====================================
    # ホーム
    # ====================================

    if selected == "個人":

        st.subheader("ホーム")

        submitted_df = pd.read_sql_query(
            """
            SELECT *
            FROM entries
            WHERE user_name = ?
            AND month = ?
            """,
            conn,
            params=(
                st.session_state.user_name,
                current_month
            )
        )

        if len(submitted_df) > 0:

            st.success(
                f"{current_month} 提出済"
            )

        else:

            st.warning(
                f"{current_month} 未提出"
            )

        st.divider()

    # ====================================
    # 入力
    # ====================================

    if selected == "入力":

        st.subheader(
            "重点項目入力"
        )

        month = st.selectbox(
            "対象月",
            [
                "2026-05",
                "2026-06",
                "2026-07"
            ]
        )

        service1 = st.text_area(
            "サービス①"
        )

        service2 = st.text_area(
            "サービス②"
        )

        income1 = st.text_area(
            "収入①"
        )

        income2 = st.text_area(
            "収入②"
        )

        expense1 = st.text_area(
            "経費①"
        )

        expense2 = st.text_area(
            "経費②"
        )

        time1 = st.text_area(
            "時間①"
        )

        time2 = st.text_area(
            "時間②"
        )

        proposal = st.text_area(
            "管理者提案"
        )

        if st.button("提出"):

            cursor.execute("""
            INSERT INTO entries (

                user_name,
                month,

                service1,
                service2,

                income1,
                income2,

                expense1,
                expense2,

                time1,
                time2,

                proposal,

                created_at

            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                st.session_state.user_name,
                month,

                service1,
                service2,

                income1,
                income2,

                expense1,
                expense2,

                time1,
                time2,

                proposal,

                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ))

            conn.commit()

            st.success(
                "提出しました"
            )

            st.rerun()

    # ====================================
    # 職員連絡
    # ====================================

    if "連絡" in selected:

        st.subheader(
            "リーダーとの連絡"
        )

        cursor.execute("""
        UPDATE messages
        SET is_read = 1
        WHERE target_user = ?
        """,
        (
            st.session_state.user_name,
        ))

        conn.commit()

        messages_df = pd.read_sql_query(
            """
            SELECT *
            FROM messages

            WHERE

            sender_name = ?

            OR

            target_user = ?
            ORDER BY id ASC
            """,
            conn,
            params=(
                st.session_state.user_name,
                st.session_state.user_name
            )
        )

        for _, row in messages_df.iterrows():

            is_me = (
                row["sender_name"]
                == st.session_state.user_name
            )

            if is_me:

                st.markdown(f"""
                <div class="chat-right">
                {row['message']}
                </div>
                """,
                unsafe_allow_html=True)

            else:

                st.markdown(f"""
                <div class="chat-left">
                {row['message']}
                </div>
                """,
                unsafe_allow_html=True)

        message_input = st.text_area(
            "メッセージ"
        )

        if st.button("送信"):

            if message_input.strip() != "":

                cursor.execute("""
                INSERT INTO messages (

                    sender_name,
                    sender_role,
                    target_user,
                    message,
                    is_read,
                    created_at

                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    st.session_state.user_name,
                    "staff",
                    "leader",
                    message_input,
                    0,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ))

                conn.commit()

                st.success(
                    "送信しました"
                )

                st.rerun()

    # ====================================
    # 履歴
    # ====================================

    if selected == "履歴":

        st.subheader("履歴")

        history_df = pd.read_sql_query(
            """
            SELECT *
            FROM entries
            WHERE user_name = ?
            ORDER BY month DESC
            """,
            conn,
            params=(
                st.session_state.user_name,
            )
        )

        for _, row in history_df.iterrows():

            st.markdown(f"""
            <div class="chat-left">

            <h4>{row['month']}</h4>

            <b>サービス</b><br>
            ① {row['service1']}<br>
            ② {row['service2']}<br><br>

            <b>収入</b><br>
            ① {row['income1']}<br>
            ② {row['income2']}<br><br>

            <b>経費</b><br>
            ① {row['expense1']}<br>
            ② {row['expense2']}<br><br>

            <b>時間</b><br>
            ① {row['time1']}<br>
            ② {row['time2']}<br><br>

            <b>管理者提案</b><br>
            {row['proposal']}

            </div>
            """,
            unsafe_allow_html=True)

            st.divider()

    # ====================================
    # 重点項目確認
    # ====================================

    if (
    selected == "確認"
    and
    st.session_state.role == "leader"
    and
    not st.session_state.selected_staff
):

        st.subheader(
            "重点項目確認"
        )

        users_df = pd.read_sql_query(
            """
            SELECT *
            FROM users
            WHERE role = 'staff'
            AND is_active = 1
            """,
            conn
        )

        for _, row in users_df.iterrows():

            staff_name = row["name"]

            st.markdown(
                f"### {staff_name}"
            )

            if st.button(
                f"{staff_name}を開く",
                key=f"open_{staff_name}"
            ):

                st.session_state.selected_staff = (
                    staff_name
                )

                st.rerun()

    # ====================================
    # 個別画面
    # ====================================

    if st.session_state.selected_staff:

        selected_staff = (
            st.session_state.selected_staff
        )

        st.title(
            f"{selected_staff}"
        )

        if st.button("← 戻る"):

            st.session_state.selected_staff = None

            st.rerun()

        st.divider()

        # ====================================
        # 最新重点項目
        # ====================================

        entry_df = pd.read_sql_query(
            """
            SELECT *
            FROM entries
            WHERE user_name = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            conn,
            params=(selected_staff,)
        )

        if len(entry_df) > 0:

            latest = entry_df.iloc[0]

            st.subheader("サービス")

            st.info(
                f"① {latest['service1']}"
            )

            st.info(
                f"② {latest['service2']}"
            )

            st.subheader("収入")

            st.info(
                f"① {latest['income1']}"
            )

            st.info(
                f"② {latest['income2']}"
            )

            st.subheader("経費")

            st.info(
                f"① {latest['expense1']}"
            )

            st.info(
                f"② {latest['expense2']}"
            )

            st.subheader("時間")

            st.info(
                f"① {latest['time1']}"
            )

            st.info(
                f"② {latest['time2']}"
            )

        else:

            st.warning(
                "まだ提出されていません"
            )

        st.divider()

        # ====================================
        # チャット
        # ====================================

        st.subheader("チャット")

        messages_df = pd.read_sql_query(
            """
            SELECT *
            FROM messages
            WHERE
            sender_name = ?
            OR
            target_user = ?
            ORDER BY id ASC
            """,
            conn,
            params=(
                selected_staff,
                selected_staff
            )
        )

        for _, row in messages_df.iterrows():

            is_leader = (
                row["sender_role"]
                == "leader"
            )

            if is_leader:

                st.markdown(f"""
                <div class="chat-right">
                {row['message']}
                </div>
                """,
                unsafe_allow_html=True)

            else:

                st.markdown(f"""
                <div class="chat-left">
                {row['message']}
                </div>
                """,
                unsafe_allow_html=True)

        reply_input = st.text_area(
            "メッセージ"
        )

        if st.button("送信"):

            if reply_input.strip() != "":

                cursor.execute("""
                INSERT INTO messages (

                    sender_name,
                    sender_role,
                    target_user,
                    message,
                    is_read,
                    created_at

                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    st.session_state.user_name,
                    "leader",
                    selected_staff,
                    reply_input,
                    0,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ))

                conn.commit()

                st.success(
                    "送信しました"
                )

                st.rerun()

    # ====================================
    # 職員管理
    # ====================================

    if (
        selected == "管理"
        and
        st.session_state.role == "leader"
    ):

        st.subheader("職員管理")

        st.divider()

        st.markdown("### 職員追加")

        new_name = st.text_input(
            "名前"
        )

        new_role = st.selectbox(
            "権限",
            [
                "staff",
                "leader"
            ]
        )

        if st.button("追加"):

            if new_name.strip() != "":

                cursor.execute("""
                INSERT INTO users (

                    name,
                    role,
                    is_active

                )
                VALUES (?, ?, ?)
                """,
                (
                    new_name,
                    new_role,
                    1
                ))

                conn.commit()

                st.success(
                    "追加しました"
                )

                st.rerun()

        st.divider()

        users_df = pd.read_sql_query(
            """
            SELECT *
            FROM users
            ORDER BY role DESC
            """,
            conn
        )

        st.markdown("### 職員一覧")

        for _, row in users_df.iterrows():

            user_id = row["id"]

            name = row["name"]

            role = row["role"]

            is_active = row["is_active"]

            if is_active == 1:

                status = "在職"

            else:

                status = "停止"

            col1, col2, col3 = st.columns(
                [3,2,1]
            )

            with col1:

                st.write(name)

            with col2:

                st.write(
                    f"{role} / {status}"
                )

            with col3:

                if is_active == 1:

                    if st.button(
                        "停止",
                        key=f"stop_{user_id}"
                    ):

                        cursor.execute("""
                        UPDATE users
                        SET is_active = 0
                        WHERE id = ?
                        """,
                        (user_id,)
                        )

                        conn.commit()

                        st.rerun()

                else:

                    if st.button(
                        "復帰",
                        key=f"back_{user_id}"
                    ):

                        cursor.execute("""
                        UPDATE users
                        SET is_active = 1
                        WHERE id = ?
                        """,
                        (user_id,)
                        )

                        conn.commit()

                        st.rerun()

            st.divider()

    # ====================================
    # ログアウト
    # ====================================

    st.divider()

    if st.button("ログアウト"):

        st.session_state.logged_in = False

        st.session_state.user_name = ""

        st.session_state.role = ""

        st.session_state.selected_staff = None

        st.rerun()
