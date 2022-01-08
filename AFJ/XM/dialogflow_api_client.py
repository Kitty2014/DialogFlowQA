# -*- encoding: utf-8 -*-
'''
@File    :   pd.py
@Contact :   emac.li@cloudminds.com
@License :   (C)Copyright 2018-2021

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/12/4 6:20 下午   Emac.li      1.0         None
'''

import datetime
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import uuid
import argparse
import shutil
import subprocess
import logging
import os
import codecs
import time
import sys
from datetime import date, datetime, timedelta
import zipfile
import threading
import boto.s3.connection
import boto
from robot.api import ExecutionResult
from crontab import CronTab

import croniter
import dialogflow
import dialogflow_v2beta1
import jenkins
from google.api_core.exceptions import InvalidArgument
from google.protobuf.json_format import MessageToDict

import logging
from crontab import CronTab
from sqlalchemy import create_engine, VARCHAR, DATETIME, DATE, NVARCHAR, BigInteger
import pandas as pd
import requests
from chardet import detect
import fire
import pandas as pd
import numpy as np
import os
import uvicorn
from pydantic import BaseModel
from pyhocon import ConfigFactory, HOCONConverter, ConfigTree
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, UploadFile, File

app = FastAPI(
    # 禁用 /docs
    # docs_url=None,
    # 禁用 /redoc
    # redoc_url=None
)

job_start_time = None


class conf_dict(BaseModel):
    customParameters: dict = {
        "项目名称": "BOSS",
        "BugID在索引_的第几个位置": 1,
        "生成的配置文件夹目录": "cases/sit_test/cross_test/",
        "j2配置文件夹目录": "data/templates/cross_test/cross_vending_user",
        "是否覆盖原有配置文件(false/true)": False
    }


class j2_dict(BaseModel):
    customParameters: dict = {
        "项目名称": "HARIX",
        "BugID在索引_的第几个位置": 0,
        "生成的配置文件夹目录": "cases/sit_test/cross_test/",
        "j2配置文件夹目录": "data/templates/cross_test/boss_II"
    }

class j2_sql_dict(BaseModel):
    customParameters: dict = {
        "j2_config": {
            "项目名称": "HARIX",
            "BugID在索引_的第几个位置": 0,
            "生成的配置文件夹目录": "cases/sit_test/cross_test/",
            "j2配置文件夹目录": "data/templates/cross_test/boss_II"
        },
        "db_switch": {
            "db_ip": "localhost",
            "db_port": "3306",
            "db_user": "root",
            "db_password": "123456",
            "db_name": "HARIX_DB",
            "table_name": "HARIX_Render_Case",
            "db_switch_enable": True
        }
    }

class SQL_j2_Dict(BaseModel):
    customParameters: dict = {
        "j2_config": {
            "j2_full_name": [],
            "BugID在索引_的第几个位置": 0,
            "生成的配置文件夹目录": "cases/robot/cross_test/",
            "j2配置文件夹目录": "data/templates/cross_test/boss_II"

        },
        "db_switch": {
            "db_ip": "localhost",
            "db_port": "3306",
            "db_user": "root",
            "db_password": "123456",
            "db_name": "HARIX_DB",
            "table_name": "HARIX_Render_Case",
            "db_switch_enable": True

        }
    }

class JobDict(BaseModel):
    customParameters: dict = {
        "jenkins_config": {
            "server": "http://ip:port/",
            "username": "admin",
            "password": "admin",
            "job_name": "CRS"
        },
        "showTrueOrFalse": {
            "start": True,
            "stop": False,
        }
    }


class DialogFlowDict(BaseModel):
    customParameters: dict = {
        "dialogflow_config": {
            "request_frequency": 3,
            "intent_name_prefix": "Agent",
            "project_id": "fbtest-tfxodj",
            "language_code": "en",

        }
    }


class QADict(BaseModel):
    customParameters: dict = {
        "dialogflow_qa": '南宁国际会展中心可以搭建多少个展位',
        "dialogflow_config": {
            "request_frequency": 3,
            "intent_name_prefix": "Agent",
            "project_id": "fbtest-tfxodj",
            "language_code": "en",

        },
        "db_switch": {
            "db_ip": "localhost",
            "db_port": "3306",
            "db_user": "root",
            "db_password": "123456",
            "db_name": "DialogFlow_DB",
            "table_name": "dialogflow_exec_record",
            "db_switch_enable": True

        }
    }


class WebDict(BaseModel):
    customParameters: dict = {
        "db_switch": {
            'db_ip': '10.155.2.4',
            'db_port': '30065',
            'db_user': 'root',
            'db_password': '123456',
            'db_name': 'BOSS_DB',
            'table_name': 'boss_exec_record',
            "db_switch_enable": True

        }
    }

class DFDict(BaseModel):
    customParameters: dict = {
        "df_action": {"batch_deletion": True, "Single_deletion": False},
        "dialogflow_config": {
            "request_frequency": 3,
            "intent_name_prefix": "意图前缀",
            "project_id": "fbtest-tfxodj",
            "language_code": "en",

        },
        "db_switch": {
            "db_ip": "localhost",
            "db_port": "3306",
            "db_user": "root",
            "db_password": "123456",
            "db_name": "DialogFlow_DB",
            "table_name": "batch_exec_record",
            "db_switch_enable": True

        }
    }

@app.post("/auto_factory_upload")
async def factory(file: UploadFile = File(...)):
    start = time.time()
    try:
        res = await file.read()
        auto_path = os.getcwd() + os.sep + 'data' + os.sep + 'rdp_data' + os.sep + 'Factory' + os.sep
        file_name = 'factory_auto.pak'
        save_path = os.path.join(auto_path, file_name)
        with open(save_path, "wb") as f:
            f.write(res)
            return_rsp = {"message": "success", 'time': time.time() - start, 'filename': file.filename, '文件位置': save_path}
            print()
            print('上传的文件路径是:\n{}'.format(save_path))
        return return_rsp
    except Exception as e:
        print({"message": str(e), 'time': time.time() - start, 'filename': file.filename})

@app.post("/build_robot_config")
async def auto_generation(struct_iterator: conf_dict):
    env_status = build_robot_config(ginger_dict=struct_iterator.dict())
    if env_status and len(env_status) == 2:
        call_back = {
            "Status": env_status[0],
            "Execution_structure": env_status[1]
        }
        return call_back
    else:
        return env_status


@app.post("/update_j2")
async def j2_update(struct_iterator: SQL_j2_Dict):
    db_switch = struct_iterator.customParameters['db_switch']
    if isinstance(db_switch, dict) and isinstance(db_switch['db_switch_enable'], bool) and not db_switch['db_switch_enable']:
        print('db_switch参数:\n{}'.format(db_switch))
        db_dict = {
            'db_ip': 'localhost',
            'db_port': '3306',
            'db_user': 'root',
            'db_password': '123456',
            'db_name': 'HARIX_DB',
            'table_name': 'qa_exec_record',
        }
        db_switch = db_dict
    else:
        db_dict = db_switch
    struct_iterator.customParameters['db_dict'] = db_dict
    env_status = bulk_query(ginger_dict=struct_iterator.dict())
    if env_status and len(env_status) == 3:
        call_back = {
            "Status": env_status[0],
            "Execution_structure": env_status[1],
             "Message": env_status[2]
        }
        return call_back

@app.post("/write_j2_sql")
async def j2_sql(struct_iterator: j2_sql_dict):
    db_switch = struct_iterator.customParameters['db_switch']
    if isinstance(db_switch, dict) and isinstance(db_switch['db_switch_enable'], bool) and not db_switch['db_switch_enable']:
        print('db_switch参数:\n{}'.format(db_switch))
        db_dict = {
            'db_ip': 'localhost',
            'db_port': '3306',
            'db_user': 'root',
            'db_password': '123456',
            'db_name': 'HARIX_DB',
            'table_name': 'qa_exec_record',
        }
        db_switch = db_dict
    else:
        db_dict = db_switch
    struct_iterator.customParameters['db_dict'] = db_dict
    env_status = build_robot_j2(ginger_dict=struct_iterator.dict())
    if env_status and len(env_status) == 3:
        call_back = {
            "Status": env_status[0],
            "Execution_structure": env_status[1],
             "Message": env_status[2]
        }
        return call_back


@app.post("/write_sql_j2")
async def sql_j2(struct_iterator: j2_dict):
    db_dict = {
        'db_ip': 'localhost',
        'db_port': '3306',
        'db_user': 'root',
        'db_password': '123456',
        'db_name': 'HARIX_DB',
    }
    struct_iterator.customParameters['db_dict'] = db_dict
    env_status = sql_write_j2(ginger_dict=struct_iterator.customParameters)
    if env_status and len(env_status) == 2:
        call_back = {
            "Status": env_status[0],
            "Execution_structure": env_status[1],
             "Message": env_status
        }
        return call_back
    else:
        print('返回信息\n{}'.format(env_status))
        return env_status


@app.post("/build_job")
async def jenkins_build(struct_iterator: JobDict):
    db_dict = {
        'db_ip': 'localhost',
        'db_port': '3306',
        'db_user': 'root',
        'db_password': '123456',
        'db_name': 'HARIX_DB',
    }
    struct_iterator.customParameters['db_dict'] = db_dict
    env_status = start_job(ginger_dict=struct_iterator.dict())
    print('callback:\n{}'.format(env_status))
    if isinstance(env_status[1], dict):
        print('当前入参如下:\n{}'.format(json.dumps(env_status[1], ensure_ascii=False, skipkeys=True, separators=(',', ':'))))
    if env_status and len(env_status) == 3:
        call_back = {
            "Status": env_status[0],
            "Message": env_status[2],
            "Execution_structure": env_status[1],
        }
        return call_back
    else:
        return env_status

@app.post("/build_dialogflow_qa")
async def bulk_import_qa(struct_iterator: DialogFlowDict):
    db_dict = {
        'db_ip': 'localhost',
        'db_port': '3306',
        'db_user': 'root',
        'db_password': '123456',
        'db_name': 'DialogFlow_DB',
        'table_name': 'dialogflow_exec_record',
    }
    struct_iterator.customParameters['db_dict'] = db_dict
    env_status = dialogflow_qa(ginger_dict=struct_iterator.dict())
    if env_status and len(env_status) == 3:
        call_back = {
            "Status": env_status[0],
            "Execution_structure": env_status[1],
             "Message": env_status[2]
        }
        return call_back
    else:
        return env_status


@app.post("/df_qa")
async def dialogue_qa(struct_iterator: QADict):
    db_switch = struct_iterator.customParameters['db_switch']
    if isinstance(db_switch, dict) and isinstance(db_switch['db_switch_enable'], bool) and not db_switch['db_switch_enable']:
        print('db_switch参数:\n{}'.format(db_switch))
        db_dict = {
            'db_ip': 'localhost',
            'db_port': '3306',
            'db_user': 'root',
            'db_password': '123456',
            'db_name': 'DialogFlow_DB',
            'table_name': 'qa_exec_record',
        }
        db_switch = db_dict
    else:
        db_dict = db_switch
    struct_iterator.customParameters['db_dict'] = db_dict
    env_status = df_qa(ginger_dict=struct_iterator.dict())
    if env_status and len(env_status) == 3:
        call_back = {
            "Status": env_status[0],
            "Execution_structure": env_status[1],
             "Message": env_status[2]
        }
        return call_back
    else:
        return env_status


@app.post("/return_boss_record")
async def db_to_web(struct_iterator: WebDict):

    db_switch = struct_iterator.customParameters['db_switch']
    if isinstance(db_switch, dict) and isinstance(db_switch['db_switch_enable'], bool) and not db_switch['db_switch_enable']:
        print('db_switch参数:\n{}'.format(db_switch))
        db_dict = {
            'db_ip': '10.155.2.4',
            'db_port': '30065',
            'db_user': 'root',
            'db_password': '123456',
            'db_name': 'BOSS_DB',
            'table_name': 'boss_exec_record',
        }
        db_switch = db_dict
    else:
        db_dict = db_switch
    struct_iterator.customParameters['db_dict'] = db_dict
    env_status = universal_to_web(ginger_dict=struct_iterator.dict())
    if env_status and len(env_status) == 3:
        call_back = {
            "Status": env_status[0],
            "Execution_structure": env_status[1],
             "Message": env_status[2]
        }
        return call_back
    else:
        return env_status


