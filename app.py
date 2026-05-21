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
# drafts テーブル
# ====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS drafts (

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

    updated_at TEXT

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

    month TEXT,

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

if "edit_entry_id" not in st.session_state:
    st.session_state.edit_entry_id = None

if "edit_draft_id" not in st.session_state:
    st.session_state.edit_draft_id = None

if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "個人"

# ====================================
# CSS
# ====================================

st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
    color: #f8fafc;
}

.main .block-container {
    max-width: 950px;
    padding-top: 2rem;
}

h1,h2,h3,p,label,div {
    color: #f8fafc;
}

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

.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: none;
    background: #22c55e;
    color: white;
    font-weight: 700;
    padding: 12px;
}

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

            st.warning("職員を選択してください")

        else:

            selected_df = users_df[
                users_df["name"]
                == selected_user
            ]

            if len(selected_df) > 0:

                user_data = selected_df.iloc[0]

                st.session_state.logged_in = True

                st.session_state.user_name = user_data["name"]

                st.session_state.role = user_data["role"]

                st.rerun()

            st.divider()

            st.markdown("""
            <div style="
            background-color:#1e293b;
            padding:20px;
            border-radius:18px;
            margin-top:10px;
            border:1px solid #334155;
            ">

            <h3 style="color:#f8fafc;">
            📢 アップデート情報
            </h3>

            <div style="
            color:#cbd5e1;
            line-height:1.8;
            font-size:15px;
            ">

            🆕 下書き編集機能を追加しました<br>

            🆕 リーダーチャット機能改善<br>

            🆕 提出状況確認機能追加<br>

            🆕 スマホUI改善<br>

            🛠 不具合修正・安定化対応

            </div>

            </div>
            """,
            unsafe_allow_html=True)

            st.caption("Version 1.3.0")

# ====================================
# ログイン後
# ====================================

