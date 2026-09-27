import streamlit as st

def login_screen():
    st.header("このアプリは非公開です。")
    st.subheader("Googleアカウントでログインしてください。")
    st.button("Googleでログイン", on_click=st.login)

# 未ログインの場合はログイン画面を表示して処理を止める
if not st.user.is_logged_in:
    login_screen()
    st.stop()  # ここで後続のアプリ本体の実行を止める

# ─── ここから下はログイン済みのユーザーだけに表示される本体コード ───
st.header(f"ようこそ、{st.user.name}さん！")
st.write("ここに限定公開したいメインのコンテンツを記述します。")

st.button("ログアウト", on_click=st.logout)