@app.post("/df_batch_delete_intents")
async def batch_deletion(struct_iterator: DFDict):
    db_switch = struct_iterator.customParameters['db_switch']
    if isinstance(db_switch, dict) and isinstance(db_switch['db_switch_enable'], bool) and not db_switch['db_switch_enable']:
        print('db_switch参数:\n{}'.format(db_switch))
        db_dict = {
            'db_ip': 'localhost',
            'db_port': '3306',
            'db_user': 'root',
            'db_password': '123456',
            'db_name': 'DialogFlow_DB',
            'table_name': 'qa_exec_record',
        }
        db_switch = db_dict
    else:
        db_dict = db_switch
    struct_iterator.customParameters['db_dict'] = db_dict
    env_status = batch_delete_intents(ginger_dict=struct_iterator.dict())
    if env_status and len(env_status) == 3:
        call_back = {
            "Status": env_status[0],
            "Execution_structure": env_status[1],
             "Message": env_status[2]
        }
        return call_back
    else:
        return env_status


@app.post("/build_dialogflow_qa_form")
async def bulk_import_qa_form(project_id: str='fbtest-tfxodj',intent_name_prefix: str='intent_name_',request_frequency: int=3,language_code: str='vi', excel_qa_file: UploadFile = File(...), service_account_key: UploadFile = File(...), db_switch: str={
        'db_ip': 'localhost',
        'db_port': '3306',
        'db_user': 'root',
        'db_password': '123456',
        'db_name': 'DialogFlow_DB',
        'table_name': 'dialogflow_exec_record',
        'db_switch_enable': True,
    },):
    db_switch = json.loads(db_switch)
    if isinstance(db_switch, str) and isinstance(db_switch['db_switch_enable'], bool) and not db_switch['db_switch_enable']:
        print('db_switch参数:\n{}'.format(db_switch))
        db_dict = {
            'db_ip': 'localhost',
            'db_port': '3306',
            'db_user': 'root',
            'db_password': '123456',
            'db_name': 'DialogFlow_DB',
            'table_name': 'dialogflow_exec_record',
        }
        db_switch = db_dict
    else:
        db_dict = db_switch
    start = time.time()
    try:
        excel_qa_res = await excel_qa_file.read()
        excel_qa_path = os.getcwd() + os.sep + 'data' + os.sep + 'qa_data' + os.sep
        excel_qa_name = 'Contents_of_ASEAN_Expo_Knowledge_Base.xlsx'
        excel_qa_path_full = os.path.join(excel_qa_path, excel_qa_name)
        excel_qa_path_full_origin = os.path.join(excel_qa_path, excel_qa_file.filename)
        with open(excel_qa_path_full, "wb") as f:
            f.write(excel_qa_res)
            print({"message": "success", 'time': time.time() - start, 'filename': excel_qa_name})
            print('表格上传的执行文件文件路径是:\n{}'.format(excel_qa_path_full))
        with open(excel_qa_path_full_origin, "wb") as f:
            f.write(excel_qa_res)
            print({"message": "success", 'time': time.time() - start, 'filename': excel_qa_file.filename})
            print('表格上传的文件原始文件路径是:\n{}'.format(excel_qa_path_full_origin))
    except Exception as e:
        print({"message": str(e), 'time': time.time() - start, 'filename': excel_qa_file.filename})

    try:
        service_account_key_res = await service_account_key.read()
        key_path = os.getcwd() + os.sep + 'data' + os.sep + 'qa_data' + os.sep
        #service_account_name = 'fbtest-tfxodj-2603bf40e440.json'
        service_account_name = 'fujian-52e4bf0f23e0.json'
        key_path_full = os.path.join(key_path, service_account_name)
        key_path_full_origin = os.path.join(key_path, service_account_key.filename)
        with open(key_path_full, "wb") as f:
            f.write(service_account_key_res)
            print({"message": "success", 'time': time.time() - start, 'filename': service_account_name})
            print('dialogflow密钥上传的执行文件路径是:\n{}'.format(key_path_full))
        with open(key_path_full_origin, "wb") as f:
            f.write(service_account_key_res)
            print({"message": "success", 'time': time.time() - start, 'filename': service_account_key.filename})
            print('dialogflow密钥上传的原始文件路径是:\n{}'.format(key_path_full_origin))
    except Exception as e:
        print({"message": str(e), 'time': time.time() - start, 'filename': service_account_key.filename})

    df_iterator = dict()
    df_iterator['customParameters'] = {
        "dialogflow_config": {
            "request_frequency": 3,
            "intent_name_prefix": "Agent",
            "project_id": "fbtest-tfxodj",

        }
    }
    df_iterator['customParameters']['dialogflow_config']['request_frequency'] = request_frequency
    df_iterator['customParameters']['dialogflow_config']['intent_name_prefix'] = intent_name_prefix
    df_iterator['customParameters']['dialogflow_config']['project_id'] = project_id
    df_iterator['customParameters']['dialogflow_config']['language_code'] = language_code
    print(df_iterator['customParameters'])
    df_iterator['customParameters']['db_dict'] = db_dict
    env_status = dialogflow_qa(ginger_dict=df_iterator)
    if env_status and len(env_status) == 3:
        call_back = {
            "Status": env_status[0],
            "Execution_structure": env_status[1],
             "Message": env_status[2]
        }
        return call_back
    else:
        return env_status


@app.get("/kill_task")
async def kill_pid():
    env_status = stop_timer()
    return env_status


@app.get('/')
def index():
    return {'message': 'API service working！'}


def write_sql(table_name, target_dict):
    if all([isinstance(target_dict, type({}.items())), isinstance(table_name, str)]):
        engine = create_engine('mysql+pymysql://root:111111@172.16.13.119:3306/rdp_data')
        engine.execute('DROP TABLE if exists {}'.format(table_name))
        df_sql = pd.DataFrame(list(target_dict)).T
        column = df_sql.iloc[0]
        df_sql.columns = column
        df_sql = df_sql.drop(df_sql.index[0])
        print(df_sql)
        df_sql.to_sql(table_name, con=engine, if_exists='append', index=False)
        df_sql.to_sql(str(table_name) +'_Persistence', con=engine, if_exists='append', index=False)


def read_sql(table_name):
    if isinstance(table_name, str):
        print('当前查询的数据表是:\n{}'.format(table_name))
        engine = create_engine('mysql+pymysql://root:111111@172.16.13.119:3306/rdp_data')
        session_factory = sessionmaker(bind=engine)
        session = session_factory()
        objs = session.execute("SELECT * FROM {}".format(table_name))
        print('fetchone:\n{}'.format(objs.fetchone()))
        rdp_param = pd.read_sql_table(table_name=table_name, con=engine).to_dict()
        print('当前查询的参数是:\n{}'.format(rdp_param))
        return rdp_param

def get_encoding_type(file):
    with open(file, 'rb') as f:
        raw_data = f.read()
    return detect(raw_data)['encoding']


def root_path_parse(sheet_name='134', config_module_name='fit_config', deploy=False, path=""):
    # sheet_name = '221'
    print('当前入参是:\n{}\n{}\n{}\n{}'.format(sheet_name, deploy, path, config_module_name))
    sheet_name = sheet_name
    param_render = write_private_config(sheet_name, config_module_name)
    platform_os = platform.system()
    print('当前操作系统是:\n{}'.format(platform_os))
    print(platform_os in ['Darwin', 'Linux'])
    if isinstance(param_render, tuple) and len(param_render) == 2 and not deploy:
        project_path = os.path.abspath(os.path.join(os.getcwd()))
        print('当前项目根目录绝对路径地址:\n{}'.format(project_path))
        if config_module_name =='fit_config':
            print('当前项目配置文件绝对路径地址:\n{}'.format(os.path.join(project_path, config_module_name)))
        elif config_module_name !='fit_config':
            print('当前项目配置文件绝对路径地址:\n{}'.format(os.path.join(project_path, config_module_name)))
        if len(config_module_name) ==0:
            config_module_name = 'fit_config'
        render_robot = 'config' + os.sep + config_module_name + os.sep + param_render[0].split('"')[1]
        render_run_robot = 'config' + os.sep + config_module_name + os.sep + param_render[1].split('"')[1]
        conf_path_robot = os.path.join(project_path, render_robot)
        conf_path_run_robot = os.path.join(project_path, render_run_robot)
        print('当前执行的Debug解析配置文件是:\n{}\n\nCI地址是:\n{}'.format(conf_path_robot, conf_path_run_robot))
        encoding_type_robot = get_encoding_type(conf_path_robot)
        encoding_type_run_robot = get_encoding_type(conf_path_run_robot)
        if os.path.exists(conf_path_robot):
            ct = ConfigFactory.parse_file(conf_path_robot, encoding=encoding_type_robot)
            ConfigTree.put(ct, "root_dir", project_path)
            ConfigTree.put(ct, "python_path", project_path)
            ConfigTree.put(ct, "data_dir", project_path + os.sep + 'data')
            ConfigTree.put(ct, 'project_dir', project_path + os.sep + 'proj-auto-test')
            ConfigTree.put(ct, 'log_dir', project_path + os.sep + 'proj-auto-test' + os.sep + 'logs')
            ConfigTree.put(ct, 'output_dir', project_path + os.sep + 'proj-auto-test' + os.sep + 'outputs')
            print('Debug写入磁盘为 {}'.format(conf_path_robot))
            with open(conf_path_robot, "w", encoding=encoding_type_robot) as conf_robot:
                conf_robot.write(HOCONConverter.to_hocon(ct))
                print('\n{}\n\nconf_path_robot 写入成功\n{}'.format(deploy, conf_path_robot))

        if os.path.exists(conf_path_run_robot):
            ci = ConfigFactory.parse_file(conf_path_run_robot, encoding=encoding_type_run_robot)
            ConfigTree.put(ci, "root_dir", project_path)
            ConfigTree.put(ci, "python_path", project_path)
            ConfigTree.put(ci, "data_dir", project_path + os.sep + 'data')
            ConfigTree.put(ci, 'project_dir', project_path + os.sep + 'proj-auto-test')
            ConfigTree.put(ci, 'log_dir', project_path + os.sep + 'proj-auto-test' + os.sep + 'logs')
            ConfigTree.put(ci, 'output_dir', project_path + os.sep + 'proj-auto-test' + os.sep + 'outputs')
            print('CI写入磁盘为 {}'.format(conf_path_robot))
            with open(conf_path_run_robot, "w", encoding=encoding_type_run_robot) as conf_run_robot:
                conf_run_robot.write(HOCONConverter.to_hocon(ci))
                print('\n{}\n\nconf_path_run_robot 写入成功\n{}'.format(deploy, conf_path_run_robot))

    if deploy and path:
        project_path = os.path.abspath(os.path.join(os.getcwd()))
        print('当前项目根目录绝对路径地址:\n{}'.format(project_path))
        project_path = project_path
        render_robot = 'config' + os.sep + 'fit_config' + os.sep + param_render[0].split('"')[1]
        render_run_robot = 'config' + os.sep + 'fit_config' + os.sep + param_render[1].split('"')[1]
        conf_path_robot = os.path.join(project_path, render_robot)
        conf_path_run_robot = os.path.join(project_path, render_run_robot)
        encoding_type_robot = get_encoding_type(conf_path_robot)
        encoding_type_run_robot = get_encoding_type(conf_path_run_robot)
        print('当前执行的解析配置文件是:\n{}\n\nCI地址是:\n{}'.format(conf_path_robot, conf_path_run_robot))
        if str(path).__contains__('='):
            project_path = path.split("=")[1].replace('\\', '/')
            data_dir = str(project_path + os.sep + 'data').replace('\\', '/')
            project_dir = str(project_path + os.sep + 'proj-auto-test').replace('\\', '/')
            log_dir = str(project_path + os.sep + 'proj-auto-test' + os.sep + 'logs').replace('\\', '/')
            output_dir = str(project_path + os.sep + 'proj-auto-test' + os.sep + 'outputs').replace('\\', '/')
        if os.path.exists(conf_path_robot):
            ct = ConfigFactory.parse_file(conf_path_robot, encoding=encoding_type_robot)
            ConfigTree.put(ct, "root_dir", project_path)
            ConfigTree.put(ct, "python_path", project_path)
            ConfigTree.put(ct, "data_dir", data_dir)
            ConfigTree.put(ct, 'project_dir', project_dir)
            ConfigTree.put(ct, 'log_dir', log_dir)
            ConfigTree.put(ct, 'output_dir', output_dir)
            print('写入磁盘为 {}'.format(conf_path_robot))
            with open(conf_path_robot, "w", encoding=encoding_type_robot) as conf_robot:
                conf_robot.write(HOCONConverter.to_hocon(ct))
                print('\n\nconf_path_robot 写入成功\n{}'.format(conf_path_robot))

        if os.path.exists(conf_path_run_robot):
            ci = ConfigFactory.parse_file(conf_path_run_robot, encoding=encoding_type_run_robot)
            ConfigTree.put(ci, "root_dir", project_path)
            ConfigTree.put(ci, "python_path", project_path)
            ConfigTree.put(ci, "data_dir", data_dir)
            ConfigTree.put(ci, 'project_dir', project_dir)
            ConfigTree.put(ci, 'log_dir', log_dir)
            ConfigTree.put(ci, 'output_dir', output_dir)
            print('写入磁盘为 {}'.format(conf_path_robot))
            with open(conf_path_run_robot, "w", encoding=encoding_type_run_robot) as conf_run_robot:
                conf_run_robot.write(HOCONConverter.to_hocon(ci))
                print('\n\nconf_path_run_robot 写入成功\n{}'.format(conf_path_run_robot))


