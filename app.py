import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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
try:
    spreadsheet = client.open("GH重点項目管理DB")
except Exception as e:
    st.error(str(e))
    st.stop()

# ====================================
# シート取得 / なければ作成
# ====================================

def get_or_create_worksheet(sheet_name, headers):
    try:
        ws = spreadsheet.worksheet(sheet_name)
    except:
        ws = spreadsheet.add_worksheet(
            title=sheet_name,
            rows=2000,
            cols=max(len(headers), 10)
        )
        ws.append_row(headers)

    values = ws.get_all_values()

    if len(values) == 0:
        ws.append_row(headers)
    else:
        first_row = values[0]
        if len(first_row) == 0 or all(str(x).strip() == "" for x in first_row):
            ws.update("A1", [headers])
        else:
            # 足りない列があればヘッダを補完
            if len(first_row) < len(headers):
                new_header = first_row + headers[len(first_row):]
                ws.update("A1", [new_header])
            else:
                # 空ヘッダだけ補完
                fixed = first_row[:]
                changed = False
                for i, h in enumerate(headers):
                    if i >= len(fixed):
                        fixed.append(h)
                        changed = True
                    elif str(fixed[i]).strip() == "":
                        fixed[i] = h
                        changed = True
                if changed:
                    ws.update("A1", [fixed])

    return ws


USERS_HEADERS = [
    "id",
    "name",
    "role",
    "is_active",
    "icon_url",
    "use_default_icon",
    "created_at"
]

ENTRIES_HEADERS = [
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
    "created_at",
    "status"
]

