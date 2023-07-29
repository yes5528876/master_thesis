#Project Name: Natural Language Navigation by using ChatGPT
#Author: Jhih-yang Long
#Affiliation: Human and Robot Lab, National Yang Ming Chiao Tung University
#E-mail: yes5528876.en11@nycu.edu.tw

import os,sys
import string
import glob
import unittest, time, re
# import pyperclip
# import pyautogui
import rospy
# from mbf_msgs.msg import MoveBaseActionGoal
from move_base_msgs.msg import MoveBaseActionGoal
import openai
import json
import socket

def fake_request_ChatGPT(system_msg,user_msg):
    text="<command>move_to(-3800,4500)</command>"
    return text


def request_ChatGPT(system_msg,user_msg):
    TOKEN="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"
    openai.api_key = TOKEN

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]
    )

    # print(completion.choices[0].message)

    openai_str=str(completion.choices[0].message)
    data = json.loads(openai_str)
    text = data['content']

    print(text)
    return text

def parse_coordinate(text):
    pattern = r"<command>move_to\((-?\d+),(-?\d+)\)</command>"

    matches = re.findall(pattern, text)
    if matches:
        x, y = matches[-1]
        print("最後一個x:", x)
        print("最後一個y:", y)
    else:
        print("未找到符合的指令")
    return x,y

def send_goal(x,y):
    pub = rospy.Publisher('/move_base/goal', MoveBaseActionGoal, queue_size=1)
    rospy.init_node('my_publisher',anonymous=True)

    goal_msg = MoveBaseActionGoal()

    goal_msg.goal.target_pose.header.frame_id = 'map'
    goal_msg.goal.target_pose.pose.position.x = float(x)/1000
    goal_msg.goal.target_pose.pose.position.y = float(y)/1000
    goal_msg.goal.target_pose.pose.orientation.w = 1.0

    pub.publish(goal_msg)

def is_request_data(data):
    try:
        parsed_data = json.loads(data)
        return isinstance(parsed_data, dict) and ("request" in parsed_data)
    except json.JSONDecodeError:
        return False
    
def is_confirm_data(data):
    try:
        parsed_data = json.loads(data)
        return isinstance(parsed_data, dict) and ("confirm" in parsed_data)
    except json.JSONDecodeError:
        return False

system_msg="有一個環境有以下的物體，物體後面接的是該物體的座標。門口(1000,60)、桌子(-2520,3140)、窗戶(-3800,4500)、書櫃(-6520,4410)。想像你是一個導覽機器人，當你聽到類似於 請移動到XX 或相關描述，就把它轉換成move_to(X,Y)這種嚴格規範的語言格式，並且用<command></command>將指令包覆起來。比如說，你聽到  指令：我想拿一本機器人學的書，就知道應該要帶人去書櫃，就輸出<command>move_to(-6520,4410)</command>"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12343)
sock.bind(server_address)
sock.listen(1)

while True:
    print('waiting for a connection')
    connection, client_address = sock.accept()

    try:
        # print('connection from', client_address)
        while True:
            data = connection.recv(1024)
            decoded_data=data.decode()
            print('received '+decoded_data)
            if(is_request_data(decoded_data)):
                data = json.loads(decoded_data)
                request_value = data["request"]
                text=request_ChatGPT(system_msg,request_value)

                x,y=parse_coordinate(text)
                print("send_goal(x,y)")
                send_goal(x,y)
                # print('sending ChatGPT response back to the client')
                # connection.sendall(text.encode())
            elif(is_confirm_data(decoded_data)):
                x,y=parse_coordinate(text)
                print("send_goal(x,y)")
                send_goal(x,y)
            else:
                print("Wrong format is recieved!")
                

    finally:
        connection.close()