def write_private_config(env_name, config_module_name='fit_config'):
    project_path = os.path.abspath(os.path.join(os.getcwd()))
    private_ct_path = project_path + os.sep + 'config' + os.sep + config_module_name + os.sep + 'private.conf'
    private_ci_path = project_path + os.sep + 'config' + os.sep + config_module_name + os.sep + 'run_robot_private.conf'
    private_harix_path = project_path + os.sep + 'config' + os.sep + 'test_harix' + os.sep + 'private.conf'
    robot_path = project_path + os.sep + 'config' + os.sep + 'robot.conf'
    run_robot_path = project_path + os.sep + 'config' + os.sep + 'run_robot.conf'
    # encoding_ci_path = get_encoding_type(private_ci_path)
    # encoding_ct_path = get_encoding_type(private_ct_path)
    print('当前项目根目录绝对路径地址:\n{}\nprivate文件地址是:/n{}'.format(project_path, private_ct_path))
    env_ct = {
        "221": 'include "robot_221.conf"',
        "231": 'include "robot_231.conf"',
        "251": 'include "robot_251.conf"',
        "134": 'include "robot_134.conf"',
        "138": 'include "robot_138.conf"',
        "136": 'include "robot_136.conf"',
        "85": 'include "robot_85.conf"',
        "86": 'include "robot_86.conf"',
        "87": 'include "robot_87.conf"',
        "61": 'include "robot_61.conf"'
    }
    env_harix = {
        "221": 'include "../env_config/robot_221.conf" log_handlers = ["file_handler", "console"]',
        "231": 'include "../env_config/robot_231.conf" log_handlers = ["file_handler", "console"]',
        "251": 'include "../env_config/robot_251.conf" log_handlers = ["file_handler", "console"]',
        "134": 'include "../env_config/robot_134.conf" log_handlers = ["file_handler", "console"]',
        "138": 'include "../env_config/robot_138.conf" log_handlers = ["file_handler", "console"]',
        "136": 'include "../env_config/robot_136.conf" log_handlers = ["file_handler", "console"]',
        "85": 'include "../env_config/robot_85.conf" log_handlers = ["file_handler", "console"]',
        "86": 'include "../env_config/robot_86.conf" log_handlers = ["file_handler", "console"]',
        "87": 'include "../env_config/robot_87.conf" log_handlers = ["file_handler", "console"]',
        "61": 'include "../env_config/robot_61.conf" log_handlers = ["file_handler", "console"]'
    }
    env_ci = {
        "221": 'include "run_robot_221.conf"',
        "231": 'include "run_robot_231.conf"',
        "251": 'include "run_robot_251.conf"',
        "134": 'include "run_robot_134.conf"',
        "138": 'include "run_robot_138.conf"',
        "136": 'include "run_robot_136.conf"',
        "85": 'include "run_robot_85.conf"',
        "86": 'include "run_robot_86.conf"',
        "87": 'include "run_robot_87.conf"',
        "61": 'include "run_robot_61.conf"'
    }
    env_robot = {
        "221": 'include "{}/private.conf"'.format(config_module_name),
        "231": 'include "{}/private.conf"'.format(config_module_name),
        "251": 'include "{}/private.conf"'.format(config_module_name),
        "134": 'include "{}/private.conf"'.format(config_module_name),
        "138": 'include "{}/private.conf"'.format(config_module_name),
        "136": 'include "{}/private.conf"'.format(config_module_name),
        "85": 'include "{}/private.conf"'.format(config_module_name),
        "86": 'include "{}/private.conf"'.format(config_module_name),
        "87": 'include "{}/private.conf"'.format(config_module_name),
        "61": 'include "{}/private.conf"'.format(config_module_name),
    }
    env_run_robot = {
        "221": 'include "{}/run_robot_private.conf"'.format(config_module_name),
        "231": 'include "{}/run_robot_private.conf"'.format(config_module_name),
        "251": 'include "{}/run_robot_private.conf"'.format(config_module_name),
        "134": 'include "{}/run_robot_private.conf"'.format(config_module_name),
        "138": 'include "{}/run_robot_private.conf"'.format(config_module_name),
        "136": 'include "{}/run_robot_private.conf"'.format(config_module_name),
        "85": 'include "{}/run_robot_private.conf"'.format(config_module_name),
        "86": 'include "{}/run_robot_private.conf"'.format(config_module_name),
        "87": 'include "{}/run_robot_private.conf"'.format(config_module_name),
        "61": 'include "{}/run_robot_private.conf"'.format(config_module_name),
    }
    env_harix_param = env_harix[str(env_name)]
    env_ct_param = env_ct[str(env_name)]
    env_ci_param = env_ci[str(env_name)]
    env_robot_param = env_robot[str(env_name)]
    env_run_robot_param = env_run_robot[str(env_name)]
    if isinstance(env_ct_param, str):
        ct = open(private_ct_path, "w")
        print('写入的private.conf文件为: {}'.format(ct.name))
        ct.write(env_ct_param)
        ct.close()
    if isinstance(env_harix_param, str):
        ct = open(private_harix_path, "w")
        print('写入的test_harix private.conf文件为: {}'.format(ct.name))
        ct.write(env_harix_param)
        ct.close()
    if os.path.exists(robot_path):
        encoding_robot = get_encoding_type(robot_path)
        with open(robot_path, encoding=encoding_robot, mode="r") as f:
            robot_file = f.read()
            if robot_file.__contains__('config/private.conf'):
                print('The current 【robot.conf】configuration already exists:\n{}'.format(env_robot_param))
            else:
                with open(robot_path, encoding=encoding_robot, mode="a") as f_robot:
                    f_robot.write(env_robot_param)
                    print(f'successfully appended: {env_robot_param}')
    if os.path.exists(run_robot_path):
        encoding_run_robot = get_encoding_type(run_robot_path)
        with open(run_robot_path, encoding=encoding_run_robot, mode="r") as f:
            run_robot_file = f.read()
            if run_robot_file.__contains__('config/run_robot_private.conf'):
                print('The current 【run_robot.conf】configuration already exists:\n{}'.format(env_run_robot_param))
            else:
                with open(run_robot_path, encoding=encoding_run_robot, mode="a") as f_run_robot:
                    f_run_robot.write(env_run_robot_param)
                    print(f'successfully appended: {env_run_robot_param}')
    if isinstance(env_ci_param, str):
        ci = open(private_ci_path, "w")
        print('写入的run_robot_private.conf文件为: {}'.format(ci.name))
        ci.write(env_ci_param)
        ci.close()
    return env_ct_param, env_ci_param


def trim_columns(df):
    trim = lambda x: x.strip() if isinstance(x, str) else x
    return df.applymap(trim)


def task_keepalive(timeout):
    from datetime import datetime, timedelta
    global job_start_time
    while True:
        start_time = job_start_time

        if not start_time:
            time.sleep(30)
            continue
        quit_time = start_time + timedelta(seconds=timeout)
        if datetime.now() > quit_time:
            logging.info("task_keepalive: quit as timeout, start_time %s, timeout %s"
                         % (start_time, timeout))
            os._exit(-1)
        time.sleep(30)

def data_init(db_dict):
    log_prefix = "data_init:\n{}".format(json.dumps(db_dict))
    print(log_prefix)
    if isinstance(db_dict, dict) and db_dict.keys() >= {'db_ip', 'db_port', 'db_user', 'db_password', 'db_name'}:
        engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(db_dict['db_user'], db_dict['db_password'],
                                                    db_dict['db_ip'], db_dict['db_port'],db_dict['db_name']))
        print('当前系统的连接串:\n{}\n{}'.format(engine, db_dict))
        return engine
    else:
        print('当前系统的连接串不满足参数要求')


def robot_lite_record(param):
    log_prefix = "Enter to robot_lite_record with {}".format(param)
    url = '/result_lite_container'
    db_dict = {
        'db_ip': '172.16.23.85',
        'db_port': '30065',
        'db_user': 'sit',
        'db_password': '123456',
        'db_name': 'Lite_DB',
    }
    engine = data_init(db_dict)
    sql_str = "SELECT * FROM mybatis_mng.RouterGateway WHERE api_service = 'result_lite_container'"
    db_all_table = pd.read_sql_query(sql_str, con=engine)
    print(db_all_table.values.tolist())
    ip_port = db_all_table.values.tolist()[0][1]
    host = 'http://' + str(ip_port)
    record_body = {
                  "customParameters": {
                    "execution_env": "134",
                    "robot_device_code": "GINLITXR-1LXXXXXXXXXGNL10S2121000087",
                    "target_map_name": "上海工厂图书馆",
                    "return_map_name": "上海工厂图书馆",
                    "target_map_location_name": "普通外借",
                    "return_map_location_name": "办证处",
                    "exec_date": "2021-07-24 16:54:42",
                    "exec_param": "{\"code\":0,\"message\":\"success\",\"data\":null,\"uid\":null}",
                    "exec_task_timer": "* * 3/5 ? * 1/1 *"
                  }
                }
    record_body['customParameters']['return_map_location_name'] = param[2]['ginger_dict']['return_map_location_name']
    record_body['customParameters']['target_map_location_name'] = param[2]['ginger_dict']['target_map_location_name']
    record_body['customParameters']['target_map_name'] = param[2]['ginger_dict']['target_map_name']
    record_body['customParameters']['return_map_name'] = param[2]['ginger_dict']['return_map_name']
    record_body['customParameters']['exec_param'] = param[2]['start_task_log']
    record_body['customParameters']['exec_task_timer'] = param[2]['ginger_dict']['exec_task_timer']
    record_body['customParameters']['exec_callback'] = json.dumps(param[2])
    record_body['customParameters']['robot_device_code'] = param[2]['ginger_dict']['robot_device_code']
    import datetime
    record_body['customParameters']['exec_date'] = str(datetime.datetime.now())
    record_body['customParameters']['exec_agent'] = host
    record_body['customParameters']['exec_device_flag'] = param[2]['ginger_dict']['exec_device_flag']
    if 'param_task' in str(param):
        record_body['customParameters']['param_task'] = json.dumps(json.loads(param[2]['ginger_dict']['charging_pile_info'])['param_task'])
    if 'charging_pile_info' in param[2]['ginger_dict']:
        record_body['customParameters']['charging_pile_info'] = param[2]['ginger_dict']['charging_pile_info']
    elif 'charging_pile_name' in param[2]['ginger_dict']:
        record_body['customParameters']['charging_pile_info'] = param[2]['ginger_dict']['charging_pile_name']
    r = requests.post(host + url, json=record_body, verify=False)
    if 'Status' in r.text and r.json()['Status'] == 'Success':
        print('{}\nresult_lite_container 执行记录入库数据库成功\n{}'.format(log_prefix, param))
    else:
        print('{}\nresult_lite_container 执行记录入库数据库失败\n{}'.format(log_prefix, param))


