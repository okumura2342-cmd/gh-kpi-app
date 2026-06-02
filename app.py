import streamlit as st
import pandas as pd
import gspread

from oauth2client.service_account import (
    ServiceAccountCredentials
)

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
# Google Sheets接続
# ====================================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets,
    scope
)

client = gspread.authorize(creds)

spreadsheet = client.open(
    "GH重点項目管理DB"
)

users_sheet = spreadsheet.worksheet("users")
entries_sheet = spreadsheet.worksheet("entries")
drafts_sheet = spreadsheet.worksheet("drafts")
messages_sheet = spreadsheet.worksheet("messages")

# ====================================
# DataFrame取得関数
# ====================================

def get_users_df():

    data = users_sheet.get_all_records()

    if len(data) == 0:
        return pd.DataFrame(
            columns=[
                "id",
                "name",
                "role",
                "is_active"
            ]
        )

    return pd.DataFrame(data)


def get_entries_df():

    data = entries_sheet.get_all_records()

    if len(data) == 0:
        return pd.DataFrame(
            columns=[
                "id",
                "user_name",
                "month",
                "service1",
                "service2",
                "income1",
                "income2",
                "expense1",
                "expense2",
                "time1",
                "time2",
                "proposal",
                "created_at"
            ]
        )

    return pd.DataFrame(data)


def get_drafts_df():

    data = drafts_sheet.get_all_records()

    if len(data) == 0:
        return pd.DataFrame(
            columns=[
                "id",
                "user_name",
                "month",
                "service1",
                "service2",
                "income1",
                "income2",
                "expense1",
                "expense2",
                "time1",
                "time2",
                "proposal",
                "updated_at"
            ]
        )

    return pd.DataFrame(data)


def get_messages_df():

    data = messages_sheet.get_all_records()

    if len(data) == 0:
        return pd.DataFrame(
            columns=[
                "id",
                "sender_name",
                "sender_role",
                "target_user",
                "month",
                "message",
                "is_read",
                "created_at"
            ]
        )

    return pd.DataFrame(data)

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

if "force_input" not in st.session_state:
    st.session_state.force_input = False

# ====================================
# CSS
# ====================================