else:

    st.title("重点項目管理")

    st.write(
        f"ログイン中：{st.session_state.user_name}"
    )

    current_month = datetime.now().strftime(
        "%Y-%m"
    )

    # ====================================
    # 未読数
    # ====================================

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
            "集計",
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
            "bar-chart",
            "people"
        ][:len(menu_options)],
        default_index=menu_options.index(
            st.session_state.selected_menu
        ),

        orientation="horizontal"
    )

    st.session_state.selected_menu = selected

    # ====================================
    # ホーム
    # ====================================

    if selected == "個人":

        st.subheader("ホーム")

        st.markdown("""
        <style>

        .manual-card {

            background-color: #1e293b;

            padding: 20px;

            border-radius: 18px;

            margin-bottom: 18px;

            border: 1px solid #334155;

            box-shadow: 0 4px 12px rgba(0,0,0,0.25);

        }

        .manual-title {

            font-size: 22px;

            font-weight: bold;

            margin-bottom: 12px;

            color: #f8fafc;

        }

        .manual-text {

            font-size: 15px;

            line-height: 1.8;

            color: #cbd5e1;

        }

        </style>
        """,
        unsafe_allow_html=True)

        with st.expander("📖 使い方マニュアル"):

            st.markdown("## 🏠 ホーム")
            st.info("""
        ・今月の提出状況を確認できます
        ・未提出 / 提出済 が表示されます
        """)

            st.markdown("## ✍ 入力")
            st.success("""
        ・重点項目を入力します
        ・下書き保存可能
        ・提出後は履歴へ保存されます
        ・提出後も編集可能
        """)

            st.markdown("## 🕘 履歴")
            st.warning("""
        ・過去提出内容を確認できます
        ・編集、削除可能
        ・下書きも表示されます
        """)

            st.markdown("## 💬 連絡")
            st.info("""
        ・リーダーへチャット送信できます
        ・既読/未読確認できます
        """)

            if st.session_state.role == "leader":

                st.markdown("## 👀 確認")
                st.error("""
        ・職員の提出状況確認
        ・重点項目確認
        ・個別チャット
        """)

                st.markdown("## 👥 管理")
                st.success("""
        ・職員追加
        ・停止 / 復帰
        ・権限管理
        """)

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

    # ====================================
    # 入力
    # ====================================

    if selected == "入力":

        edit_data = None

        draft_data = None

        if st.session_state.edit_draft_id:

            draft_edit_df = pd.read_sql_query(
                """
                SELECT *
                FROM drafts
                WHERE id = ?
                """,
                conn,
                params=(
                    st.session_state.edit_draft_id,
                )
            )

            if len(draft_edit_df) > 0:

                draft_data = (
                    draft_edit_df.iloc[0]
                )

        if st.session_state.edit_entry_id:

            edit_df = pd.read_sql_query(
                """
                SELECT *
                FROM entries
                WHERE id = ?
                """,
                conn,
                params=(
                    st.session_state.edit_entry_id,
                )
            )

            if len(edit_df) > 0:

                edit_data = edit_df.iloc[0]

        st.subheader("重点項目入力")

        month_list = [
            "2026-04",
            "2026-05",
            "2026-06"
        ]

        default_month = current_month

        if "draft_month" in st.session_state:

            default_month = (
                st.session_state.draft_month
            )

        if edit_data is not None:

            default_month = (
                edit_data["month"]
            )

        month = st.selectbox(
            "月",
            month_list,
            index=month_list.index(
                default_month
            )
        )

        service1 = st.text_area(
            "サービス①",
            value=(
                edit_data["service1"]
                if edit_data is not None
                else (
                    draft_data["service1"]
                    if draft_data is not None
                    else ""
                )
            )
        )
        
        service2 = st.text_area(
            "サービス②",
            value=(
                edit_data["service2"]
                if edit_data is not None
                else (
                    draft_data["service2"]
                    if draft_data is not None
                    else ""
                )
            )
        )

        income1 = st.text_area(
            "収入①",
            value=(
                edit_data["income1"]
                if edit_data is not None
                else (
                    draft_data["income1"]
                    if draft_data is not None
                    else ""
                )
            )
        )
        income2 = st.text_area(
            "収入②",
            value=(
                edit_data["income2"]
                if edit_data is not None
                else (
                    draft_data["income2"]
                    if draft_data is not None
                    else ""
                )
            )
        )

        expense1 = st.text_area(
            "経費①",
            value=(
                edit_data["expense1"]
                if edit_data is not None
                else (
                    draft_data["expense1"]
                    if draft_data is not None
                    else ""
                )
            )
        )
        expense2 = st.text_area(
            "経費②",
            value=(
                edit_data["expense2"]
                if edit_data is not None
                else (
                    draft_data["expense2"]
                    if draft_data is not None
                    else ""
                )
            )
        )

        time1 = st.text_area(
            "時間①",
            value=(
                edit_data["time1"]
                if edit_data is not None
                else (
                    draft_data["time1"]
                    if draft_data is not None
                    else ""
                )
            )
        )
        time2 = st.text_area(
            "時間②",
            value=(
                edit_data["time2"]
                if edit_data is not None
                else (
                    draft_data["time2"]
                    if draft_data is not None
                    else ""
                )
            )
        )

        proposal = st.text_area(
            "管理者提案",
            value=(
                edit_data["proposal"]
                if edit_data is not None
                else (
                    draft_data["proposal"]
                    if draft_data is not None
                    else ""
                )
            )
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button("下書き保存"):

                cursor.execute("""
                DELETE FROM drafts
                WHERE user_name = ?
                AND month = ?
                """,
                (
                    st.session_state.user_name,
                    month
                ))

                cursor.execute("""
                INSERT INTO drafts (

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

                    updated_at

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

                st.success("下書き保存しました")

        with col2:

            if st.button(
                "提出",
                key="submit_entry"
            ):

                try:

                    if st.session_state.edit_entry_id:

                        cursor.execute("""
                        UPDATE entries
                        SET

                            service1 = ?,
                            service2 = ?,

                            income1 = ?,
                            income2 = ?,

                            expense1 = ?,
                            expense2 = ?,

                            time1 = ?,
                            time2 = ?,

                            proposal = ?

                        WHERE id = ?
                        """,
                        (
                            service1,
                            service2,

                            income1,
                            income2,

                            expense1,
                            expense2,

                            time1,
                            time2,

                            proposal,

                            st.session_state.edit_entry_id
                        ))

                        conn.commit()

                        st.session_state.edit_entry_id = None

                        st.success("更新しました")

                        st.rerun()

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

                    st.success("提出しました")

                    st.write("保存成功")

                except Exception as e:

                    st.error(e)

    # ====================================
    # 職員連絡
    # ====================================

    if "連絡" in selected:

        st.subheader("リーダーとの連絡")

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

            cursor.execute("""
            INSERT INTO messages (

                sender_name,
                sender_role,
                target_user,
                month,
                message,
                is_read,
                created_at

            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                st.session_state.user_name,
                "staff",
                "leader",
                current_month,
                message_input,
                0,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ))

            conn.commit()

            st.rerun()

    # ====================================
    # 履歴
    # ====================================

    if selected == "履歴":

        st.subheader("履歴")

        draft_df = pd.read_sql_query(
            """
            SELECT *
            FROM drafts
            WHERE user_name = ?
            ORDER BY updated_at DESC
            """,
            conn,
            params=(
                st.session_state.user_name,
            )
        )

        if len(draft_df) > 0:

            st.subheader("下書き")

            for _, row in draft_df.iterrows():

                st.warning(f"""
        【下書き】
        {row['month']}

        【サービス】
        ① {row['service1']}
        ② {row['service2']}
        """)

                if st.button(
                    "下書きを編集",
                    key=f"draft_{row['id']}"
                ):

                    st.session_state.edit_entry_id = None

                    st.session_state.edit_draft_id = (
                        row["id"]
                    )

                    st.session_state.selected_menu = "入力"

                    st.rerun()

                    if st.button(
                        "下書きを削除",
                        key=f"delete_draft_{row['id']}"
                    ):

                        cursor.execute("""
                        DELETE FROM drafts
                        WHERE id = ?
                        """,
                        (
                            row["id"],
                        ))

                        conn.commit()

                        st.success("削除しました")

                        st.rerun()

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

        st.write(history_df)

        for _, row in history_df.iterrows():

            st.info(f"""
            【対象月】
            {row['month']}

            【サービス】
            ① {row['service1']}
            ② {row['service2']}

            【収入】
            ① {row['income1']}
            ② {row['income2']}

            【経費】
            ① {row['expense1']}
            ② {row['expense2']}

            【時間】
            ① {row['time1']}
            ② {row['time2']}

            【管理者提案】
            {row['proposal']}
            """)

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "編集",
                    key=f"edit_{row['id']}"
                ):

                    st.session_state.edit_entry_id = (
                        row["id"]
                    )

                    st.session_state.selected_menu = (
                        "入力"
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "削除",
                    key=f"delete_{row['id']}"
                ):

                    cursor.execute("""
                    DELETE FROM entries
                    WHERE id = ?
                    """,
                    (
                        row["id"],
                    ))

                    conn.commit()

                    st.success(
                        "削除しました"
                    )

                    st.rerun()

            st.divider()

    # ====================================
    # 確認
    # ====================================

    if (
        selected == "確認"
        and
        st.session_state.role == "leader"
        and
        not st.session_state.selected_staff
    ):

        st.subheader("重点項目確認")

        users_df = pd.read_sql_query(
            """
            SELECT *
            FROM users
            WHERE role = 'staff'
            """,
            conn
        )

        for _, row in users_df.iterrows():

            staff_name = row["name"]

            submit_check = pd.read_sql_query(
                """
                SELECT *
                FROM entries
                WHERE user_name = ?
                AND month = ?
                """,
                conn,
                params=(
                    staff_name,
                    current_month
                )
            )

            submitted = len(submit_check) > 0

            if submitted:

                st.success(
                    f"{staff_name} ｜ {current_month} 提出済"
                )

            else:

                st.warning(
                    f"{staff_name} ｜ {current_month} 未提出"
                )

            if st.button(

                f"{staff_name}を開く",
                key=f"open_{staff_name}_{row['id']}"
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

        st.title(selected_staff)

        if st.button("← 戻る"):

            st.session_state.selected_staff = None

            st.rerun()

        entry_df = pd.read_sql_query(
            """
            SELECT *
            FROM entries
            WHERE user_name = ?
            ORDER BY month DESC
            """,
            conn,
            params=(selected_staff,)
        )
           
        st.subheader("提出内容")

        latest_entry_df = pd.read_sql_query(
            """
            SELECT *
            FROM entries
            WHERE user_name = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            conn,
            params=(
                selected_staff,
            )
        )

        if len(latest_entry_df) > 0:

            latest = latest_entry_df.iloc[0]

            st.markdown(f"""
            ### 【対象月】
            {latest['month']}
            """)

            st.success(f"""
            【サービス】
            ① {latest['service1']}

            ② {latest['service2']}
            """)

            st.info(f"""
            【収入】
            ① {latest['income1']}

            ② {latest['income2']}
            """)

            st.warning(f"""
            【経費】
            ① {latest['expense1']}

            ② {latest['expense2']}
            """)

            st.error(f"""
            【時間】
            ① {latest['time1']}

            ② {latest['time2']}
            """)

            st.success(f"""
            【管理者提案】

            {latest['proposal']}
            """)

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

            cursor.execute("""
            INSERT INTO messages (

                sender_name,
                sender_role,
                target_user,
                month,
                message,
                is_read,
                created_at

            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                st.session_state.user_name,
                "leader",
                selected_staff,
                current_month,
                reply_input,
                0,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ))

            conn.commit()

            st.rerun()

    # ====================================
    # 集計
    # ====================================

    if (
        selected == "集計"
        and
        st.session_state.role == "leader"
    ):

        st.subheader("重点項目集計")

        summary_df = pd.read_sql_query(
            """
            SELECT *
            FROM entries
            WHERE month = ?
            ORDER BY user_name
            """,
            conn,
            params=(current_month,)
        )

        if len(summary_df) == 0:

            st.warning("提出データがありません")

        else:

            st.markdown("## サービスの質")

            for _, row in summary_df.iterrows():

                st.success(f"""
    【{row['user_name']}】

    ① {row['service1']}

    ② {row['service2']}
    """)

            st.markdown("## 収入")

            for _, row in summary_df.iterrows():

                st.info(f"""
    【{row['user_name']}】

    ① {row['income1']}

    ② {row['income2']}
    """)

            st.markdown("## 経費")

            for _, row in summary_df.iterrows():

                st.warning(f"""
    【{row['user_name']}】

    ① {row['expense1']}

    ② {row['expense2']}
    """)

            st.markdown("## 時間")

            for _, row in summary_df.iterrows():

                st.error(f"""
    【{row['user_name']}】

    ① {row['time1']}

    ② {row['time2']}
    """)

    # ====================================
    # 職員管理
    # ====================================

    if (
        selected == "管理"
        and
        st.session_state.role == "leader"
    ):

        st.subheader("職員管理")

        new_name = st.text_input("名前")

        new_role = st.selectbox(
            "権限",
            [
                "staff",
                "leader"
            ]
        )

        if st.button("追加"):

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

            st.subheader("職員一覧")

            for _, row in users_df.iterrows():

                col1, col2, col3 = st.columns([3,2,1])

                with col1:
                    st.write(row["name"])

                with col2:

                    status = "在職"

                    if row["is_active"] == 0:
                        status = "停止"

                    st.write(
                        f"{row['role']} / {status}"
                    )

                with col3:

                    if row["is_active"] == 1:

                        if st.button(
                            "停止",
                            key=f"stop_{row['id']}"
                        ):

                            cursor.execute("""
                            UPDATE users
                            SET is_active = 0
                            WHERE id = ?
                            """,
                            (
                                row["id"],
                            ))

                            conn.commit()

                            st.rerun()

                    else:

                        if st.button(
                            "復帰",
                            key=f"back_{row['id']}"
                        ):

                            cursor.execute("""
                            UPDATE users
                            SET is_active = 1
                            WHERE id = ?
                            """,
                            (
                                row["id"],
                            ))

                            conn.commit()

                            st.rerun()

            st.divider()

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

            st.rerun()

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