def build_robot_config(ginger_dict=conf_dict):
    import os
    if isinstance(ginger_dict, dict) and 'customParameters' in ginger_dict:
        print('==========================接口调用模式==================================')
        ginger_dict = ginger_dict['customParameters']
    else:
        print('==========================命令行CI调用模式==================================')
        ginger_dict = {
            "customParameters": {
                "项目名称": "Marketing",
                "BugID在索引_的第几个位置": 0,
                "生成的配置文件夹目录": "cases/sit_test/crs_test/cross_marketing_order",
                "j2配置文件夹目录": "data/templates/crs_test/cross_marketing_order",
                "是否覆盖原有配置文件(false/true)": False
            }
        }
        ginger_dict = ginger_dict['customParameters']
    project_path = os.path.abspath(os.path.join(os.getcwd()))
    print('当前项目根目录绝对路径地址:\n{}'.format(project_path))
    print('=====================================End==================================')
    template_iterator = '/cases/sit_test/template_iterator.robot'
    template_path = project_path + template_iterator
    conf_param_list = dict()
    project_name = ginger_dict['项目名称'] if '项目名称' in ginger_dict else None
    robot_generation_folder = ginger_dict['生成的配置文件夹目录'] if '生成的配置文件夹目录' in ginger_dict else None
    j2_source_folder = ginger_dict['j2配置文件夹目录'] if 'j2配置文件夹目录' in ginger_dict else None
    slice_index = ginger_dict['BugID在索引_的第几个位置'] if 'BugID在索引_的第几个位置' in ginger_dict else None
    conf_folder_name = j2_source_folder.rsplit("/", 1)[1]
    override_flag = ginger_dict['是否覆盖原有配置文件(false/true)'] if '是否覆盖原有配置文件(false/true)' in ginger_dict else False
    # robot_generation_folder = os.path.join(robot_generation_folder, conf_folder_name)
    path_list = []
    if os.path.exists(project_path) and robot_generation_folder and j2_source_folder and os.path.exists(template_path):
        robot_generation_folder_path = os.path.join(project_path, robot_generation_folder)
        if not os.path.exists(robot_generation_folder_path):
            os.makedirs(robot_generation_folder_path, exist_ok=True)
        j2_source_folder_path = os.path.join(project_path, j2_source_folder)
        path_list.append(robot_generation_folder_path)
        path_list.append(j2_source_folder_path)
        conf_param_list['conf_path'] = {'配置文件夹目录路径': path_list}
        print(conf_param_list)
        files_all = []
        files_dict = dict()
        bug_id_list = []
        j2_file_list = os.listdir(j2_source_folder_path)
        robot_file_target = os.path.join(project_path, ginger_dict['生成的配置文件夹目录'])
        robot_file_list = os.listdir(robot_file_target)
        # 遍历输出每一个文件的名字和类型
        original_robot_file_target = robot_file_list
        counter = 0
        all_final_robot_path = []
        override_flag_false_robot_path = []
        override_flag_false_j2_path = []
        all_final_j2_path = []
        exist_robot_file = []
        new_robot_file = []
        if override_flag:
            shutil.rmtree(robot_file_target)
            os.mkdir(robot_file_target)
        for iterator in j2_file_list:
            # 输出指定后缀类型的文件
            invalid_flag_dict = dict()
            if (iterator.endswith('.j2')):
                print('当前的j2文件\n', iterator)
                print('当前的BugID索引位置是: {}'.format(slice_index))
                bug_id = iterator.rsplit("_", maxsplit=50)[int(slice_index)]
                bug_id_list.append(iterator.rsplit("_", maxsplit=50)[int(slice_index)])
                files_all.append(iterator)
                files_dict["bug_id"] = bug_id
                files_dict["robot_file_path"] = j2_source_folder
                j2_full_path = os.path.join(j2_source_folder_path, iterator)
                encoding_type_j2 = get_encoding_type(j2_full_path)
                encoding_type_template = get_encoding_type(template_path)
                j2_lines = open(j2_full_path, encoding=encoding_type_j2)

                def load_json(path):
                    print('\npath:\n{}'.format(path))
                    import json
                    lines = []
                    with open(path, encoding=encoding_type_j2) as f:
                        for row in f.readlines():
                            #print(row)  # 第二步：读取文件内容
                            return_list = ['}},', '%},','{%','"{%', '{#']
                            contain_list = list(filter(lambda x: row.strip().__contains__(x), return_list))
                            if contain_list and len(contain_list) is not None:
                            # if row.strip().__contains__("}},"):  # 第三步：对每一行进行过滤
                                print('当前需要去除的标记位是:\n{}'.format(row))
                                invalid_flag_dict[bug_id] = [path, row]
                                print('入库标记位是:\n{}'.format(invalid_flag_dict))
                                continue
                            lines.append(row)
                    return json.loads("\n".join(lines))
                spec_j2 = load_json(j2_full_path)
                j2_lines = j2_lines.readlines()
                tmp_rf = open(template_path, encoding=encoding_type_template)
                lines = tmp_rf.readlines()
                lines[3] = lines[3].replace('Project', project_name)
                lines[8] = lines[8].replace('BugID', bug_id).replace('BugTitle', str(spec_j2['params']['step_description'][1]).strip())
                lines[9] = lines[9].replace('Module_folder', os.path.join(os.path.join(j2_source_folder.rsplit("/", maxsplit=50)[2], conf_folder_name), iterator).replace('\\','/'))
                robot_file_target = os.path.join(project_path, ginger_dict['生成的配置文件夹目录'])
                final_name = '000{}__{}'.format(j2_file_list.index(iterator), iterator.replace('.json.j2', '.robot'))
                j2_file_namespace = iterator.replace('.json.j2', '.robot')
                final_name_path = os.path.join(robot_file_target, final_name)
                if not override_flag:
                    print('skip操作 当前覆盖变量是:\n{}\n'.format(final_name))
                    exist_robot_file.append(final_name)
                if not j2_file_namespace in str(robot_file_list) and not override_flag:
                    robot_file_list = os.listdir(robot_file_target)
                    if len(robot_file_list)!=0 and str(robot_file_list[-1]).__contains__('__'):
                        if '__init__.robot' in robot_file_list:
                            robot_file_list.pop(robot_file_list.index('__init__.robot'))
                        cal_num_list = []
                        for calc in robot_file_list:
                            if calc.endswith('.robot'):
                                print('切割对象:\n{}'.format(calc))
                                cal_num = int(str(calc).rsplit('__', maxsplit=50)[0])
                                cal_num_list.append(cal_num)
                        max_num = max(cal_num_list)
                        j2_file_namespace = j2_file_namespace.replace('.j2', '.robot')
                        final_name_path = os.path.join(robot_file_target, '000{}__{}'.format(max_num + 1, j2_file_namespace))
                    with open(final_name_path, 'w', encoding=encoding_type_j2) as f:
                        override_flag_false_robot_path.append(final_name_path)
                        override_flag_false_j2_path.append(j2_full_path)
                        print('执行新建操作 当前配置文件是:\n{}'.format(final_name))
                        new_robot_file.append(final_name)
                        f.writelines(lines)
                if override_flag:
                    with open(final_name_path, 'w', encoding=encoding_type_j2) as f:
                        all_final_robot_path.append(final_name_path)
                        all_final_j2_path.append(j2_full_path)
                        print('执行新建操作 当前配置文件是:\n{}'.format(final_name))
                        f.writelines(lines)
                tmp_rf.close()
                counter = counter + 1
                print(final_name_path, counter)

        conf_param_list['new_robot_file'] = {'不在已有列表全新生成的robot配置文件列表': new_robot_file}
        conf_param_list['override_flag_false_robot_path'] = {'.robot 未覆盖全新生成的robot配置文件列表': override_flag_false_robot_path}
        conf_param_list['override_flag_false_j2_path'] = {'.j2 未覆盖全新生成的j2配置文件列表': override_flag_false_j2_path}

        conf_param_list['robot_path'] = {'.robot 覆盖全新生成的robot配置文件列表': all_final_robot_path}
        conf_param_list['j2_path'] = {'.j2 覆盖全新生成的j2配置文件列表': all_final_j2_path}

        conf_param_list['all_final_robot_path'] = {'覆盖生成的robot配置文件列表': all_final_robot_path}
        conf_param_list['exist_robot_file'] = {'已经存在的robot配置文件列表': exist_robot_file}
        conf_param_list['original_robot_file_target'] = {'原始robot配置文件列表': original_robot_file_target}

        print(files_all,'\n',bug_id_list,'\n',files_dict)

        return 'Success', conf_param_list
    else:
        return_msg = '入参条件不符合预期: project_path\n{}\nrobot_generation_folder\n{}\nj2_source_folder\n{}\ntemplate_path\n{}'.format(project_path,robot_generation_folder,j2_source_folder,template_path)
        print(return_msg)
        return return_msg


def bulk_query(ginger_dict=SQL_j2_Dict):
    log_prefix = "bulk_query:"
    print('通用数据库渲染 数据库中增删改查接口: {}'.format(log_prefix))
    try:
        import os
        project_path = os.path.abspath(os.path.join(os.getcwd()))
        os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
        conf_param_list = dict()
        db_dict = ginger_dict['customParameters']['db_dict'] if 'db_dict' in ginger_dict['customParameters'] else None
        if isinstance(db_dict, dict) and db_dict.keys() >= {'db_ip', 'db_port', 'db_user', 'db_password', 'db_name'}:
            engine = create_engine(
                'mysql+pymysql://{}:{}@{}:{}/{}'.format(db_dict['db_user'], db_dict['db_password'], db_dict['db_ip'],
                                                        db_dict['db_port'], db_dict['db_name']))
            print('当前系统的连接串:\n{}'.format(engine, db_dict))
        else:
            print('当前系统的连接串不满足参数要求')
        ginger_dict = ginger_dict['customParameters']
        table_name = db_dict['table_name']
        if isinstance(table_name, str) and engine:
            try:
                db_query_results = pd.read_sql_table(table_name=table_name, con=engine)
                j2_file_name_list = ginger_dict['j2_config']['j2_full_name']
                print(j2_file_name_list)
                qs = db_query_results.query("j2_full_name in @j2_file_name_list")
                print(qs)
                json_qs = qs.to_json(orient="records", force_ascii=False)
                print('json_qs:\n{}'.format(json_qs))
                dict_qs = qs.to_dict()
                print('dict_qs:\n{}'.format(dict_qs))
                print('##############db_query_sort#################')
                project_root_path = os.path.join(project_path, 'data/boss_data')
                path_excel = os.path.join(project_root_path, 'universal_to_web.xlsx')
                temp_excel = pd.ExcelWriter(path_excel)
                db_query_results.to_excel(temp_excel)
                temp_excel.save()
                db_query_excel = pd.read_excel(path_excel)
                if 'Unnamed: 0' in db_query_excel:
                    db_query_excel.pop('Unnamed: 0')
                db_query_excel = db_query_excel.reindex(index=db_query_excel.index[::-1])
                records_json = db_query_excel.to_json(orient="records", force_ascii=False)
                print('##############format_json#################')
                format_json = json.loads(records_json, encoding='utf8')
                print('##############format_json#################')
                conf_param_list['BossParameters'] = format_json
                env_status = ['Success', conf_param_list, '执行成功,回调信息\n{}'.format(json.dumps(ginger_dict, ensure_ascii=False))]
                return env_status
            except Exception as e:
                env_status = ['Failure', conf_param_list, '执行失败,当前表格内容不合法\n{}'.format(e)]
                return env_status

            return 'Success', format_json
        else:
            print('当前 数据结构不满足参数要求')
    except Exception as e:
        email_status = ['Failure', '日志入库失败,回调信息{}'.format(e)]
        return email_status