st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
    color: #f8fafc;
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
""", unsafe_allow_html=True)

# ====================================
# ログイン
# ====================================

if not st.session_state.logged_in:

    st.title("ログイン")

    users_df = get_users_df()

    if len(users_df) > 0:

        users_df = users_df[
            users_df["is_active"] == 1
        ]

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
                users_df["name"] == selected_user
            ]

            if len(selected_df) > 0:

                user_data = selected_df.iloc[0]

                st.session_state.logged_in = True
                st.session_state.user_name = user_data["name"]
                st.session_state.role = user_data["role"]

                st.rerun()

# ====================================
# ログイン後
# ====================================

else:

    current_month = datetime.now().strftime(
        "%Y-%m"
    )

    st.title("重点項目管理")

    messages_df = get_messages_df()

    unread_df = messages_df[
        (messages_df["target_user"] == st.session_state.user_name)
        &
        (messages_df["is_read"] == 0)
    ]

    unread_count = len(unread_df)

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

    default_menu = st.session_state.get(
        "selected_menu",
        "個人"
    )

    if st.session_state.force_input:

        default_menu = "入力"

        st.session_state.force_input = False

    selected = option_menu(
        menu_title=None,
        options=menu_options,
        orientation="horizontal",
        default_index=menu_options.index(default_menu)
    )

    st.session_state.selected_menu = selected

    # ====================================
    # ホーム
    # ====================================

    if selected == "個人":

        st.subheader("ホーム")

        entries_df = get_entries_df()

        submitted_df = entries_df[
            (entries_df["user_name"] == st.session_state.user_name)
            &
            (entries_df["month"] == current_month)
        ]

        if len(submitted_df) > 0:
            st.success(f"{current_month} 提出済")
        else:
            st.warning(f"{current_month} 未提出")

    # ====================================
    # 入力
    # ====================================

    if selected == "入力":

        edit_data = None

        if st.session_state.edit_entry_id:

            entries_df = get_entries_df()

            edit_df = entries_df[
                entries_df["id"].astype(str)
                ==
                str(
                    st.session_state.edit_entry_id
                )
            ]

            if len(edit_df) > 0:

                edit_data = edit_df.iloc[0]

        st.subheader("重点項目入力")

        month = st.selectbox(
            "月",
            [current_month]
        )

        service1 = st.text_area(
            "サービス①",
            value=(
                edit_data["service1"]
                if edit_data is not None
                else ""
            )
        )
        service2 = st.text_area(
            "サービス②",
            value=(
                edit_data["service2"]
                if edit_data is not None
                else ""
            )
        )

        income1 = st.text_area(
            "収入①",
            value=(
                edit_data["income1"]
                if edit_data is not None
                else ""
            )
        )
        income2 = st.text_area(
            "収入②",
            value=(
                edit_data["income2"]
                if edit_data is not None
                else ""
            )
        )

        expense1 = st.text_area(
            "経費①",
            value=(
                edit_data["expense1"]
                if edit_data is not None
                else ""
            )
        )
        expense2 = st.text_area(
            "経費②",
            value=(
                edit_data["expense2"]
                if edit_data is not None
                else ""
            )
        )

        time1 = st.text_area(
            "時間①",
            value=(
                edit_data["time1"]
                if edit_data is not None
                else ""
            )
        )
        time2 = st.text_area(
            "時間②",
            value=(
                edit_data["time2"]
                if edit_data is not None
                else ""
            )
        )

        proposal = st.text_area(
            "管理者提案",
            value=(
                edit_data["proposal"]
                if edit_data is not None
                else ""
            )
        )

        col1, col2 = st.columns(2)

        # 下書き
        with col1:

            if st.button("下書き保存"):

                draft_id = str(datetime.now().timestamp())

                drafts_sheet.append_row([
                    draft_id,
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
                ])

                st.success("下書き保存しました")

        # 提出
        with col2:

            if st.button("提出"):

                if st.session_state.edit_entry_id:

                    cell = entries_sheet.find(
                        str(
                            st.session_state.edit_entry_id
                        )
                    )

                    row_num = cell.row

                    entries_sheet.update(
                        f"D{row_num}:L{row_num}",
                        [[
                            service1,
                            service2,

                            income1,
                            income2,

                            expense1,
                            expense2,

                            time1,
                            time2,

                            proposal
                        ]]
                    )

                    st.success("更新しました")

                    st.session_state.edit_entry_id = None

                    st.rerun()

                else:

                    entry_id = str(datetime.now().timestamp())

                    entries_sheet.append_row([
                        entry_id,
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
                    ])

                    st.success("提出しました")

                    st.rerun()

    # ====================================
    # 連絡
    # ====================================

    if "連絡" in selected:

        st.subheader("リーダーとの連絡")

        messages_df = get_messages_df()

        chat_df = messages_df[
            (messages_df["sender_name"] == st.session_state.user_name)
            |
            (messages_df["target_user"] == st.session_state.user_name)
        ]

        for _, row in chat_df.iterrows():

            is_me = (
                row["sender_name"]
                == st.session_state.user_name
            )

            if is_me:

                st.markdown(f"""
                <div class="chat-right">
                {row['message']}
                </div>
                """, unsafe_allow_html=True)

            else:

                st.markdown(f"""
                <div class="chat-left">
                {row['message']}
                </div>
                """, unsafe_allow_html=True)

        message_input = st.text_area("メッセージ")

        if st.button("送信"):

            message_id = str(datetime.now().timestamp())

            messages_sheet.append_row([
                message_id,
                st.session_state.user_name,
                "staff",
                "leader",
                current_month,
                message_input,
                0,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ])

            st.rerun()

    # ====================================
    # 履歴
    # ====================================

    if selected == "履歴":

        st.subheader("履歴")

        entries_df = get_entries_df()

        history_df = entries_df[
            entries_df["user_name"]
            == st.session_state.user_name
        ]

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

            if st.button(
                "編集",
                key=f"edit_{row['id']}"
            ):

                st.session_state.edit_entry_id = row["id"]

                st.session_state.force_input = True

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

        entries_df = get_entries_df()

        summary_df = entries_df[
            entries_df["month"] == current_month
        ]

        st.markdown("## サービスの質")

        for _, row in summary_df.iterrows():

            st.success(f"""
【{row['user_name']}】

① {row['service1']}
② {row['service2']}
""")

    # ====================================
    # 管理
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
            ["staff", "leader"]
        )

        if st.button("追加"):

            user_id = str(datetime.now().timestamp())

            users_sheet.append_row([
                user_id,
                new_name,
                new_role,
                1
            ])

            st.success("追加しました")

            st.rerun()

        users_df = get_users_df()

        for _, row in users_df.iterrows():

            st.write(
                f"{row['name']} / {row['role']}"
            )

    # ====================================
    # ログアウト
    # ====================================

    st.divider()

    if st.button("ログアウト"):

        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.role = ""

        st.rerun()