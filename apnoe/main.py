import streamlit as st
import pandas as pd

import plotly.graph_objects as go
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


def save_config(config):
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)


def login_user():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )
    authenticator.login(clear_on_submit=True)
    return authenticator, config


def reset_password(authenticator, config):
    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"], location='sidebar'):
                st.success('Password modified successfully')
                save_config(config)
        except Exception as e:
            st.error(e)


def create_user(authenticator, config):
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(
            pre_authorization=True, location='sidebar')
        if email_of_registered_user:
            st.success('User registered successfully')
            save_config(config)
    except Exception as e:
        st.error(e)


def auth():
    authenticator, config = login_user()
    if not st.session_state["authentication_status"]:
        create_user(authenticator, config)
    if st.session_state["authentication_status"]:
        authenticator.logout()
        st.write(f'Добро пожаловать *{st.session_state["name"]}*')
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')

    reset_password(authenticator, config)
    return authenticator, config

def draw_visualization():
    patients = [7, 37]
    uploaded_file = st.sidebar.file_uploader('Выберите файл для загрузки', accept_multiple_files=True)
    tabs = st.tabs([str(patient) for patient in patients])
    for tab, patient in zip(tabs, patients):
        draw_tab(tab, patient)


def get_similar_patients(patient):
    if patient == 7:
        return [6]
    if patient == 37:
        return [36]


def draw_tab(tab, patient):
    tab.header(f"Идентификатор пациента: {patient}", divider='rainbow')
    user_df = pd.read_csv(f'data/base_data_num_patient_{patient}.csv')
    tab.table(user_df)
    tab.divider()
    if patient == 7:
        tab.text('Статус пациента: здоров')
        tab.text(f'Принадлежит к здоровому типу с уверенностью 95%')
        tab.text(f'В данных количество эпизодов апноэ отсутствует')
    if patient == 37:
        tab.text('Статус пациента: тяжелая степень апноэ')
        tab.text(f'Принадлежность к тяжелому типу с уверенностью 93%')
        tab.text(f'В данных зафиксировано 668 эпизодов апноэ')
    similar_patients = get_similar_patients(patient)
    similar_patients_selector = tab.multiselect('Похожие случаи', similar_patients, key=patient)
    draw_plot(tab, patient, similar_patients_selector)


def config_figure(fig, title, showlegend=True):
    fig.update_layout(
        plot_bgcolor='rgba(58,240,18,0.1)',
        title_text=title,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=30,
                         label="30 минут",
                         step="minute",
                         stepmode="backward"),
                    dict(count=1,
                         label="1 час",
                         step="hour",
                         stepmode="backward"),
                ]),
                font=dict(color='indigo',
                          size=15,
                          family='Droid Serif')
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        ),
        yaxis=dict(
            anchor="x",
            autorange=True,
            linecolor='rgba(29,11,142,1)',
            side="right",
            title="01-m2",
            titlefont={"color": 'rgba(29,11,142,1)'},
            type="linear",
        ),
        showlegend=showlegend
    )


def draw_plot(tab, patient, similar_patients):
    df = pd.read_csv(f'data/num_patient_{patient}.csv')
    fig = go.Figure()
    colors = ['rgba(29, 11, 142, 1)',
              'rgba(243, 156, 18, 1)',
              'rgba(142, 68, 173, 1)',
              'rgba(192, 57, 43, 1)',
              'rgba(186, 74, 0, 1)']

    for (name, group), color in zip(df.groupby('filter'), colors):
        fig.add_trace(go.Scatter(x=list(group.time),
                                 y=list(group.value),
                                 name=f'{patient}_{name}',
                                 line=dict(color=color, width=3)))

    comments = []
    for patient in similar_patients:
        df = pd.read_csv(f'data/num_patient_{patient}.csv')
        for (name, group), color in zip(df.groupby('filter'), colors):
            fig.add_trace(go.Scatter(x=list(group.time),
                                     y=list(group.value),
                                     name=f'схожий_пациент_{patient}_{name}',
                                     line=dict(color=color, width=1, dash='dash')))
        comments.append(f'Полезная информация по поставленному диагнозу для пациента {patient}')

    config_figure(fig, title="График ЭЭГ")
    tab.plotly_chart(fig, use_container_width=True)

    for comment in comments:
        tab.markdown(f'''<p style="background-color:#90ee90">{comment}</p>''',
                    unsafe_allow_html=True)  # либо маркдаун либо фон но html css

    df_box_plot = pd.read_csv(f'data/box_plot_num_patient_{patient}.csv')
    fig_box = go.Figure()
    for time, group in df_box_plot.groupby('time'):
        fig_box.add_trace(go.Box(
            y=group['value'],
            jitter=0.5,
            whiskerwidth=0.2,
            name=time,
            boxpoints='outliers',
            notched=True,
            marker_color='rgb(107,174,214)',
        ))

    config_figure(fig_box, title="Box plot ЭЭГ", showlegend=False)
    tab.plotly_chart(fig_box, use_container_width=True)


if __name__ == '__main__':
    authenticator, config = auth()

    if st.session_state["authentication_status"]:
        draw_visualization()