def build_robot_j2(ginger_dict=j2_dict):
    import os
    db_dict = ginger_dict['customParameters']['db_dict'] if 'db_dict' in ginger_dict['customParameters'] else None
    if isinstance(db_dict, dict) and db_dict.keys() >= {'db_ip', 'db_port', 'db_user', 'db_password', 'db_name'}:
        engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(db_dict['db_user'], db_dict['db_password'], db_dict['db_ip'], db_dict['db_port'], db_dict['db_name']))
        print('当前系统的连接串:\n{}'.format(engine, db_dict))
    else:
        print('当前系统的连接串不满足参数要求')

    if isinstance(ginger_dict, dict) and 'customParameters' in ginger_dict:
        print('==========================接口调用模式==================================')
    else:
        print('==========================命令行CI调用模式==================================')
        ginger_dict = {
            "customParameters": {
                "项目名称": "Vending",
                "BugID在索引_的第几个位置": 0,
                "生成的配置文件夹目录": "cases/sit_test/j2_sql",
                "j2配置文件夹目录": "data/templates/j2_sql"
            }
        }
        ginger_dict = ginger_dict['customParameters']
    project_path = os.path.abspath(os.path.join(os.getcwd()))
    print('当前项目根目录绝对路径地址:\n{}'.format(project_path))
    print('=====================================End==================================')
    template_iterator = '/cases/sit_test/template_sql.j2'
    template_path = project_path + template_iterator
    if os.path.exists(project_path) and os.path.exists(template_path):
        try:
            ginger_dict = ginger_dict['customParameters']['j2_config']
            conf_param_list = dict()
            project_name = ginger_dict['项目名称'] if '项目名称' in ginger_dict else None
            robot_generation_folder = ginger_dict['生成的配置文件夹目录'] if '生成的配置文件夹目录' in ginger_dict else None
            j2_source_folder = ginger_dict['j2配置文件夹目录'] if 'j2配置文件夹目录' in ginger_dict else None
            slice_index = ginger_dict['BugID在索引_的第几个位置'] if 'BugID在索引_的第几个位置' in ginger_dict else None
            conf_folder_name = j2_source_folder.rsplit("/", 1)[1]
            path_list = []
            if os.path.exists(project_path) and robot_generation_folder and j2_source_folder and os.path.exists(template_path):
                robot_generation_folder_path = os.path.join(project_path, robot_generation_folder)
                if not os.path.exists(robot_generation_folder_path):
                    os.makedirs(robot_generation_folder_path, exist_ok=True)
                j2_source_folder_path = os.path.join(project_path, j2_source_folder)
                path_list.append(robot_generation_folder_path)
                path_list.append(j2_source_folder_path)
                conf_param_list['conf_path'] = {'配置文件夹目录路径': path_list}
                print(conf_param_list)
                files_all = []
                files_dict = dict()
                bug_id_list = []
                j2_file_list = os.listdir(j2_source_folder_path)
                # 遍历输出每一个文件的名字和类型
                all_final_robot_path = []
                all_final_j2_path = []
                combine_flag_list = []
                bug_id_list = []
                params_list = []
                datas_list = []
                invalid_flag_list = []
                valid_flag_list = []
                pop_flag_list = []
                replace_flag_list = []
                counter = 0
                for iterator in j2_file_list:
                    # 输出指定后缀类型的文件
                    invalid_flag_dict = dict()
                    pop_flag_dict = dict()
                    replace_flag_dict = dict()
                    valid_flag_dict = dict()
                    if (iterator.endswith('.j2')):
                        counter = counter + 1
                        print('=====================start 【{}】==========================='.format(counter))
                        print('当前的j2文件\n', iterator)
                        print('当前的BugID索引位置是: {}'.format(slice_index))
                        import json
                        def trim_columns(df):
                            trim = lambda x: x.strip() if isinstance(x, str) else x
                            return df.applymap(trim)
                        bug_id = iterator.rsplit("_", maxsplit=50)[int(slice_index)]
                        slice_0 = iterator.rsplit("_", maxsplit=50)[0]
                        # slice_2 = iterator.rsplit("_", maxsplit=50)[2]
                        combine_flag = str(bug_id + slice_0)
                        bug_id_list.append(iterator.rsplit("_", maxsplit=50)[int(slice_index)])
                        files_all.append(iterator)
                        files_dict["bug_id"] = bug_id
                        files_dict["robot_file_path"] = j2_source_folder
                        j2_full_path = os.path.join(j2_source_folder_path, iterator)
                        encoding_type_j2 = get_encoding_type(j2_full_path)
                        def load_json(path):
                            import json
                            print('\npath:\n{}'.format(path))
                            with open(path) as f_type:
                                file_content = f_type.read()
                                try:
                                    legal_json = json.loads(file_content)
                                    print(f'File format is legal:\n{legal_json}')
                                    result_dict = {
                                        'j2_file_abs_path': path,
                                        'valid_j2_file': legal_json
                                    }
                                    valid_flag_dict.update(
                                        {
                                            bug_id: result_dict
                                        }
                                    )
                                    if valid_flag_dict and valid_flag_dict != {}:
                                        valid_flag_list.append(valid_flag_dict)
                                    print(f'valid_flag_dict入库标记位是:\n{valid_flag_dict}')
                                    return legal_json
                                except:
                                    print(f'File format is unlegal:\n{file_content}')
                                    lines = []  # 第一步：定义一个列表， 打开文件
                                    # encoding_type_j2 = get_encoding_type(path)
                                    print('=====================start Loading===========================')
                                    with open(path) as f:
                                        print('=============【{}】==============='.format(path))
                                        for index_position, row in enumerate(f.readlines()):
                                            # pop_list = ['[{', '}}]','}]','"{{', 'tojson()']
                                            pop_list = ['[{', '}}]', '}]', 'tojson()', '{%','%}']
                                            contain_list = list(filter(lambda x: row.strip().__contains__(x), pop_list))
                                            print('origin【索引位置: {}】【include line】: {}\n【当前行】:{}',index_position, row, contain_list)# 第二步：读取文件内容
                                            if not (row.strip().startswith('"') and row.strip().endswith('"')) and not(row.strip().__contains__('[{') and (row.strip().startswith('"') or row.strip().endswith('},')) or row.strip().endswith('}]')) and (row.strip().startswith('"') and row.strip().endswith('},')):
                                                def replace_row(row):
                                                    replace_dict = {
                                                        'j2_file_abs_path': path,
                                                        'j2_file_origin_row': row,
                                                        'j2_file_replace_row': row.replace('{{', '"{{').replace('}}', '}}"'),
                                                        'j2_file_index_position': index_position,
                                                    }
                                                    replace_flag_dict.update(
                                                        {
                                                            bug_id + '_replace': replace_dict
                                                        }
                                                    )
                                                    if replace_flag_dict and replace_flag_dict != {}:
                                                        replace_flag_list.append(replace_flag_dict)
                                                    row = row.replace('{{', '"{{').replace('}}', '}}"')
                                                    print('replace_current_row:\n{}'.format(row))
                                                    return row

                                                if contain_list !=[] or row.strip().__contains__("}},") or row.strip().__contains__('tojson'):  # 第三步：对每一行进行过滤
                                                    print('当前需要去除的标记位是:\n{}'.format(row))
                                                    if row.strip().__contains__('tojson'):
                                                        print('当前需要去除的标记位是:\n{}\n{}'.format(row, index_position))
                                                        print('current_tojson_row:\n{}'.format(row))
                                                    result_dict = {
                                                        'j2_file_abs_path': path,
                                                        'j2_file_row': row,
                                                        'j2_file_index_position': index_position,
                                                    }
                                                    invalid_flag_dict.update(
                                                        {
                                                            bug_id: result_dict
                                                        }
                                                    )
                                                    print('入库标记位是:\n{}'.format(invalid_flag_dict))
                                                    if invalid_flag_dict and invalid_flag_dict != {}:
                                                        invalid_flag_list.append(invalid_flag_dict)
                                                    contain_list = ['{%', '%}', '({','})', '{"','"}']
                                                    in_list = list(filter(lambda x: row.strip().__contains__(x), contain_list))
                                                    if in_list and in_list !=[] and not row.strip().__contains__('%}",') or row.strip().__contains__('-%}",') and not row.strip().__contains__('"{%'):
                                                    # if row.strip().__contains__('{%') or row.strip().__contains__('%}'):
                                                        print('Start deleting/repalce the current line:\n{}'.format(row))
                                                        # row = row.replace('{%', '\u007b\u0025').replace('%}', '\u0025\u007d').replace('({','\u0028\u007b').replace('})','\u007d\u0029').replace('{"','\u007b\u0022').replace('"}','\u0022\u007d')
                                                        pop_dict = {
                                                            'j2_file_abs_path': path,
                                                            'j2_file_pop_row': row,
                                                            'j2_file_index_position': index_position,
                                                        }
                                                        pop_flag_dict.update(
                                                            {
                                                                bug_id + '_pop': pop_dict
                                                            }
                                                        )
                                                        if pop_flag_dict and pop_flag_dict != {}:
                                                            pop_flag_list.append(pop_flag_dict)
                                                        continue
                                                        # print('After deleting/repalce the current line:\n{}'.format(row))
                                                    else:
                                                        row = replace_row(row)
                                                        print(row)
                                                elif row.strip().__contains__('}}') and row.strip().__contains__('{{') and not (row.strip().__contains__('"{{') or row.strip().__contains__('}}"')) and not (row.strip().startswith('"') and row.strip().endswith('"')):
                                                    row = replace_row(row)
                                                    print(row)
                                            else:
                                                print("==========Closed intervals on both sides==========")
                                            lines.append(row)  # 第四步：将过滤后的行添加到列表中.
                                    print('=====================End loading===========================')
                                    print("\n".join(lines))
                                    return json.loads("\n".join(lines))  # 将列表中的每个字符串用某一个符号拼接为一整个字符串，用json.loads()函数加载，这样就大功告成啦！！

                        with open(j2_full_path) as fw:
                            if str(fw.readlines()).__contains__('datas'):
                                print('=====================Structure that meets expectations===========================')
                                spec_j2 = load_json(j2_full_path)
                            else:
                                print('===============Structure that does not meet expectations===============')
                                spec_j2['params'] = ''
                                spec_j2['datas'] = ''

                        def pd_format(pd_data):
                            pd_data = pd.DataFrame(pd_data)
                            pd_data = pd_data.astype(str)
                            columns = list(pd_data.select_dtypes(include=['object']).columns.values)
                            pd_data[columns] = pd_data[columns].replace([None], '')
                            pd_data[columns] = pd_data[columns].replace([{}], '')
                            pd_data[columns] = pd_data[columns].replace(['nan'], '')
                            pd_data = trim_columns(pd_data)
                            return pd_data

                        print('开始执行params入库操作:\n{}'.format(iterator))
                        params_db_str = 'params_{}'.format(combine_flag)
                        ## datas
                        print('开始执行datas入库操作:\n{}'.format(iterator))
                        datas_db_str = 'datas_{}'.format(combine_flag)
                        print('开始执行表合并操作操作:\n{}'.format(iterator))
                        print('=====================================START HARIX_Render_Case==================================')
                        j2_param = {'j2_full_name': iterator, 'bug_id': bug_id,
                                    'params': json.dumps(spec_j2['params'], ensure_ascii=False),
                                    'datas': json.dumps(spec_j2['datas'], ensure_ascii=False),
                                    'invalid_flag_dict': json.dumps(invalid_flag_dict, ensure_ascii=False)}
                        j2_param_render = pd.DataFrame.from_dict(j2_param, orient='index').T
                        j2_param_render.to_sql('HARIX_Render_Case', con=engine, if_exists='append', index=False)
                        print('=====================================End HARIX_Render_Case==================================')
                        if invalid_flag_dict !=dict():#not null
                            print('=====================================START invalid_flag_dict==================================')
                            df_invalid_flag_dict = pd_format(invalid_flag_dict)
                            df_invalid_flag_dict.to_sql('invalid_flag_dict_{}'.format(combine_flag), con=engine, if_exists='append', index=False)
                            print('=====================================End invalid_flag_dict==================================')
                        print('计数器:\n{}\n调度文件路径:\n{}'.format(j2_full_path, counter))
                        combine_flag_list.append(combine_flag)
                        bug_id_list.append(bug_id)
                        params_list.append(params_db_str)
                        datas_list.append(datas_db_str)
            print(invalid_flag_list)
            conf_param_list['robot_path'] = {'.robot配置文件夹目录路径': all_final_robot_path}
            conf_param_list['j2_path'] = {'.j2配置文件夹目录路径': j2_file_list}
            conf_param_list['invalid_flag_dict'] = {'非标准J2文件集合': invalid_flag_list}
            conf_param_list['pop_flag_list'] = {'非标准J2文件POP集合': pop_flag_list}
            conf_param_list['replace_flag_list'] = {'非标准J2文件Replace集合': replace_flag_list}
            conf_param_list['valid_flag_dict'] = {'标准J2文件集合': valid_flag_list}
            conf_param_list['bug_id_list'] = {'CaseID集合': bug_id_list}
            conf_param_list['case_parameter'] = {'Case_Parameter集合': params_list}
            conf_param_list['case_scene'] = {'Case_Scene集合': datas_list}
            print(files_all, '\n', bug_id_list, '\n', files_dict)
            env_status = ['Success', conf_param_list, bug_id_list]
            return env_status
        except Exception as e:
            print('exception file:\n{}'.format(j2_full_path))
            env_status = ['Failure', conf_param_list, '执行失败,回调信息\n{}'.format(e)]
            return env_status


