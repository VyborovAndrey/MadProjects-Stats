from flask import Flask, Response, request
from flask_cors import CORS
import plotly.express as px
import pandas as pd
from random import sample
import requests
import os
from io import StringIO
from math import ceil

guap_colors = ['rgb(231, 15, 71)', 'rgb(0, 184, 238)', 'rgb(0, 152, 170)', 'rgb(80, 45, 127)', 'rgb(139, 35, 70)', 'rgb(0, 90, 170)']
title_style={
        'font_family':'Roboto FLEX',
        'font': {'size': 19},
        'y':0.9,
        'x':0.5,
        'xanchor':'center',
        'yanchor':'top'}


def graph_commits(csv, type='html'):
    df_commits = pd.read_csv(StringIO(csv.decode('utf-8')))
    # Для каждого проекта в соответствие ставим один из цеветов 
    df_commits['colors'] = ([i for i in range(len(guap_colors))] *
                            ceil(df_commits.shape[0]/len(guap_colors)))[:df_commits.shape[0]]
    strip_style = {'data_frame': df_commits,
                'x': 'commits',
                'labels': {'project_name':'Название проекта', 'commits': 'Количество коммитов'},
                'title': "Количество коммитов по проектам",
                'hover_data': {'project_name': True,
                            'commits': True,
                            'colors': False},
                'color': 'colors',
                'stripmode': 'overlay',
                'color_discrete_sequence': guap_colors}
    fig_commits = px.strip(**strip_style)
    fig_commits.update_layout(title = title_style)
    fig_commits.update(layout_showlegend=False)
    if type == 'html':
        return fig_commits.to_html()
    elif type == 'png':
        return fig_commits.to_image(format="png")
    
def graph_statuses(csv, type='png'):
    df_status = pd.read_csv(StringIO(csv.decode('utf-8')))
    bar_status_style = {'data_frame': df_status,
                'x': 'status',
                'labels': {'count': 'Количество проектов', 'status': 'Статус проекта'},
                'title': "Статусы проектов"}
    fig_status = px.bar(**bar_status_style)
    fig_status.update_layout(**title_style)
    if type == 'html':
        return fig_status.to_html()
    elif type == 'png':
        return fig_status.to_image(format="png")

def graph_grades(csv, type='png'):
    df_grades = pd.read_csv(StringIO(pd.read_csv(StringIO(csv.decode('utf-8')))))
    bar_grades_style = {'data_frame': df_grades,
                'x': 'grade',
                'labels': {'count': 'Количество проектов', 'grade': 'Оценка проекта'},
                'title': "Оценки проектов"}
    fig_grades = px.pie(**bar_grades_style)
    fig_grades.update_layout(**title_style)
    if type == 'html':
        return fig_grades.to_html()
    elif type == 'png':
        return fig_grades.to_image(format="png")

def graph_user_commits(csv, type='png'):
    df_commits_user = pd.read_csv(StringIO(csv.decode('utf-8')))
    pie_style = {'data_frame': df_commits_user,
                'labels': {'commits': 'Коммитов', 'name': 'Имя'},
                'values': 'commits',
                'names': 'name',
                'hole': .7, 
                'color_discrete_sequence': sample(guap_colors, df_commits_user.shape[0]),
                'title': "Количество коммитов по участникам"}
    fig_commits_user = px.pie(**pie_style)
    fig_commits_user.update_layout(**title_style)
    if type == 'html':
        return fig_commits_user.to_html()
    elif type == 'png':
        return fig_commits_user.to_image(format="png")

app = Flask(__name__)
CORS(app, resources={ r"/*": {"origins": "http://localhost:3000/ https://kaelesty.ru/" }})

@app.route("/hello", methods=['GET'])
def hello():
    return Response('hello lenya')

@app.route("/graph_commits", methods=['GET'])
def GET_graph_commits():
    type = request.args.get('type')
    groupId = request.args.get('groupId')
    token = request.args.get('token')
    csv = requests.get(f'https://kaelesty.ru:8080/analytics/projectCommits?groupId={groupId}',
                        headers = {'Authorization': f'Bearer {token}'}).content
    return Response(graph_commits(csv, type))

@app.route("/graph_user_commits", methods=['GET'])
def GET_graph_user_commits():
    type = request.args.get('type')
    projectId = request.args.get('projectId')
    token = request.args.get('token')
    csv = requests.get(f'https://kaelesty.ru:8080/analytics/userCommits?projectId={projectId}',
                        headers = {'Authorization': f'Bearer {token}'}).content
    return Response(graph_user_commits(csv, type))

@app.route("/graph_statuses", methods=['GET'])
def GET_graph_statuses():
    type = request.args.get('type')
    groupId = request.args.get('groupId')
    token = request.args.get('token')
    csv = requests.get(f'https://kaelesty.ru:8080/analytics/projectStatuses?groupId={groupId}',
                        headers = {'Authorization': f'Bearer {token}'}).content
    print(csv)
    zapros = requests.get(f'https://kaelesty.ru:8080/analytics/projectGradses?groupId={groupId}',
                        headers = {'Authorization': f'Bearer {token}'})
    print(zapros)   
    return Response(graph_statuses(csv, type))

@app.route("/graph_grades", methods=['GET'])
def GET_graph_grades():
    type = request.args.get('type')
    groupId = request.args.get('groupId')
    token = request.args.get('token')
    csv = requests.get(f'https://kaelesty.ru:8080/analytics/projectGradses?groupId={groupId}',
                        headers = {'Authorization': f'Bearer {token}'}).content
    return Response(graph_grades(csv, type))


 
if __name__ == "__main__":
    cert = '/etc/letsencrypt/live/kaelesty.ru/fullchain.pem'
    key = '/etc/letsencrypt/live/kaelesty.ru/privkey.pem'
    context = (cert, key)
    app.run(port=5002, ssl_context=context)