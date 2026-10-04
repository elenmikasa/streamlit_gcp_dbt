import streamlit as st
from workflow import process_csv_workflow


def login_screen():
    st.header("このアプリは非公開です。")
    st.subheader("Googleアカウントでログインしてください。")
    st.button("Googleでログイン", on_click=st.login)


# 未ログインの場合はログイン画面を表示して処理を止める
if not st.user.is_logged_in:
    login_screen()
    st.stop()

# ─── ログイン済みのユーザー向け画面 ───
st.header(f"ようこそ、{st.user.name}さん！")
st.subheader("エリア需給実績CSVの一括取得・加工")

# ボタンは1つに集約
if st.button("先月のCSVを一括取得・加工してGCSに保存"):
    with st.spinner("全エリアの処理を実行中..."):
        process_csv_workflow()
    st.success("すべての処理が完了しました！")

st.divider()
st.button("ログアウト", on_click=st.logout)