def sql_write_j2(ginger_dict=j2_dict):
    import os
    db_dict = ginger_dict['db_dict'] if 'db_dict' in ginger_dict else None
    if isinstance(db_dict, dict) and db_dict.keys() >= {'db_ip', 'db_port', 'db_user', 'db_password', 'db_name'}:
        engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(db_dict['db_user'], db_dict['db_password'], db_dict['db_ip'], db_dict['db_port'], db_dict['db_name']))
        print('当前系统的连接串:\n{}'.format(engine, db_dict))
    else:
        print('当前系统的连接串不满足参数要求')

    if isinstance(ginger_dict, dict) and not 'customParameters' in ginger_dict:
        print('==========================接口调用模式==================================')
    else:
        print('==========================命令行CI调用模式==================================')
        ginger_dict = {
            "customParameters": {
                "项目名称": "Vending",
                "BugID在索引_的第几个位置": 0,
                "生成的配置文件夹目录": "cases/sit_test/j2_sql",
                "j2配置文件夹目录": "data/templates/j2_sql"
            }
        }
        ginger_dict = ginger_dict['customParameters']
    project_path = os.path.abspath(os.path.join(os.getcwd()))
    print('当前项目根目录绝对路径地址:\n{}'.format(project_path))
    print('=====================================End==================================')
    template_iterator = '/cases/sit_test/template_sql.j2'
    template_path = project_path + template_iterator
    if os.path.exists(project_path) and os.path.exists(template_path):
        try:
            bug_id_list = []
            conf_param_list = []
            project_name = ginger_dict['项目名称'] if '项目名称' in ginger_dict else None
            robot_generation_folder = ginger_dict['生成的配置文件夹目录'] if '生成的配置文件夹目录' in ginger_dict else None
            j2_source_folder = ginger_dict['j2配置文件夹目录'] if 'j2配置文件夹目录' in ginger_dict else None
            slice_index = ginger_dict['BugID在索引_的第几个位置'] if 'BugID在索引_的第几个位置' in ginger_dict else None
            conf_folder_name = j2_source_folder.rsplit("/", 1)[1]
            sql_str = "select table_name from information_schema.tables where table_schema='HARIX_DB'"
            db_all_table = pd.read_sql_query(sql_str, con=engine)
            print(db_all_table.values.tolist())
            at = db_all_table['table_name'].values.tolist()
            def find_contains(elements):
                lst = list(filter(lambda x: x.find(elements) >= 0, at))
                print(lst)
                new_data = []
                for idx in lst:
                    if str(idx).__contains__(elements):
                        idx = str(idx).replace(elements, '')
                        new_data.append(idx)
                print(new_data)
                return new_data

            datas_table_list = find_contains('datas_')
            print(datas_table_list)
            params_table_list = find_contains('params_')
            print(params_table_list)
            invalid_table_list = find_contains('invalid_flag_dict_')
            print(invalid_table_list)
            db_query_results_j2 = pd.read_sql_table(table_name='HARIX_Render_Case', con=engine)
            print('##############db_query_sort#################')
            project_root_path = os.path.join(project_path, 'data/templates/sql_j2')
            path_excel = os.path.join(project_root_path, 'x_excel.xlsx')
            path_j2_list = db_query_results_j2['j2_full_name'].values.tolist()
            db_query_dict_j2 = db_query_results_j2.to_dict()
            j2_name_list = db_query_dict_j2['j2_full_name']
            for j2_name in j2_name_list:
                dict_datas = dict()
                conf_param_dict = dict()
                if db_query_dict_j2['invalid_flag_dict'][j2_name]!={}:
                    iter_invalid = db_query_dict_j2['invalid_flag_dict'][j2_name]
                    print('iter_invalid:\n{}'.format(iter_invalid))
                    if isinstance(iter_invalid, str):
                        iter_invalid_dict = json.loads(iter_invalid )
                        print('iter_invalid_dict:\n{}'.format(iter_invalid_dict))
                dict_datas['params'] = json.loads(db_query_dict_j2['params'][j2_name])
                dict_datas['datas'] = json.loads(db_query_dict_j2['datas'][j2_name])
                bug_id = db_query_dict_j2['bug_id'][j2_name]
                path_j2 = j2_name_list[j2_name]
                invalid_flag_dict = db_query_dict_j2['invalid_flag_dict'][j2_name]
                path_j2 = os.path.join(project_root_path, path_j2)
                conf_param_dict.update({'bug_id': bug_id,'invalid_flag_dict': json.loads(invalid_flag_dict),'j2_content':dict_datas})
                conf_param_list.append(conf_param_dict)
                with open(path_j2, "w") as fd:
                    fd.write(json.dumps(dict_datas, indent=2, ensure_ascii=False))
                print('##############format_json#################')
            env_status = ['Success', conf_param_list, bug_id_list]
            return env_status
        except Exception as e:
            env_status = ['Failure', conf_param_list, '执行失败,回调信息\n{}'.format(e)]
            return env_status

def stop_timer():
    # cmd = 'lsof -i :9002 |grep -v grep|grep -v tail|cut -c 9-15|xargs |cut -c 15-23'
    get_process_pid = b'''lsof -i :9002 |grep -v grep|grep -v tail|cut -c 9-15|xargs |cut -c 15-23'''
    # _cmd = 'ps -ef|grep debug_case_api_client |grep -v grep|grep -v tail|cut -c 9-15|xargs'
    _cmd = "lsof -i :9002 |grep LISTEN | awk '{ print $2 }'"
    return_result = dict()
    process_pid = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE)
    out = process_pid.stdout.read()
    print(out)
    return_result['cmd'] = {'命令行': _cmd, '输出进程': out}
    if isinstance(out, bytes) and out !=b'\n' and not out.decode('utf-8').__contains__(' '):
        out = out.decode('utf-8')
        print('单个进程号\n{}'.format(out))
        if out.__contains__('\n'):
            pid_list = out.split('\n')
            none_pid_list = list(filter(None,out.split('\n')))
            if isinstance(pid_list, list) and len(none_pid_list)!=1:
                for idx in none_pid_list:
                    kill_pid_cmd = 'echo "Cloud1688" | sudo -S kill -9 {}'.format(idx)
                    print(kill_pid_cmd)
                    kill_pid = subprocess.Popen(kill_pid_cmd, shell=True, stdout=subprocess.PIPE)
                    kill_pid_out = kill_pid.stdout.read()
            return_result['execute_cmd'] = {'命令行': kill_pid_cmd, '输出进程': kill_pid_out}
            print(kill_pid_out)
        # pid = out.decode('utf-8').split('\n')[0]
        # kill_pid_cmd = 'echo "Cloud1688" | sudo -S kill -9 {}'.format(pid)
        # kill_pid = subprocess.Popen(kill_pid_cmd, shell=True, stdout=subprocess.PIPE)
        # kill_pid_out = kill_pid.stdout.read()
    if isinstance(out, bytes) and out.decode('utf-8').__contains__(' '):
        print('2个进程号\n{}'.format(out.decode('utf-8')))
        pid = out.decode('utf-8').split(' ')[0]
        kill_pid_cmd = 'echo "Cloud1688" | sudo -S kill -9 {}'.format(pid)
        kill_pid = subprocess.Popen(kill_pid_cmd, shell=True, stdout=subprocess.PIPE)
        kill_pid_out = kill_pid.stdout.read()
        return_result['execute_cmd'] = {'命令行': kill_pid_cmd, '输出进程': kill_pid_out}
        print(kill_pid_out)
    return return_result


def start_job(ginger_dict=JobDict):
    ginger_dict = ginger_dict['customParameters']
    project_path = os.path.abspath(os.path.join(os.getcwd()))
    print('当前项目根目录绝对路径地址:\n{}'.format(project_path))
    jenkins_config = ginger_dict['jenkins_config'] if 'jenkins_config' in ginger_dict else None
    task_scheduling = ginger_dict['showTrueOrFalse'] if 'showTrueOrFalse' in ginger_dict else None
    conf_param_list = dict()
    conf_param_list['customParameters'] = {'jenkins_config': jenkins_config}
    if isinstance(ginger_dict, dict) and ginger_dict.keys() >= {'jenkins_config', 'showTrueOrFalse', 'db_dict'}:
        print('==========================接口调用模式==================================')
        try:
            server = jenkins.Jenkins(jenkins_config['server'], username=jenkins_config['username'], password=jenkins_config['password'])
            server.get_all_jobs()
            build_dict = dict()
            current_build_num = server.get_job_info(jenkins_config['job_name'])['lastCompletedBuild']['number'] + 1
            if task_scheduling['stop']:
                start_build_result = server.build_job(jenkins_config['job_name'])
                build_dict['start_build_result'] = {'start_build_result': start_build_result, 'start_job_Num': current_build_num}
            if not task_scheduling['stop']:
                stop_build_result = server.stop_build(jenkins_config['job_name'], current_build_num)
                build_dict['stop_build_result'] = {'stop_build_result': stop_build_result, 'stop_job_Num': current_build_num}
            # server.stop_build(jenkins_config['job_name'], 33)
            # current_build_num = server.get_job_info(jenkins_config['job_name'])['lastCompletedBuild']['number'] + 1
            current_build_out = server.get_build_console_output(jenkins_config['job_name'], 6)[-1000:]
            print('=====================================End==================================')
            conf_param_list['BuildConsoleOutput'] = {'job_output': current_build_out}
            conf_param_list['build_dict'] = {'build_dict': build_dict}
            env_status = ['Success', conf_param_list, '执行成功,回调信息\n{}'.format(build_dict)]
            print(env_status)
            return env_status

        except Exception as e:
            env_status = ['Failure', conf_param_list, '执行失败,回调信息\n{}'.format(e)]
            return env_status
    else:
        return_msg = '入参条件不符合预期:\n{}\n'.format(ginger_dict)
        print(return_msg)
        return return_msg