DRAFTS_HEADERS = [
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

MESSAGES_HEADERS = [
    "id",
    "room_user",
    "sender_name",
    "sender_role",
    "message",
    "month",
    "is_read",
    "created_at",
    "read_at",
    "icon_url"
]

SETTINGS_HEADERS = [
    "user_name",
    "icon_url",
    "use_default_icon",
    "theme",
    "updated_at"
]

users_sheet = get_or_create_worksheet("users", USERS_HEADERS)
entries_sheet = get_or_create_worksheet("entries", ENTRIES_HEADERS)
drafts_sheet = get_or_create_worksheet("drafts", DRAFTS_HEADERS)
messages_sheet = get_or_create_worksheet("messages", MESSAGES_HEADERS)
settings_sheet = get_or_create_worksheet("settings", SETTINGS_HEADERS)

# ====================================
# 初期データ投入（users が空なら）
# ====================================

def seed_users_if_empty():
    values = users_sheet.get_all_records()
    if len(values) > 0:
        return

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = [
        ["1", "奥村", "leader", 1, "", 1, now_str],
        ["2", "和田", "staff", 1, "", 1, now_str],
        ["3", "福山", "staff", 1, "", 1, now_str],
        ["4", "神谷", "staff", 1, "", 1, now_str],
        ["5", "松永", "staff", 1, "", 1, now_str],
    ]

    for row in rows:
        users_sheet.append_row(row)

seed_users_if_empty()

# ====================================
# DataFrame取得関数
# ====================================

def safe_df(records, columns):
    if len(records) == 0:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(records)
    for c in columns:
        if c not in df.columns:
            df[c] = ""
    return df[columns]


@st.cache_data(ttl=30)
def get_users_df():
    data = users_sheet.get_all_records()
    df = safe_df(data, USERS_HEADERS)

    if len(df) > 0:
        df["id"] = df["id"].astype(str)
        df["name"] = df["name"].astype(str)
        df["role"] = df["role"].astype(str)
        df["is_active"] = pd.to_numeric(df["is_active"], errors="coerce").fillna(1).astype(int)
        df["use_default_icon"] = pd.to_numeric(df["use_default_icon"], errors="coerce").fillna(1).astype(int)
    return df


@st.cache_data(ttl=30)
def get_entries_df():

    st.write("entries 読み込み")
    data = entries_sheet.get_all_records()
    return safe_df(data, ENTRIES_HEADERS)


@st.cache_data(ttl=30)
def get_drafts_df():
    data = drafts_sheet.get_all_records()
    return safe_df(data, DRAFTS_HEADERS)


@st.cache_data(ttl=30)
def get_messages_df():

    st.write("messages 読み込み")

    data = messages_sheet.get_all_records()

    return safe_df(data, MESSAGES_HEADERS)

@st.cache_data(ttl=30)
def get_users_df():

    st.write("users 読み込み")
    data = settings_sheet.get_all_records()
    df = safe_df(data, SETTINGS_HEADERS)
    if len(df) > 0:
        df["use_default_icon"] = pd.to_numeric(df["use_default_icon"], errors="coerce").fillna(1).astype(int)
    return df

# ====================================
# 共通関数
# ====================================

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def role_label(role):
    return "リーダー" if role == "leader" else "職員"


def default_icon_url():
    return "https://cdn-icons-png.flaticon.com/512/847/847969.png"


def get_user_icon(user_name):
    users_df = get_users_df()
    settings_df = get_settings_df()

    setting_row = settings_df[settings_df["user_name"] == user_name]
    if len(setting_row) > 0:
        row = setting_row.iloc[0]
        if int(row.get("use_default_icon", 1)) == 0 and str(row.get("icon_url", "")).strip() != "":
            return str(row["icon_url"])

    user_row = users_df[users_df["name"] == user_name]
    if len(user_row) > 0:
        row = user_row.iloc[0]
        if int(row.get("use_default_icon", 1)) == 0 and str(row.get("icon_url", "")).strip() != "":
            return str(row["icon_url"])

    return default_icon_url()


def get_unread_count_for_user(user_name):
    messages_df = get_messages_df()
    if len(messages_df) == 0:
        return 0

    unread_df = messages_df[
        (messages_df["room_user"] == user_name)
        &
        (messages_df["sender_name"] != user_name)
        &
        (messages_df["is_read"] == 0)
    ]
    return len(unread_df)

# ====================================
# session_state
# ====================================

DEFAULT_SESSION_VALUES = {
    "logged_in": False,
    "user_name": "",
    "role": "",
    "selected_staff": None,
    "selected_room_user": None,
    "edit_entry_id": None,
    "edit_draft_id": None,
    "selected_menu": "ホーム",
    "force_input": False,
    "chat_compact_mode": False,
}

for key, value in DEFAULT_SESSION_VALUES.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ====================================
# CSS
# ====================================

st.markdown("""
<style>

.stApp {
    background: #0f172a;
    color: #f8fafc;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 4rem;
    max-width: 760px;
}

h1, h2, h3 {
    color: #f8fafc;
}

div[data-baseweb="select"] > div,
.stTextInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div {
    border-radius: 14px !important;
}

.stButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 14px;
    border: none;
    background: #22c55e;
    color: white;
    font-weight: 700;
    padding: 12px 14px;
    font-size: 16px;
}

.stButton > button:hover {
    background: #16a34a;
}

.app-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 16px;
}

.status-ok {
    background: rgba(34, 197, 94, 0.15);
    color: #86efac;
    padding: 10px 14px;
    border-radius: 12px;
    font-weight: 700;
    margin-bottom: 12px;
}

.status-ng {
    background: rgba(239, 68, 68, 0.15);
    color: #fca5a5;
    padding: 10px 14px;
    border-radius: 12px;
    font-weight: 700;
    margin-bottom: 12px;
}

.notice-red {
    background: #7f1d1d;
    color: #fee2e2;
    padding: 10px 14px;
    border-radius: 12px;
    font-weight: 700;
    margin-top: 8px;
    margin-bottom: 8px;
}

.user-mini {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

.user-mini img {
    width: 42px;
    height: 42px;
    border-radius: 999px;
    object-fit: cover;
    border: 2px solid #334155;
}

.menu-note {
    color: #cbd5e1;
    font-size: 13px;
    margin-top: 6px;
}

@media (max-width: 640px) {
    .block-container {
        padding-top: 0.8rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
        padding-bottom: 5rem;
    }

    .stButton > button {
        min-height: 52px;
        font-size: 16px;
    }
}

</style>
""", unsafe_allow_html=True)

# ====================================
# ログイン画面
# ====================================

if not st.session_state.logged_in:

    st.title("重点項目管理")

    users_df = get_users_df()

    if len(users_df) > 0:
        users_df = users_df[users_df["is_active"] == 1]

    if len(users_df) == 0:
        st.error("users シートに在籍者がいません。")
        st.stop()

    users_df = users_df.sort_values(
        by=["role", "name"],
        ascending=[False, True]
    )

    user_options = ["職員を選択してください"] + [
        f"{row['name']}（{role_label(row['role'])}）"
        for _, row in users_df.iterrows()
    ]

    selected_user_label = st.selectbox(
        "職員選択",
        user_options
    )

    selected_user_name = None
    if selected_user_label != "職員を選択してください":
        selected_user_name = selected_user_label.split("（")[0]

    if st.button("ログイン"):

        if not selected_user_name:
            st.warning("職員を選択してください")
        else:
            selected_df = users_df[users_df["name"] == selected_user_name]

            if len(selected_df) > 0:
                user_data = selected_df.iloc[0]
                st.session_state.logged_in = True
                st.session_state.user_name = user_data["name"]
                st.session_state.role = user_data["role"]
                st.session_state.selected_menu = "ホーム"
                st.rerun()

# ====================================
# ログイン後の基本画面
# ====================================

else:

    current_month = datetime.now().strftime("%Y-%m")
    unread_count = get_unread_count_for_user(st.session_state.user_name)

    st.title("重点項目管理")

    my_icon = get_user_icon(st.session_state.user_name)
    st.markdown(
        f'''
        <div class="user-mini">
            <img src="{my_icon}">
            <div>
                <div style="font-weight:700; color:#f8fafc;">{st.session_state.user_name}</div>
                <div style="font-size:13px; color:#cbd5e1;">{role_label(st.session_state.role)}</div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    if st.session_state.role == "leader":
        menu_options = [
            "ホーム",
            "入力",
            "履歴",
            "確認",
            "集計",
            "管理",
            "設定"
        ]
    else:
        chat_name = "連絡"
        if unread_count > 0:
            chat_name = f"連絡 🔴{unread_count}"

        menu_options = [
            "ホーム",
            "入力",
            chat_name,
            "履歴",
            "設定"
        ]

    default_menu = st.session_state.get("selected_menu", "ホーム")

    if default_menu not in menu_options:
        default_menu = menu_options[0]

    if st.session_state.force_input:
        default_menu = "入力"
        st.session_state.force_input = False

    selected = option_menu(
        menu_title=None,
        options=menu_options,
        orientation="horizontal",
        default_index=menu_options.index(default_menu),
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#111827",
                "border-radius": "14px",
                "border": "1px solid #1f2937",
                "margin-bottom": "14px"
            },
            "icon": {"color": "white", "font-size": "14px"},
            "nav-link": {
                "font-size": "14px",
                "font-weight": "700",
                "text-align": "center",
                "margin": "0px",
                "padding": "12px 8px",
                "color": "#e2e8f0",
                "border-radius": "10px"
            },
            "nav-link-selected": {
                "background-color": "#22c55e",
                "color": "white"
            }
        }
    )

    st.session_state.selected_menu = selected

    # ====================================
    # ホーム（基本版）
    # ====================================

    if selected == "ホーム":

        st.subheader("ホーム")

        entries_df = get_entries_df()
        submitted_df = entries_df[
            (entries_df["user_name"] == st.session_state.user_name)
            &
            (entries_df["month"] == current_month)
        ]

        if len(submitted_df) > 0:
            st.markdown(
                f'<div class="status-ok">{current_month} 提出済み</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="status-ng">{current_month} 未提出</div>',
                unsafe_allow_html=True
            )

        if st.session_state.role != "leader" and unread_count > 0:
            st.markdown(
                f'<div class="notice-red">リーダーから {unread_count} 件の未読連絡があります</div>',
                unsafe_allow_html=True
            )

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown(f"**対象月**: {current_month}")
        st.markdown(f"**名前**: {st.session_state.user_name}")
        st.markdown(f"**権限**: {role_label(st.session_state.role)}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.caption("Part2 で入力機能・下書き保存・提出更新を追加します。")

    # ====================================
    # 入力（基本枠のみ）
    # ====================================

    elif selected == "入力":
        st.subheader("重点項目入力")

    # ====================================
    # 連絡（基本枠のみ）
    # ====================================

    elif "連絡" in selected:
        st.subheader("リーダーとの連絡")

    # ====================================
    # 履歴（基本枠のみ）
    # ====================================

    elif selected == "履歴":
        st.subheader("履歴")

    # ====================================
    # 確認（基本枠のみ）
    # ====================================

    elif selected == "確認" and st.session_state.role == "leader":
        st.subheader("確認")

    # ====================================
    # 集計（基本枠のみ）
    # ====================================

    elif selected == "集計" and st.session_state.role == "leader":
        st.subheader("集計")

    # ====================================
    # 管理（基本枠のみ）
    # ====================================

    elif selected == "管理" and st.session_state.role == "leader":
        st.subheader("管理")

    # ====================================
    # 設定（基本枠のみ）
    # ====================================

    elif selected == "設定":
        st.subheader("設定")

    # ====================================
    # ログアウト
    # ====================================

    st.divider()

    if st.button("ログアウト"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.role = ""
        st.session_state.selected_staff = None
        st.session_state.selected_room_user = None
        st.session_state.edit_entry_id = None
        st.session_state.edit_draft_id = None
        st.session_state.selected_menu = "ホーム"
        st.rerun()
# ====================================
# Part2 共通関数
# ====================================

def find_row_number_by_id(ws, target_id):
    values = ws.get_all_values()
    if len(values) <= 1:
        return None

    for i, row in enumerate(values[1:], start=2):
        if len(row) > 0 and str(row[0]) == str(target_id):
            return i
    return None


def get_user_month_draft(user_name, month):
    drafts_df = get_drafts_df()
    if len(drafts_df) == 0:
        return None

    target_df = drafts_df[
        (drafts_df["user_name"] == user_name)
        &
        (drafts_df["month"] == month)
    ]

    if len(target_df) == 0:
        return None

    target_df = target_df.sort_values("updated_at", ascending=False)
    return target_df.iloc[0]


def get_entry_by_id(entry_id):
    entries_df = get_entries_df()
    if len(entries_df) == 0:
        return None

    target_df = entries_df[
        entries_df["id"].astype(str) == str(entry_id)
    ]

    if len(target_df) == 0:
        return None

    return target_df.iloc[0]


def delete_draft_by_id(draft_id):
    row_num = find_row_number_by_id(drafts_sheet, draft_id)
    if row_num:
        drafts_sheet.delete_rows(row_num)


def save_draft_record(
    draft_id,
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
    proposal
):
    existing = None
    drafts_df = get_drafts_df()

    if len(drafts_df) > 0:
        existing_df = drafts_df[
            (drafts_df["user_name"] == user_name)
            &
            (drafts_df["month"] == month)
        ]
        if len(existing_df) > 0:
            existing = existing_df.iloc[0]

    values = [[
        draft_id,
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
        now_str()
    ]]

    if existing is not None:
        row_num = find_row_number_by_id(drafts_sheet, existing["id"])
        if row_num:
            drafts_sheet.update(
                f"A{row_num}:M{row_num}",
                values
            )
        else:
            drafts_sheet.append_row(values[0])
    else:
        drafts_sheet.append_row(values[0])


def submit_entry_record(
    entry_id,
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
    is_edit=False
):
    values = [[
        entry_id,
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
        now_str(),
        "提出済み"
    ]]

    if is_edit:
        row_num = find_row_number_by_id(entries_sheet, entry_id)
        if row_num:
            entries_sheet.update(
                f"A{row_num}:N{row_num}",
                values
            )
        else:
            entries_sheet.append_row(values[0])
    else:
        entries_sheet.append_row(values[0])

    # 同月の下書きがあれば削除
    draft_row = get_user_month_draft(user_name, month)
    if draft_row is not None:
        delete_draft_by_id(draft_row["id"])


def build_input_default_data():
    blank = {
        "service1": "",
        "service2": "",
        "income1": "",
        "income2": "",
        "expense1": "",
        "expense2": "",
        "time1": "",
        "time2": "",
        "proposal": "",
    }

    month = datetime.now().strftime("%Y-%m")

    # 1. 編集中の提出データを最優先
    if st.session_state.edit_entry_id:
        edit_data = get_entry_by_id(st.session_state.edit_entry_id)
        if edit_data is not None:
            return {
                "month": edit_data["month"],
                "service1": edit_data["service1"],
                "service2": edit_data["service2"],
                "income1": edit_data["income1"],
                "income2": edit_data["income2"],
                "expense1": edit_data["expense1"],
                "expense2": edit_data["expense2"],
                "time1": edit_data["time1"],
                "time2": edit_data["time2"],
                "proposal": edit_data["proposal"],
            }

    # 2. 同月の下書き
    draft = get_user_month_draft(st.session_state.user_name, month)
    if draft is not None:
        return {
            "month": draft["month"],
            "service1": draft["service1"],
            "service2": draft["service2"],
            "income1": draft["income1"],
            "income2": draft["income2"],
            "expense1": draft["expense1"],
            "expense2": draft["expense2"],
            "time1": draft["time1"],
            "time2": draft["time2"],
            "proposal": draft["proposal"],
        }

    data = {"month": month}
    data.update(blank)
    return data

# ====================================
# Part2 画面追加描画
# Part1 の後ろに追記される前提
# ====================================

if st.session_state.logged_in:

    # ====================================
    # 入力（本体）
    # ====================================

    if selected == "入力":

        st.markdown("---")
        st.markdown("### 入力フォーム")

        default_data = build_input_default_data()
        current_month_for_input = datetime.now().strftime("%Y-%m")

        month = st.selectbox(
            "月",
            [current_month_for_input],
            index=0,
            key="part2_month_select"
        )

        service1 = st.text_area(
            "サービス①",
            value=default_data["service1"],
            key="part2_service1"
        )
        service2 = st.text_area(
            "サービス②",
            value=default_data["service2"],
            key="part2_service2"
        )

        income1 = st.text_area(
            "収入①",
            value=default_data["income1"],
            key="part2_income1"
        )
        income2 = st.text_area(
            "収入②",
            value=default_data["income2"],
            key="part2_income2"
        )

        expense1 = st.text_area(
            "経費①",
            value=default_data["expense1"],
            key="part2_expense1"
        )
        expense2 = st.text_area(
            "経費②",
            value=default_data["expense2"],
            key="part2_expense2"
        )

        time1 = st.text_area(
            "時間①",
            value=default_data["time1"],
            key="part2_time1"
        )
        time2 = st.text_area(
            "時間②",
            value=default_data["time2"],
            key="part2_time2"
        )

        proposal = st.text_area(
            "リーダー提案",
            value=default_data["proposal"],
            key="part2_proposal"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("下書き保存", key="part2_save_draft"):
                draft_id = str(datetime.now().timestamp())
                save_draft_record(
                    draft_id=draft_id,
                    user_name=st.session_state.user_name,
                    month=month,
                    service1=service1,
                    service2=service2,
                    income1=income1,
                    income2=income2,
                    expense1=expense1,
                    expense2=expense2,
                    time1=time1,
                    time2=time2,
                    proposal=proposal
                )
                st.success("下書き保存しました")
                st.rerun()

        with col2:
            if st.button("提出", key="part2_submit"):
                if st.session_state.edit_entry_id:
                    submit_entry_record(
                        entry_id=str(st.session_state.edit_entry_id),
                        user_name=st.session_state.user_name,
                        month=month,
                        service1=service1,
                        service2=service2,
                        income1=income1,
                        income2=income2,
                        expense1=expense1,
                        expense2=expense2,
                        time1=time1,
                        time2=time2,
                        proposal=proposal,
                        is_edit=True
                    )
                    st.session_state.edit_entry_id = None
                    st.success("更新しました")
                    st.rerun()
                else:
                    entry_id = str(datetime.now().timestamp())
                    submit_entry_record(
                        entry_id=entry_id,
                        user_name=st.session_state.user_name,
                        month=month,
                        service1=service1,
                        service2=service2,
                        income1=income1,
                        income2=income2,
                        expense1=expense1,
                        expense2=expense2,
                        time1=time1,
                        time2=time2,
                        proposal=proposal,
                        is_edit=False
                    )
                    st.success("提出しました")
                    st.rerun()

        if st.session_state.edit_entry_id:
            if st.button("編集をやめる", key="part2_cancel_edit"):
                st.session_state.edit_entry_id = None
                st.rerun()

    # ====================================
    # 履歴（本体）
    # ====================================

    if selected == "履歴":

        st.markdown("---")
        st.markdown("### 履歴一覧")

        entries_df = get_entries_df()

        history_df = entries_df[
            entries_df["user_name"] == st.session_state.user_name
        ]

        if len(history_df) == 0:
            st.info("履歴はまだありません")
        else:
            history_df = history_df.sort_values(
                by=["month", "created_at"],
                ascending=[False, False]
            )

            for _, row in history_df.iterrows():
                with st.container(border=True):
                    st.markdown(f"### {row['month']}")
                    st.write(f"**状態**: {row.get('status', '提出済み')}")
                    st.write(f"**作成日時**: {row['created_at']}")

                    with st.expander("内容を見る"):
                        st.markdown(f"**サービス①**\n\n{row['service1']}")
                        st.markdown(f"**サービス②**\n\n{row['service2']}")
                        st.markdown(f"**収入①**\n\n{row['income1']}")
                        st.markdown(f"**収入②**\n\n{row['income2']}")
                        st.markdown(f"**経費①**\n\n{row['expense1']}")
                        st.markdown(f"**経費②**\n\n{row['expense2']}")
                        st.markdown(f"**時間①**\n\n{row['time1']}")
                        st.markdown(f"**時間②**\n\n{row['time2']}")
                        st.markdown(f"**リーダー提案**\n\n{row['proposal']}")

                    if st.button("この内容を編集", key=f"part2_edit_{row['id']}"):
                        st.session_state.edit_entry_id = row["id"]
                        st.session_state.force_input = True
                        st.session_state.selected_menu = "入力"
                        st.rerun()

st.markdown("""
<style>
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 8px;
    margin-bottom: 12px;
}

.chat-row {
    display: flex;
    align-items: flex-end;
    gap: 8px;
}

.chat-row.me {
    justify-content: flex-end;
}

.chat-row.other {
    justify-content: flex-start;
}

.chat-icon {
    width: 36px;
    height: 36px;
    border-radius: 999px;
    object-fit: cover;
    border: 1px solid #334155;
    flex-shrink: 0;
}

.chat-bubble {
    max-width: 78%;
    padding: 10px 12px;
    border-radius: 16px;
    line-height: 1.6;
    font-size: 14px;
    white-space: pre-wrap;
    word-break: break-word;
}

.chat-bubble.me {
    background: #22c55e;
    color: white;
    border-bottom-right-radius: 6px;
}

.chat-bubble.other {
    background: #1e293b;
    color: #f8fafc;
    border-bottom-left-radius: 6px;
    border: 1px solid #334155;
}

.chat-meta {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 4px;
}

.read-label {
    display: inline-block;
    margin-left: 6px;
    font-size: 10px;
    color: #bfdbfe;
    font-weight: 700;
}

.room-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
}

.room-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.room-name {
    font-weight: 800;
    color: #f8fafc;
    font-size: 16px;
}

.room-sub {
    color: #cbd5e1;
    font-size: 13px;
    margin-top: 6px;
}

.badge-ok {
    display: inline-block;
    background: rgba(34, 197, 94, 0.15);
    color: #86efac;
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 700;
}

.badge-ng {
    display: inline-block;
    background: rgba(239, 68, 68, 0.15);
    color: #fca5a5;
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 700;
}

.small-muted {
    color: #94a3b8;
    font-size: 12px;
}

.priority-box {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
}

.priority-box h4 {
    margin: 0 0 10px 0;
    color: #f8fafc;
}

@media (max-width: 640px) {
    .chat-bubble {
        max-width: 84%;
        font-size: 14px;
    }

    .room-head {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>
""", unsafe_allow_html=True)

# ====================================
# Part3 共通関数
# ====================================

def get_current_month_str():
    return datetime.now().strftime("%Y-%m")


def get_active_staff_df():
    users_df = get_users_df()
    if len(users_df) == 0:
        return users_df

    return users_df[
        (users_df["role"] == "staff")
        &
        (users_df["is_active"] == 1)
    ].sort_values("name")


def get_leader_name():
    users_df = get_users_df()
    if len(users_df) == 0:
        return "リーダー"

    leader_df = users_df[
        (users_df["role"] == "leader")
        &
        (users_df["is_active"] == 1)
    ]

    if len(leader_df) == 0:
        return "リーダー"

    return str(leader_df.iloc[0]["name"])


def get_entry_for_user_month(user_name, month):
    entries_df = get_entries_df()
    if len(entries_df) == 0:
        return None

    target_df = entries_df[
        (entries_df["user_name"] == user_name)
        &
        (entries_df["month"] == month)
    ]

    if len(target_df) == 0:
        return None

    target_df = target_df.sort_values("created_at", ascending=False)
    return target_df.iloc[0]


def get_submit_status(user_name, month):
    row = get_entry_for_user_month(user_name, month)
    if row is None:
        return "未提出"
    return str(row.get("status", "提出済み") or "提出済み")


def save_chat_message(room_user, sender_name, sender_role, message, month):
    text = str(message).strip()
    if text == "":
        return False

    message_id = str(datetime.now().timestamp())
    icon = get_user_icon(sender_name)

    messages_sheet.append_row([
        message_id,
        room_user,
        sender_name,
        sender_role,
        text,
        month,
        0,
        now_str(),
        "",
        icon
    ])
    return True


def get_room_messages(room_user, month):
    messages_df = get_messages_df()
    if len(messages_df) == 0:
        return messages_df

    room_df = messages_df[
        (messages_df["room_user"] == room_user)
        &
        (messages_df["month"] == month)
    ].copy()

    if len(room_df) == 0:
        return room_df

    room_df = room_df.sort_values("created_at", ascending=True)
    return room_df


def mark_room_messages_as_read(room_user, viewer_name, month):
    values = messages_sheet.get_all_values()
    if len(values) <= 1:
        return

    for idx, row in enumerate(values[1:], start=2):
        row = row + [""] * (10 - len(row))
        row_room_user = str(row[1])
        row_sender_name = str(row[2])
        row_month = str(row[5])
        row_is_read = str(row[6])

        if (
            row_room_user == str(room_user)
            and row_month == str(month)
            and row_sender_name != str(viewer_name)
            and row_is_read != "1"
        ):
            messages_sheet.update_cell(idx, 7, 1)
            messages_sheet.update_cell(idx, 9, now_str())


def get_room_unread_count(room_user, viewer_name, month):
    room_df = get_room_messages(room_user, month)
    if len(room_df) == 0:
        return 0

    unread_df = room_df[
        (room_df["sender_name"] != viewer_name)
        &
        (room_df["is_read"] == 0)
    ]
    return len(unread_df)


def get_latest_room_message(room_user, month):
    room_df = get_room_messages(room_user, month)
    if len(room_df) == 0:
        return "", ""

    row = room_df.iloc[-1]
    return str(row.get("message", "")), str(row.get("created_at", ""))


def build_leader_confirm_rows(month):
    staff_df = get_active_staff_df()
    rows = []

    for _, user_row in staff_df.iterrows():

        staff_name = str(user_row["name"])

        rows.append({
            "name": staff_name,
            "status": "テスト",
            "latest_message": "",
            "latest_at": "",
            "unread_count": 0,
            "icon_url": default_icon_url()
        })

    return rows


def render_priority_summary_for_leader(user_name, month):
    row = get_entry_for_user_month(user_name, month)

    st.markdown('<div class="priority-box">', unsafe_allow_html=True)
    st.markdown(f"#### {user_name} の重点項目（{month}）")

    if row is None:
        st.info("この職員の今月の提出はまだありません。")
    else:
        st.markdown(f"**提出状況**: {row.get('status', '提出済み')}")
        st.markdown(f"**サービス①**\n\n{row.get('service1', '')}")
        st.markdown(f"**サービス②**\n\n{row.get('service2', '')}")
        st.markdown(f"**収入①**\n\n{row.get('income1', '')}")
        st.markdown(f"**収入②**\n\n{row.get('income2', '')}")
        st.markdown(f"**経費①**\n\n{row.get('expense1', '')}")
        st.markdown(f"**経費②**\n\n{row.get('expense2', '')}")
        st.markdown(f"**時間①**\n\n{row.get('time1', '')}")
        st.markdown(f"**時間②**\n\n{row.get('time2', '')}")
        st.markdown(f"**リーダー提案**\n\n{row.get('proposal', '')}")

    st.markdown('</div>', unsafe_allow_html=True)


def render_chat_block(room_user, month):
    mark_room_messages_as_read(room_user, st.session_state.user_name, month)
    room_df = get_room_messages(room_user, month)

    if len(room_df) == 0:
        st.info("まだメッセージはありません。")
        return

    html_parts = ['<div class="chat-wrap">']

    for _, row in room_df.iterrows():
        sender_name = str(row.get("sender_name", ""))
        is_me = sender_name == st.session_state.user_name
        icon_url = str(row.get("icon_url", "") or "").strip()
        if icon_url == "":
            icon_url = get_user_icon(sender_name)

        bubble_class = "me" if is_me else "other"
        row_class = "me" if is_me else "other"
        read_label = ""

        try:
            is_read_flag = int(row.get("is_read", 0))
        except:
            is_read_flag = 0

        if is_me and is_read_flag == 1:
            read_label = '<span class="read-label">既読</span>'

        msg = str(row.get("message", ""))
        msg = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        msg = msg.replace("\n", "<br>")

        created_at = str(row.get("created_at", ""))

        if is_me:
            html_parts.append(
                f'''
                <div class="chat-row {row_class}">
                    <div>
                        <div class="chat-bubble {bubble_class}">{msg}</div>
                        <div class="chat-meta" style="text-align:right;">{created_at}{read_label}</div>
                    </div>
                </div>
                '''
            )
        else:
            html_parts.append(
                f'''
                <div class="chat-row {row_class}">
                    <img class="chat-icon" src="{icon_url}">
                    <div>
                        <div class="small-muted">{sender_name}</div>
                        <div class="chat-bubble {bubble_class}">{msg}</div>
                        <div class="chat-meta">{created_at}</div>
                    </div>
                </div>
                '''
            )

    html_parts.append('</div>')
    st.markdown("".join(html_parts), unsafe_allow_html=True)

# ====================================
# Part3 画面追加描画
# ====================================

if st.session_state.logged_in:

    current_month = get_current_month_str()

    # ====================================
    # 職員側 連絡（個別チャット）
    # ====================================

    if "連絡" in selected and st.session_state.role != "leader":
        st.markdown("---")
        st.markdown("### リーダーとの個別チャット")

        leader_name = get_leader_name()
        st.caption(f"対象月: {current_month} / ルーム: {st.session_state.user_name}")

        render_chat_block(st.session_state.user_name, current_month)

        staff_message = st.text_area(
            "メッセージ入力",
            key="part3_staff_message",
            placeholder=f"{leader_name} にメッセージを送る"
        )

        if st.button("送信", key="part3_staff_send"):
            if str(staff_message).strip() == "":
                st.warning("メッセージを入力してください")
            else:
                save_chat_message(
                    room_user=st.session_state.user_name,
                    sender_name=st.session_state.user_name,
                    sender_role=st.session_state.role,
                    message=staff_message,
                    month=current_month
                )
                st.success("送信しました")
                st.rerun()

    # ====================================
    # リーダー側 確認一覧 + 個別チャット
    # ====================================

    if selected == "確認" and st.session_state.role == "leader":
        st.markdown("---")
        st.markdown("### 確認画面")

        if not st.session_state.selected_room_user:
            st.caption(f"対象月: {current_month}")
            leader_rows = build_leader_confirm_rows(current_month)

            if len(leader_rows) == 0:
                st.info("表示できる職員がいません")
            else:
                for row in leader_rows:
                    status_badge = (
                        f'<span class="badge-ok">{row["status"]}</span>'
                        if row["status"] == "提出済み"
                        else f'<span class="badge-ng">{row["status"]}</span>'
                    )

                    latest_text = row["latest_message"] if row["latest_message"] else "メッセージはまだありません"
                    unread_text = f'未読 {row["unread_count"]} 件' if row["unread_count"] > 0 else '未読なし'

                    st.markdown(
                        f'''
                        <div class="room-card">
                            <div class="room-head">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <img src="{row['icon_url']}" style="width:44px;height:44px;border-radius:999px;object-fit:cover;border:1px solid #334155;">
                                    <div>
                                        <div class="room-name">{row['name']}</div>
                                        <div class="room-sub">{status_badge}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="room-sub">{unread_text}</div>
                            <div class="room-sub">最新: {latest_text}</div>
                            <div class="small-muted">{row['latest_at']}</div>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )

                    if st.button(f"{row['name']} を確認する", key=f"part3_open_room_{row['name']}"):
                        st.session_state.selected_room_user = row["name"]
                        st.rerun()

        else:
            target_user = st.session_state.selected_room_user

            top1, top2 = st.columns([1, 2])
            with top1:
                if st.button("一覧に戻る", key="part3_back_to_confirm_list"):
                    st.session_state.selected_room_user = None
                    st.rerun()
            with top2:
                st.markdown(f"#### {target_user} との個別チャット")

            render_priority_summary_for_leader(target_user, current_month)
            render_chat_block(target_user, current_month)

            leader_message = st.text_area(
                "メッセージ入力",
                key="part3_leader_message",
                placeholder=f"{target_user} にメッセージを送る"
            )

            if st.button("送信", key="part3_leader_send"):
                if str(leader_message).strip() == "":
                    st.warning("メッセージを入力してください")
                else:
                    save_chat_message(
                        room_user=target_user,
                        sender_name=st.session_state.user_name,
                        sender_role=st.session_state.role,
                        message=leader_message,
                        month=current_month
                    )
                    st.success("送信しました")
                    st.rerun()

def find_user_row_by_name(user_name):
    values = users_sheet.get_all_values()
    if len(values) <= 1:
        return None

    for i, row in enumerate(values[1:], start=2):
        row = row + [""] * (7 - len(row))
        if str(row[1]) == str(user_name):
            return i
    return None


def find_setting_row_by_name(user_name):
    values = settings_sheet.get_all_values()
    if len(values) <= 1:
        return None

    for i, row in enumerate(values[1:], start=2):
        row = row + [""] * (5 - len(row))
        if str(row[0]) == str(user_name):
            return i
    return None


def save_user_icon_setting(user_name, icon_url, use_default_icon):
    icon_url = str(icon_url).strip()
    use_default_flag = 1 if use_default_icon else 0

    setting_values = [[
        user_name,
        icon_url,
        use_default_flag,
        "dark",
        now_str()
    ]]

    setting_row = find_setting_row_by_name(user_name)
    if setting_row:
        settings_sheet.update(f"A{setting_row}:E{setting_row}", setting_values)
    else:
        settings_sheet.append_row(setting_values[0])

    user_row = find_user_row_by_name(user_name)
    if user_row:
        current = users_sheet.row_values(user_row)
        current = current + [""] * (7 - len(current))
        current[4] = icon_url
        current[5] = str(use_default_flag)
        users_sheet.update(f"A{user_row}:G{user_row}", [current[:7]])


def get_next_user_id():
    users_df = get_users_df()
    if len(users_df) == 0:
        return "1"

    ids = pd.to_numeric(users_df["id"], errors="coerce").fillna(0)
    return str(int(ids.max()) + 1)


def add_new_user(user_name, role="staff"):
    user_name = str(user_name).strip()
    if user_name == "":
        return False, "名前を入力してください"

    users_df = get_users_df()
    if len(users_df) > 0:
        dup_df = users_df[users_df["name"] == user_name]
        if len(dup_df) > 0:
            return False, "同じ名前の職員がすでに存在します"

    new_row = [
        get_next_user_id(),
        user_name,
        role,
        1,
        "",
        1,
        now_str()
    ]
    users_sheet.append_row(new_row)
    return True, f"{user_name} を追加しました"


def set_user_active_flag(user_name, is_active):
    row_num = find_user_row_by_name(user_name)
    if not row_num:
        return False, "対象ユーザーが見つかりません"

    current = users_sheet.row_values(row_num)
    current = current + [""] * (7 - len(current))
    current[3] = "1" if is_active else "0"
    users_sheet.update(f"A{row_num}:G{row_num}", [current[:7]])
    return True, "在籍状態を更新しました"


def build_month_list_for_aggregate():
    entries_df = get_entries_df()
    months = []

    if len(entries_df) > 0 and "month" in entries_df.columns:
        months = [
            str(x).strip() for x in entries_df["month"].tolist()
            if str(x).strip() != ""
        ]

    current_month = get_current_month_str()
    if current_month not in months:
        months.append(current_month)

    months = sorted(list(set(months)), reverse=True)
    return months


def build_aggregate_summary(month):
    staff_df = get_active_staff_df()
    entries_df = get_entries_df()

    rows = []
    for _, user_row in staff_df.iterrows():
        user_name = str(user_row["name"])

        submitted_df = entries_df[
            (entries_df["user_name"] == user_name)
            &
            (entries_df["month"] == month)
        ] if len(entries_df) > 0 else pd.DataFrame()

        if len(submitted_df) > 0:
            submitted_df = submitted_df.sort_values("created_at", ascending=False)
            latest = submitted_df.iloc[0]
            status = str(latest.get("status", "提出済み") or "提出済み")
            submitted_at = str(latest.get("created_at", ""))
        else:
            status = "未提出"
            submitted_at = ""

        rows.append({
            "name": user_name,
            "status": status,
            "submitted_at": submitted_at
        })

    summary_df = pd.DataFrame(rows)

    if len(summary_df) == 0:
        return {
            "summary_df": summary_df,
            "submitted_count": 0,
            "unsubmitted_count": 0,
            "staff_count": 0
        }

    submitted_count = len(summary_df[summary_df["status"] == "提出済み"])
    unsubmitted_count = len(summary_df[summary_df["status"] != "提出済み"])

    return {
        "summary_df": summary_df,
        "submitted_count": submitted_count,
        "unsubmitted_count": unsubmitted_count,
        "staff_count": len(summary_df)
    }

# ====================================
# Part4 画面追加描画
# ====================================

if st.session_state.logged_in:

    # ====================================
    # 設定画面
    # ====================================

    if selected == "設定":
        st.markdown("---")
        st.markdown("### 設定")

        current_icon = get_user_icon(st.session_state.user_name)
        settings_df = get_settings_df()
        current_setting = settings_df[
            settings_df["user_name"] == st.session_state.user_name
        ] if len(settings_df) > 0 else pd.DataFrame()

        current_custom_url = ""
        current_use_default = True

        if len(current_setting) > 0:
            row = current_setting.iloc[0]
            current_custom_url = str(row.get("icon_url", "") or "")
            current_use_default = int(row.get("use_default_icon", 1)) == 1
        else:
            users_df = get_users_df()
            me_df = users_df[users_df["name"] == st.session_state.user_name]
            if len(me_df) > 0:
                me = me_df.iloc[0]
                current_custom_url = str(me.get("icon_url", "") or "")
                current_use_default = int(me.get("use_default_icon", 1)) == 1

        st.markdown("#### アイコン設定")
        st.image(current_icon, width=96)

        use_default_icon = st.checkbox(
            "デフォルト画像を使う",
            value=current_use_default,
            key="part4_use_default_icon"
        )

        icon_url_input = st.text_input(
            "カスタム画像URL",
            value=current_custom_url,
            key="part4_icon_url_input",
            placeholder="https://..."
        )

        if st.button("アイコン設定を保存", key="part4_save_icon_setting"):
            save_user_icon_setting(
                user_name=st.session_state.user_name,
                icon_url=icon_url_input,
                use_default_icon=use_default_icon
            )
            st.success("アイコン設定を保存しました")
            st.rerun()

        st.caption("※ デフォルト画像をONにすると、カスタム画像URLを入れていてもデフォルト画像を優先表示します。")

    # ====================================
    # 管理画面（リーダーのみ）
    # ====================================

    if selected == "管理" and st.session_state.role == "leader":
        st.markdown("---")
        st.markdown("### 管理画面")

        with st.expander("新入職者を追加", expanded=True):
            new_user_name = st.text_input(
                "氏名",
                key="part4_new_user_name"
            )
            new_user_role_label = st.selectbox(
                "権限",
                ["職員", "リーダー"],
                index=0,
                key="part4_new_user_role"
            )
            new_user_role = "leader" if new_user_role_label == "リーダー" else "staff"

            if st.button("新しいユーザーを追加", key="part4_add_new_user"):
                ok, msg = add_new_user(new_user_name, new_user_role)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.warning(msg)

        st.markdown("#### 在籍管理")
        users_df = get_users_df()
        if len(users_df) == 0:
            st.info("ユーザーがいません")
        else:
            users_df = users_df.sort_values(by=["is_active", "role", "name"], ascending=[False, False, True])

            for _, row in users_df.iterrows():
                user_name = str(row["name"])
                role_text = role_label(str(row["role"]))
                active_text = "在籍" if int(row.get("is_active", 1)) == 1 else "退職"
                icon_url = get_user_icon(user_name)

                st.markdown(
                    f'''
                    <div class="room-card">
                        <div class="room-head">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <img src="{icon_url}" style="width:42px;height:42px;border-radius:999px;object-fit:cover;border:1px solid #334155;">
                                <div>
                                    <div class="room-name">{user_name}</div>
                                    <div class="room-sub">{role_text} / {active_text}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"{user_name} を在籍にする", key=f"part4_activate_{user_name}"):
                        ok, msg = set_user_active_flag(user_name, True)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.warning(msg)
                with c2:
                    if st.button(f"{user_name} を退職にする", key=f"part4_deactivate_{user_name}"):
                        ok, msg = set_user_active_flag(user_name, False)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.warning(msg)

        st.caption("※ 退職者は削除せず、在籍状態を『退職』にする運用です。")

    # ====================================
    # 集計画面（リーダーのみ）
    # ====================================

    if selected == "集計" and st.session_state.role == "leader":
        st.markdown("---")
        st.markdown("### 集計画面")

        month_options = build_month_list_for_aggregate()
        selected_month_for_agg = st.selectbox(
            "集計対象月",
            month_options,
            index=0,
            key="part4_agg_month"
        )

        agg = build_aggregate_summary(selected_month_for_agg)
        summary_df = agg["summary_df"]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("対象職員数", agg["staff_count"])
        with c2:
            st.metric("提出済み", agg["submitted_count"])
        with c3:
            st.metric("未提出", agg["unsubmitted_count"])

        if len(summary_df) == 0:
            st.info("集計対象データがありません")
        else:
            st.markdown("#### 月次提出状況一覧")
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

            submitted_names = summary_df[summary_df["status"] == "提出済み"]["name"].tolist()
            unsubmitted_names = summary_df[summary_df["status"] != "提出済み"]["name"].tolist()

            st.markdown("#### 提出済み職員")
            if len(submitted_names) == 0:
                st.write("なし")
            else:
                st.write("、".join(submitted_names))

            st.markdown("#### 未提出職員")
            if len(unsubmitted_names) == 0:
                st.write("なし")
            else:
                st.write("、".join(unsubmitted_names))