def dialogflow_qa(ginger_dict=DialogFlowDict):
    excel_name = 'Contents_of_ASEAN_Expo_Knowledge_Base.xlsx'
    #df_name = 'fbtest-tfxodj-2603bf40e440.json'
    df_name = 'fujian-52e4bf0f23e0.json'
    import os
    import datetime
    db_dict = ginger_dict['customParameters']['db_dict'] if 'db_dict' in ginger_dict['customParameters'] else None
    if isinstance(db_dict, dict) and db_dict.keys() > {'db_ip', 'db_port', 'db_user', 'db_password', 'db_name'}:
        engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(db_dict['db_user'], db_dict['db_password'], db_dict['db_ip'], db_dict['db_port'], db_dict['db_name']))
        print('当前系统的连接串:\n{}'.format(engine, db_dict))
    else:
        print('当前系统的连接串不满足参数要求')
    ginger_dict = ginger_dict['customParameters']
    dialogflow_config = ginger_dict['dialogflow_config'] if 'dialogflow_config' in ginger_dict else None
    intent_name_prefix = dialogflow_config['intent_name_prefix'] if 'intent_name_prefix' in dialogflow_config else 'Default_'
    project_id = dialogflow_config['project_id'] if 'project_id' in dialogflow_config else None
    request_frequency = dialogflow_config['request_frequency'] if 'request_frequency' in dialogflow_config else 5
    language_code = dialogflow_config['language_code'] if 'language_code' in dialogflow_config else 'en'
    project_path = os.path.abspath(os.path.join(os.getcwd()))
    print('当前项目根目录绝对路径地址:\n{}'.format(project_path))
    excel_path = project_path + os.sep + 'data' + os.sep + 'qa_data' + os.sep + excel_name
    df_json_path = project_path + os.sep + 'data' + os.sep + 'qa_data' + os.sep + df_name
    conf_param_list = dict()
    if request_frequency and isinstance(intent_name_prefix, str) and isinstance(project_id, str) and excel_name and os.path.exists(excel_path) and os.path.exists(df_json_path):
        try:
            all_sheet_names_pd = pd.ExcelFile(excel_path)
            all_sheet_names = all_sheet_names_pd.sheet_names
            print('所有表格名称:\n{}'.format(all_sheet_names))
            response_list = []
            id = 0
            for sn in all_sheet_names:
                handle_excel_path = project_path + os.sep + 'data' + os.sep + 'qa_data' + os.sep + 'Data_Processed_{}.xlsx'.format(sn)
                df_env = pd.read_excel(all_sheet_names_pd, sn, engine='openpyxl')
                # df_env = pd.read_excel(excel_path, sheet_name=0, engine='openpyxl')
                nrows = df_env.shape[0]
                ncols = df_env.columns.size
                print(nrows)
                print(ncols)
                print("=========================================================================")
                df_env = df_env.replace(np.nan, '')
                df_env = trim_columns(df_env)
                if isinstance(df_env, pd.DataFrame):
                    # print(df_env.columns.tolist())
                    question_list = []
                    answer_list = []
                    for item in df_env.itertuples():
                        print('当前行数据是:\n', item)
                        print(item._fields)
                        print('\n获取行索引: ', item.Index)
                        print('\n获取该行的x4值: ', item)
                        phrases_parts = str(item[1]).replace('&&', ',').split(',')
                        response_texts = str(item[2]).replace('&&', ',').split(',')
                        phrases_parts = [x.encode('utf-8').decode('utf-8') for x in phrases_parts]
                        response_texts = [y.encode('utf-8').decode('utf-8') for y in response_texts]

                        question_list.append(phrases_parts)
                        answer_list.append(response_texts)
                        print('=====================================Single line==================================')
                        print('问题:\n{}\n回复:\n{}'.format(question_list, answer_list))
                    print('=====================================All line==================================')
                    print('问题:\n{}\n回复:\n{}'.format(question_list, answer_list))
                    # phrases_parts = ['你在哪边上班', '上班地点', '去哪上班']
                    # rsp = ['我在望京上班', '我在厦门上班', '我在福州上班', '我在房山上班']
                    # project_id = 'fbtest-tfxodj'
                    print(question_list)
                    print(answer_list)
                    pd.DataFrame({'question_list': question_list, 'answer_list': answer_list}).to_excel(handle_excel_path)
                    combine_list = pd.DataFrame({'question_list': question_list, 'answer_list': answer_list}).values.tolist()
                    def create_intent(project_id, intent_name, phrases_parts, response_texts, language_code):
                        intents_client = dialogflow_v2beta1.IntentsClient.from_service_account_json(df_json_path)
                        parent = intents_client.project_agent_path(project_id)
                        training_phrases = []
                        for training_phrases_part in phrases_parts:
                            part = dialogflow_v2beta1.types.Intent.TrainingPhrase.Part(text=training_phrases_part)
                            training_phrase = dialogflow_v2beta1.types.Intent.TrainingPhrase(parts=[part])
                            training_phrases.append(training_phrase)

                        text = dialogflow_v2beta1.types.Intent.Message.Text(text=response_texts)
                        message = dialogflow_v2beta1.types.Intent.Message(text=text)

                        intent = dialogflow_v2beta1.types.Intent(
                            display_name=intent_name,
                            training_phrases=training_phrases,
                            messages=[message])

                        response = intents_client.create_intent(parent, intent,language_code=language_code)
                        print('Intent created: {}'.format(response))
                        if isinstance(request_frequency, int):
                            time.sleep(request_frequency)
                        else:
                            time.sleep(5)

                        rsp = MessageToDict(response)
                        print('GRPC输出日志:\n{}'.format(rsp))
                        print('===============================Google DialogFlow Return success==================================')
                        return rsp

                    for idx in combine_list:
                        id = id + 1
                        print(idx)
                        response = create_intent(project_id, '{}_{}'.format(intent_name_prefix, id), idx[0], idx[1],language_code)
                        project_url = str('https://dialogflow.cloud.google.com/#/' + response['name'].replace('agent/','').replace('projects','agent').replace('intents','editIntent') + '/')
                        # hyper_link = '<a href="{}"></a>'.format(project_url)
                        response_list.append(response)
                        exec_param = dict()
                        exec_param['exec_param'] = {'dialogflow_config': dialogflow_config, 'runtime_param': {'ID': id, 'phrases_parts': idx[0], 'response_texts': idx[1]}}
                        df_exec_iterator = {
                            "exec_date": str(datetime.datetime.now()),
                            "phrases_parts": '&&'.join(idx[0]),
                            "response_texts": '&&'.join(idx[1]),
                            "exec_callback": json.dumps(response, ensure_ascii=False),
                            "project_url": str(project_url),
                            "execution_env": "134",
                            "table_name": db_dict['table_name'],
                            "exec_param": json.dumps(exec_param, ensure_ascii=False),

                        }
                        df_to_sql(engine, df_exec_iterator)

                else:
                    env_status = ['Failure', conf_param_list, '执行失败,当前表格内容不合法']
                    return env_status
            conf_param_list['all_sheet_names'] = {'遍历表格名称': all_sheet_names}
            conf_param_list['DialogFlowResponse'] = {'dialogflow返回值': response_list}
            conf_param_list['customParameters'] = {'dialogflow_config': dialogflow_config}
            conf_param_list['QAParameters'] = {'问题': question_list, '回复': answer_list}
            env_status = ['Success', conf_param_list, '执行成功,回调信息\n{}'.format(json.dumps(dialogflow_config, ensure_ascii=False))]
            return env_status
        except Exception as e:
            env_status = ['Failure', conf_param_list, '执行失败,回调信息\n{}'.format(e)]
            return env_status
    else:
        return_msg = '入参条件不符合预期: excel_path\n{}\nintent_name_prefix:\n{}\nproject_id:\n{}\ndf_json_path:\n{}'.format(excel_path, intent_name_prefix,project_id, df_json_path)
        print(return_msg)
        return return_msg


def df_qa(ginger_dict=QADict):
    excel_name = 'Contents_of_ASEAN_Expo_Knowledge_Base.xlsx'
    # df_name = 'fbtest-tfxodj-2603bf40e440.json'
    df_name = 'fujian-52e4bf0f23e0.json'
    import os
    db_dict = ginger_dict['customParameters']['db_dict'] if 'db_dict' in ginger_dict['customParameters'] else None
    if isinstance(db_dict, dict) and db_dict.keys() >= {'db_ip', 'db_port', 'db_user', 'db_password', 'db_name'}:
        engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(db_dict['db_user'], db_dict['db_password'], db_dict['db_ip'], db_dict['db_port'], db_dict['db_name']))
        print('当前系统的连接串:\n{}'.format(engine, db_dict))
    else:
        print('当前系统的连接串不满足参数要求')
    ginger_dict = ginger_dict['customParameters']
    dialogflow_config = ginger_dict['dialogflow_config'] if 'dialogflow_config' in ginger_dict else None
    project_id = dialogflow_config['project_id'] if 'project_id' in dialogflow_config else None
    dialogflow_qa = ginger_dict['dialogflow_qa'] if 'dialogflow_qa' in ginger_dict else None
    request_frequency = dialogflow_config['request_frequency'] if 'request_frequency' in dialogflow_config else 5
    language_code = dialogflow_config['language_code'] if 'language_code' in dialogflow_config else 'en'
    project_path = os.path.abspath(os.path.join(os.getcwd()))
    print('当前项目根目录绝对路径地址:\n{}'.format(project_path))
    df_json_path = project_path + os.sep + 'data' + os.sep + 'qa_data' + os.sep + df_name
    conf_param_list = dict()
    if request_frequency and isinstance(project_id, str) and excel_name and os.path.exists(df_json_path):
        try:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (df_json_path)
            # DIALOGFLOW_PROJECT_ID = 'fbtest-tfxodj'
            # DIALOGFLOW_LANGUAGE_CODE = 'en'
            SESSION_ID = str(uuid.uuid4())
            # text_to_be_analyzed = "南宁国际会展中心可以搭建多少个展位"
            print('语料入参数:\n{}'.format(dialogflow_qa))
            session_client = dialogflow.SessionsClient()
            session = session_client.session_path(project_id, SESSION_ID)
            text_input = dialogflow.types.TextInput(text=dialogflow_qa, language_code=language_code)
            query_input = dialogflow.types.QueryInput(text=text_input)
            try:
                print('=============================== DialogFlow Incoming parameters==================================')
                print('query_input:\n{}'.format(query_input))
                print('session:\n{}'.format(session))
                print('===============================Google DialogFlow QA==================================')
                response = session_client.detect_intent(session=session, query_input=query_input)
            except InvalidArgument:
                raise

            print("Query text:", response.query_result.query_text)
            print("Detected intent:", response.query_result.intent.display_name)
            print("Detected intent confidence:", response.query_result.intent_detection_confidence)
            print("DialogFlow Response:", response.query_result.fulfillment_text)
            rsp = MessageToDict(response)
            print('GRPC输出日志:\n{}'.format(rsp))
            print('===============================Google DialogFlow Return success==================================')
            conf_param_list['customParameters'] = {'dialogflow_config': ginger_dict}
            conf_param_list['QAParameters'] = {'问题': dialogflow_qa, '回复': rsp}
            exec_param = dict()
            exec_param['exec_param'] = {
                'dialogflow_config': dialogflow_config,
                'runtime_param': {'phrases_parts': dialogflow_qa, 'response_texts': rsp}
            }
            import datetime
            qa_exec_iterator = {
                "exec_date": str(datetime.datetime.now()),
                "direct_url_qa": str('https://dialogflow.cloud.google.com/#/' + rsp['queryResult']['intent']['name'].replace('agent/','').replace('projects','agent').replace('intents','editIntent') + '/'),
                "phrases_parts": str(dialogflow_qa),
                "response_texts": str(response.query_result.fulfillment_text),
                "exec_callback": json.dumps(rsp, ensure_ascii=False),
                "execution_env": "134",
                "table_name": db_dict['table_name'],
                "exec_param": json.dumps(exec_param, ensure_ascii=False),

            }
            qa_to_sql(engine, qa_exec_iterator)

            env_status = ['Success', conf_param_list, '执行成功,回调信息\n{}'.format(json.dumps(dialogflow_config, ensure_ascii=False))]
            return env_status
        except Exception as e:
            env_status = ['Failure', conf_param_list, '执行失败,回调信息\n{}'.format(e)]
            return env_status
    else:
        return_msg = '入参条件不符合预期:\nproject_id:\n{}\ndf_json_path:\n{}'.format(project_id, df_json_path)
        print(return_msg)
        return return_msg


def batch_delete_intents(ginger_dict=QADict):
    excel_name = 'Contents_of_ASEAN_Expo_Knowledge_Base.xlsx'
    #df_name = 'fbtest-tfxodj-2603bf40e440.json'
    df_name = 'fujian-52e4bf0f23e0.json'
    import os
    db_dict = ginger_dict['customParameters']['db_dict'] if 'db_dict' in ginger_dict['customParameters'] else None
    if isinstance(db_dict, dict) and db_dict.keys() >= {'db_ip', 'db_port', 'db_user', 'db_password', 'db_name'}:
        engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(db_dict['db_user'], db_dict['db_password'], db_dict['db_ip'], db_dict['db_port'], db_dict['db_name']))
        print('当前系统的连接串:\n{}'.format(engine, db_dict))
    else:
        print('当前系统的连接串不满足参数要求')
    ginger_dict = ginger_dict['customParameters']
    dialogflow_config = ginger_dict['dialogflow_config'] if 'dialogflow_config' in ginger_dict else None
    project_id = dialogflow_config['project_id'] if 'project_id' in dialogflow_config else None
    dialogflow_qa = ginger_dict['dialogflow_qa'] if 'dialogflow_qa' in ginger_dict else None
    project_path = os.path.abspath(os.path.join(os.getcwd()))
    print('当前项目根目录绝对路径地址:\n{}'.format(project_path))
    df_json_path = project_path + os.sep + 'data' + os.sep + 'qa_data' + os.sep + df_name
    conf_param_list = dict()
    if isinstance(project_id, str) and os.path.exists(df_json_path):
        try:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (df_json_path)
            intents_client = dialogflow_v2beta1.IntentsClient.from_service_account_json(df_json_path)
            parent = intents_client.project_agent_path(project_id)
            intents_to_delete = []
            display_name_list = []
            question_list = []
            rsp_list = []
            df_qa_url_list = []
            intents = intents_client.list_intents(parent)
            for intent in intents:
                intent = intents_client.get_intent(intent.name, intent_view=dialogflow.enums.IntentView.INTENT_VIEW_FULL)
                question = MessageToDict(intents_client.get_intent(intent.name, intent_view=dialogflow.enums.IntentView.INTENT_VIEW_FULL))['trainingPhrases']
                answer = MessageToDict(intent)['messages'][0]['text']
                print(intent.name)
                print(intent.display_name)
                question_list.append(question[0]['parts'][0]['text'])
                rsp_list.append(answer['text'][0])
                df_qa_url_list.append(str('https://dialogflow.cloud.google.com/#/' + MessageToDict(intent)['name'].replace('agent/','').replace('projects','agent').replace('intents','editIntent') + '/'))
                display_name_list.append(intent.display_name)
                if intent.display_name:
                    intents_to_delete.append(intent)
            if intents_to_delete !=[]:
                rsp = MessageToDict(intents_client.batch_delete_intents(parent, intents_to_delete).operation)
                print(rsp)
            else:
                rsp = []
            # qa_to_sql(engine, qa_exec_iterator)
            conf_param_list['customParameters'] = {'dialogflow_config': dialogflow_config}
            conf_param_list['QAParameters'] = {'问题': question_list, '回复': rsp_list}

            exec_param = dict()
            exec_param['exec_param'] = {
                'dialogflow_config': dialogflow_config,
                'runtime_param': {'phrases_parts': '', 'response_texts': ''}
            }
            qa_exec_iterator = {
                "exec_date": str(datetime.datetime.now()),
                "direct_url_qa": str('&&'.join(df_qa_url_list)),
                "phrases_parts": str('&&'.join(question_list)),
                "response_texts": str('&&'.join(rsp_list)),
                "exec_callback": json.dumps(rsp,ensure_ascii=False),
                "execution_env": "134",
                "table_name": db_dict['table_name'],
                "exec_param": json.dumps(exec_param, ensure_ascii=False),

            }
            qa_to_sql(engine, qa_exec_iterator)

            env_status = ['Success', conf_param_list, '执行成功,回调信息\n{}'.format(json.dumps(ginger_dict, ensure_ascii=False))]
            return env_status
        except Exception as e:
            env_status = ['Failure', conf_param_list, '执行失败,回调信息\n{}'.format(e)]
            return env_status
    else:
        return_msg = '入参条件不符合预期:\nproject_id:\n{}\ndf_json_path:\n{}'.format(project_id, df_json_path)
        print(return_msg)
        return return_msg


def df_to_sql(engine, df_exec_iterator):
    try:
        conf_param_list = dict()
        conf_param_list['dialogflow_collection'] = df_exec_iterator
        if isinstance(df_exec_iterator, dict) and df_exec_iterator.keys() >= {'execution_env', 'exec_date', 'phrases_parts', 'response_texts', 'project_url', 'exec_callback',  'exec_param', 'table_name'}:
            df_sql = pd.DataFrame.from_dict(df_exec_iterator, orient='index').T
            dtypedict = {
                'id': BigInteger(),
                'execution_env': NVARCHAR(length=255),
                'exec_date': NVARCHAR(length=255),
                'phrases_parts': NVARCHAR(length=255),
                'response_texts': NVARCHAR(length=255),
                'project_url': NVARCHAR(length=255),
                'exec_callback': NVARCHAR(length=255),
                'exec_date': NVARCHAR(length=255),
                'exec_param': NVARCHAR(length=255)
            }

            def trim_columns(df):
                trim = lambda x: x.strip() if isinstance(x, str) else x
                return df.applymap(trim)

            obj_columns = list(df_sql.select_dtypes(include=['object']).columns.values)
            df_sql[obj_columns] = df_sql[obj_columns].replace([None], '')
            df_sql[obj_columns] = df_sql[obj_columns].replace([{}], '')
            df_sql = trim_columns(df_sql)
            sort_columns = ['execution_env', 'exec_date', 'phrases_parts', 'response_texts', 'project_url', 'exec_callback', 'exec_param']
            df_sql = df_sql[sort_columns]
            table_name = df_exec_iterator['table_name']
            df_sql.to_sql(table_name, con=engine, if_exists='append', index=False)
            # with self.engine.connect() as con:
            # 	con.execute('ALTER TABLE {} ADD PRIMARY KEY (`{}`);'.format(table_name, 'Index'))

            print(df_sql)
            print(sort_columns)
            return_list = df_sql.to_json(orient="records", force_ascii=False)
            if isinstance(return_list, str):
                return_list = json.loads(return_list)
            return return_list, 'Success', 'DialogFlow日志执行[入库成功]'
        else:
            env_status = ['Failure', conf_param_list, '执行失败,当前表格内容不合法']
            return env_status
    except Exception as e:
        email_status = ['Failure', 'DialogFlow日志入库失败,回调信息{}'.format(e)]
        return email_status


def qa_to_sql(engine, qa_exec_iterator):
    try:
        conf_param_list = dict()
        conf_param_list['dialogflow_collection'] = qa_exec_iterator
        if isinstance(qa_exec_iterator, dict) and qa_exec_iterator.keys() >= {'execution_env', 'exec_date','direct_url_qa', 'phrases_parts', 'response_texts', 'exec_callback',  'exec_param', 'table_name'}:
            df_sql = pd.DataFrame.from_dict(qa_exec_iterator, orient='index').T
            def trim_columns(df):
                trim = lambda x: x.strip() if isinstance(x, str) else x
                return df.applymap(trim)

            obj_columns = list(df_sql.select_dtypes(include=['object']).columns.values)
            df_sql[obj_columns] = df_sql[obj_columns].replace([None], '')
            df_sql[obj_columns] = df_sql[obj_columns].replace([{}], '')
            df_sql = trim_columns(df_sql)
            sort_columns = ['execution_env', 'exec_date', 'direct_url_qa', 'phrases_parts', 'response_texts', 'exec_callback', 'exec_param']
            df_sql = df_sql[sort_columns]
            table_name = qa_exec_iterator['table_name']
            df_sql.to_sql(table_name, con=engine, if_exists='append', index=False)
            print(df_sql)
            print(sort_columns)
            return_list = df_sql.to_json(orient="records", force_ascii=False)
            if isinstance(return_list, str):
                return_list = json.loads(return_list)
            return return_list, 'Success', 'DialogFlow日志执行[入库成功]'
        else:
            env_status = ['Failure', conf_param_list, '执行失败,当前dialogflow返回内容不合法,提交数据库失败\n{}'.format(json.dumps(qa_exec_iterator, ensure_ascii=False))]
            return env_status
    except Exception as e:
        email_status = ['Failure', 'DialogFlow日志入库失败,回调信息{}'.format(e)]
        return email_status


def universal_to_sql(engine, table_name, df_exec_iterator):
    log_prefix = "universal_to_sql:"
    print('通用web渲染 执行结果return DB接口: {}\nGeneral web rendering Execution result return DB interface:'.format(log_prefix))
    try:
        conf_param_list = dict()
        conf_param_list['dialogflow_collection'] = df_exec_iterator
        if isinstance(df_exec_iterator, dict):
            df_sql = pd.DataFrame.from_dict(df_exec_iterator, orient='index').T
            def trim_columns(df):
                trim = lambda x: x.strip() if isinstance(x, str) else x
                return df.applymap(trim)

            obj_columns = list(df_sql.select_dtypes(include=['object']).columns.values)
            df_sql[obj_columns] = df_sql[obj_columns].replace([None], '')
            df_sql[obj_columns] = df_sql[obj_columns].replace([{}], '')
            df_sql = trim_columns(df_sql)
            sort_columns = ['execution_env', 'exec_date', 'phrases_parts', 'response_texts', 'project_url', 'exec_callback', 'exec_param']
            df_sql = df_sql[sort_columns]
            table_name = df_exec_iterator['table_name']
            df_sql.to_sql(table_name, con=engine, if_exists='append', index=False)
            print(df_sql)
            print(sort_columns)
            return_list = df_sql.to_json(orient="records", force_ascii=False)
            if isinstance(return_list, str):
                return_list = json.loads(return_list)
            return return_list, 'Success', 'BOSS 工厂批量设备 执行[入库成功]'
        if isinstance(df_exec_iterator, pd.DataFrame) and table_name:
            df_exec_iterator.to_sql(table_name, con=engine, if_exists='append', index=False)
            print('BOSS 工厂批量设备 执行[入库成功]')

        else:
            env_status = ['Failure', conf_param_list, '执行失败,当前表格内容不合法']
            return env_status
    except Exception as e:
        email_status = ['Failure', '日志入库失败,回调信息{}'.format(e)]
        return email_status


def universal_to_web(ginger_dict=WebDict):
    log_prefix = "universal_to_web:"
    print('通用web渲染 数据库中执行结果return web接口: {}'.format(log_prefix))
    try:
        import os
        project_path = os.path.abspath(os.path.join(os.getcwd()))
        os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
        conf_param_list = dict()
        db_dict = ginger_dict['customParameters']['db_dict'] if 'db_dict' in ginger_dict['customParameters'] else None
        if isinstance(db_dict, dict) and db_dict.keys() >= {'db_ip', 'db_port', 'db_user', 'db_password', 'db_name'}:
            engine = create_engine(
                'mysql+pymysql://{}:{}@{}:{}/{}'.format(db_dict['db_user'], db_dict['db_password'], db_dict['db_ip'],
                                                        db_dict['db_port'], db_dict['db_name']))
            print('当前系统的连接串:\n{}'.format(engine, db_dict))
        else:
            print('当前系统的连接串不满足参数要求')
        ginger_dict = ginger_dict['customParameters']
        table_name = db_dict['table_name']
        if isinstance(table_name, str) and engine:
            db_query_results = pd.read_sql_table(table_name=table_name, con=engine)
            try:
                print('##############db_query_sort#################')
                project_root_path = os.path.join(project_path, 'data/boss_data')
                path_excel = os.path.join(project_root_path, 'universal_to_web.xlsx')
                temp_excel = pd.ExcelWriter(path_excel)
                db_query_results.to_excel(temp_excel)
                temp_excel.save()
                db_query_excel = pd.read_excel(path_excel)
                if 'Unnamed: 0' in db_query_excel:
                    db_query_excel.pop('Unnamed: 0')
                db_query_excel = db_query_excel.reindex(index=db_query_excel.index[::-1])
                records_json = db_query_excel.to_json(orient="records", force_ascii=False)
                print('##############format_json#################')
                format_json = json.loads(records_json, encoding='utf8')
                print('##############format_json#################')
                conf_param_list['BossParameters'] = format_json
                env_status = ['Success', conf_param_list, '执行成功,回调信息\n{}'.format(json.dumps(ginger_dict, ensure_ascii=False))]
                return env_status
            except Exception as e:
                env_status = ['Failure', conf_param_list, '执行失败,当前表格内容不合法\n{}'.format(e)]
                return env_status

            return 'Success', format_json
        else:
            print('当前 数据结构不满足参数要求')
    except Exception as e:
        email_status = ['Failure', '日志入库失败,回调信息{}'.format(e)]
        return email_status


if __name__ == '__main__':
    # sys.path.append(".")
    args = sys.argv[1:]
    print(args, type(args), len(args))
    print(args)
    # root_path_parse(sheet_name='134')
    if len(args) == 0:
        print("==================================API service working=======================================")
        uvicorn.run(
            app='dialogflow_api_client:app',
            host='0.0.0.0',
            port=9009,
            reload=True, debug=False
        )
    else:
        print("==================================Auto schedule working=======================================")
        fire.Fire()
