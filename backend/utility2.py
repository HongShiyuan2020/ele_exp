from openai import OpenAI
import json
import random
import base64
import numpy as np
import os
from utility3 import tidy_det, conn_det

SERVER_DIR = os.path.dirname(__file__)
file_path = os.path.join(SERVER_DIR, '1_config.json')



# client = OpenAI(api_key='sk-5oFGTJyCXifa3ykPC8791a5a65E14515A3642918D3C992Ef',
#                 base_url="https://api.planetzero.live/v1/")

client = OpenAI(api_key='sk-4vj3NYKrgqfUfHSDVD4xkiuOuBpOlo6jGY0kWiq6ioUXswoC', 
                base_url="https://api.hunyuan.cloud.tencent.com/v1")

# client = OpenAI(api_key='sk-OWwbeu95SJyl88LXVaN4WWq3SuPHrnrLGAhSdU0tZJMiYiDv',
#                 base_url="https://api.planetzero.live/v1/")

# client = OpenAI(api_key='ollama',
#                 base_url="http://223.2.29.223:11434/v1/")

# path='traindata.txt'

class APIGetException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

#读取prompt并拼接   
def getprompt(config,phase,step):
    desc1 = config[phase]['desc1']
    desc2 = config[phase]['desc2']
    example = config[phase][step]['prompt']['example']
    mission = config[phase][step]['prompt']['mission']
    return f"{desc1}\n{example}\n{desc2}\n{mission}"

def getTableprompt(config, phase, step):
    return config[phase][step]['prompt'], config[phase][step]['promptTrue'], config[phase][step]['promptFalse']

def getanswer(prompt,history,usehis=False):
    answer = getans(prompt.replace("'", '"'),history,usehis)  # 调用函数获取返回的字符串
    start_idx = answer.find('{')  
    end_idx = answer.rfind('}') 
    json_string = answer[start_idx:end_idx+1]
    return  json_string
       
def getans(prompt, history, usehis=False):
    if not usehis :
        messages = [{"role":"user","content":prompt}]
    else:
        messages = [{"role":"system","content":history}]
        message_prompt = {"role":"user","content":prompt}
        messages.append(message_prompt)
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,  # 使用完整的消息列表
            # model="gpt-4-turbo",
            # model="gpt-4o",
            # model="deepseek-r1:32b",
            model="hunyuan-turbo",
            stream=False,
            temperature=0.7
        )
        result = chat_completion.choices[0].message.content
        return result
    except Exception as e:
        print(f"API调用失败：{e}")
        raise APIGetException()


#打乱选项,输出问题
def shuffle_options(data):
    answer = data.get("answer", "未找到答案")
    options = data.get("options", "未找到选项")
    feedbacks = data.get("feedbacks", "未找到评价")
    question = data.get("question", "未找到提问")

    options_list = list(options.items())
    feedbacks_list = list(feedbacks.items())
    new_answer_key = None

    random.shuffle(options_list)

    new_options = {}
    new_feedbacks = {}
    new_answer = None
    for i, (key, value) in enumerate(options_list):
        new_key = chr(65 + i)  # 生成新的选项标签 A, B, C, D...
        new_options[new_key] = value
        if options[key] == options['A']:
            new_answer_key = new_key
                  
        new_feedbacks[new_key] = feedbacks[key]

    return new_options, new_feedbacks, new_answer_key, question

def tfun(json_string):
    try:
        opt,fee,key,quest = shuffle_options(json.loads(json_string)) #opt:选项  fee 选项的反馈评价，key：正确答案
    except:
        raise APIGetException()
    return opt, fee, key, quest



class ChatProcess:
    def __init__(self, config):
        self.config = config                    # 配置文件
        self.steps = self.getstep(config)       # 阶段和步骤
        self.currentStep = 0                    # 当前步骤，从0开始计数
        self.stepCount = len(self.steps)        # 步骤总数
        self.history = "接下去将生成问题让学生回答\n"                       # 历史记录
        self.answer_times = 0                   # 当前问题学生回答次数
        self.question = None                    # 当前正在回答的问题
        self.answers = []
        self.client = OpenAI(api_key='sk-4vj3NYKrgqfUfHSDVD4xkiuOuBpOlo6jGY0kWiq6ioUXswoC', 
                base_url="https://api.hunyuan.cloud.tencent.com/v1")

    def getTans(self, prompt, history, useHis=False):
        if not useHis :
            messages = [{"role":"user","content":prompt}]
        else:
            messages = [{"role":"system","content":history}]
            message_prompt = {"role":"user","content":prompt}
            messages.append(message_prompt)
        try:
            response = self.client.chat.completions.create(
                model="hunyuan-turbo",
                messages=messages,
                temperature=0.7,
                stream=True,
            )
            return response                
        except Exception as e:
            print(f"API调用失败：{e}")
            raise APIGetException()

    def getstep(self,data):
        all_steps = []
        for stage_name, stage_data in data.items():
            for key in stage_data:
                if not key.startswith("desc"):  # 忽略 desc开头
                    all_steps.append((stage_name, key))
        return all_steps 
    
    '''
    :进行下一步，会根据当前状态自动切换下一步
    '''
    def next(self, result=None):
        if self.currentStep >= self.stepCount:
            self.currentStep = 0
            self.history = ""
            self.answer_times = 0
            return self.getEndInfo()

        phase, step = self.steps[self.currentStep]

        # 根据format的input选择步骤执行函数
        input_t = self.config[phase][step]["format"]["input"]
        self.history = self.history + f"现在是阶段{phase}步骤{step}\n"

        if input_t == "":
            return self.step_question(result)
        elif input_t == "table":
            return self.step_table(result)
        elif input_t == "circuit":
            return self.step_circuit(result)
        elif input_t == "connection":
            return self.step_connection(result)
        elif input_t == "record":
            return self.step_record(result)
        elif input_t == "tidyUp":
            return self.step_tidyup(result)
        elif input_t == "evaluation":
            return self.step_evaluation(result)
    
    def nextStream(self, res=None):
        if True:
            phase, step = self.steps[self.currentStep]
            desc1 = self.config[phase]['desc1']
            desc2 = self.config[phase][step]["desc"]            
            example = self.config[phase][step]["prompt"]["example"]
            ques = example["question"]
            options = example["options"]
            ans = example["answer"]
            
            prompt = f"{desc1}，当前步骤的目的为{desc2}，所出的问题要满足目的，且尽量容易理解\n例如：\n{ques}\n"
            for key in options:
                prompt += f"{key} {options[key]}\n"
                
            prompt += f"在我给出的例子中正确答案为：{ans}\n"
            prompt += f"这是我的教学目标，请你为我生成提问和答案选项，只要问题和选项注意只要输出这两项，不要任何提示文本，遵循我给的样例，不要生成任何评价。同时请确保C选项为正确答案"
            res = self.getTans(prompt, "")

            for chunk in res:
                print(f'{chunk.choices[0].delta.content}', end="")
    '''
    :生成总结
    '''
    def step_evaluation(self, result):
        phase, step = self.steps[self.currentStep]
        self.config[phase][step]["prompt"]["mission"]["学生回答情况"] = self.history 
        desc1 = self.config[phase]['desc1']
        desc2 = self.config[phase]['desc2']
        example = self.config[phase][step]['prompt']['example']
        mission = self.config[phase][step]['prompt']['mission']
        prompt = f"{desc1}\n{example}\n{desc2}\n{mission}"
        answer = getans(prompt,self.history)
        start_idx = answer.find('{')  
        end_idx = answer.rfind('}') 
        json_string = answer[start_idx:end_idx+1]
        try:
            res_obj = json.loads(json_string)
        except:
            res_obj = {
                "学生回答情况": "无",
                "生成评价": {
                    "overall_evaluation": {
                        "summary": "",
                        "score": 0,
                        "max_score": 5
                    },
                    "phase_evaluation": {
                        "question": {
                            "表现分析": {
                            },
                            "评价": ""
                        },
                        "evidence": {
                            "表现分析": {
                            },
                            "评价": ""
                        },
                        "analysis": {
                            "表现分析": {
                            },
                            "评价": ""
                        },
                        "discussion": {
                            "表现分析": {
                            },
                            "评价": ""
                        }
                    },
                    "improvement_suggestions": [
                        
                    ]
                }
                
            }
            
        self.currentStep += 1
        return {
            "type": "SUM_GET",
            "phase": phase,
            "reply": res_obj
        }   
    
    def step_sumup(self, result):
        phase, step = self.steps[self.currentStep]
        self.currentStep += 1
        return {
            "type": "SUM_GET",
            "reply": "你的实验完成得非常出色，不仅步骤清晰、操作规范，而且结果准确，充分展现了你的认真态度和扎实的实验能力，真是令人印象深刻！继续保持这份专注和热情，未来一定会更加优秀！",
            "phase": phase
        }
 
    def setCurrentStep(self, idx):
        if idx < 0 and idx >= self.stepCount:
            print("Idx Invaild!")
        
        self.currentStep = idx
        self.question = None
        self.answer_times = 0
          
    def startStepByIdx(self, idx):
        self.setCurrentStep(idx)
        return self.next()

    def getTableAnswer(self):
        phase, step = self.steps[self.currentStep]
        que, trueAns, falseAns = getTableprompt(self.config, phase, step)
        queF = getans(que, self.history) 
        
        if "</think>" in queF:
            queF = queF[queF.find("</think>")+len("</think>"):]
            queF = queF.strip()
        trueAnsF = getans(trueAns, self.history)
        if "</think>" in trueAnsF:
            trueAnsF = trueAnsF[trueAnsF.find("</think>")+len("</think>"):]
            trueAnsF = trueAnsF.strip()
        falseAnsF = getans(falseAns, self.history)
        if "</think>" in falseAnsF:
            falseAnsF = falseAnsF[falseAnsF.find("</think>")+len("</think>"):]
            falseAnsF = falseAnsF.strip()
            
        return {
            "queF": queF,
            "trueAnsF": trueAnsF,
            "falseAnsF": falseAnsF
        }



    '''
    :处理普通问答
    '''
    def step_question(self, result):
        if self.answer_times == 0:   
            if result != None:                              # 学生第一次回答问题
                self.history = self.history + "学生第一次回答问题给出答案:" + result["answer"] + "\n"
                if self.judge_answer(result) == True:
                    comment = self.getOKComment()
                    self.answer_times = 0
                    self.currentStep += 1
                    return comment
                else:
                    self.answer_times += 1
                    return self.getRetryComment(result)
            else:                                           # 学生没有回答这个问题且回答次数为0，说明还没给出问题，大模型生成问题，发送给学生
                self.question = self.getQuestion()
                return self.question
        else:
            if result != None:                              # 学生第二次回答问题
                self.history = self.history + "学生第二次回答问题给出答案:" + result["answer"] + "\n"
                if self.judge_answer(result) == True:
                    comment = self.getOKComment()
                    self.currentStep += 1
                    self.answer_times = 0
                    return comment
                else:
                    comment = self.getFailedComment()
                    self.currentStep += 1
                    self.answer_times = 0
                    return comment
            else:
                comment = self.getFailedComment()
                self.currentStep += 1
                self.answer_times = 0
                return comment

    def judge_answer(self, res):
        try:
            return res["answer"] == self.question["key"]
        except:
            return False

    def getOKComment(self):
        comment = {
            "type": "QUES_OK", 
            "reply": "回答正确。",
            "fee": self.question["fee"],
            "key": self.question["key"],
            "ready": True
        }
        return comment

    def getRetryComment(self, result):
        comment = {
            "type": "QUES_RETRY",
            "reply": "回答错误。",
            "question": self.question["question"],
            "opt": self.question["opt"],
            "wrong_answer": result["answer"],
            "fee": self.question["fee"]
        }
        return comment

    def getQuestion(self):
        phase, step = self.steps[self.currentStep]   
        extrainfo = self.config[phase][step]["extrainfo"]
        json_string = getanswer(getprompt(self.config,phase,step), "", extrainfo == "withhistory")
        opt, fee, key_ans, quest = tfun(json_string)

        self.history = self.history + f"现在是阶段{phase}步骤{step}，问题为：\n" + quest + "\n" +"选项为：\n" 
        for key, value in opt.items():
            self.history = self.history + f"options: {key}: {value}\n"
        self.history = self.history + "每个选项的反馈为：\n"
        for key, value in fee.items():
            self.history = self.history + f"options: {key}: {value}\n"
        
        return {
            "type": "QUES_GET",
            "question": quest,
            "opt": opt,
            "key": key_ans,
            "fee": fee,
            "phase": phase,
            "step": step,
            "step_desc": self.config[phase][step]["desc"]
        }

    def getFailedComment(self):
        comment = {
            "type": "QUES_FAILED",
            "reply": f"回答错误, 正确答案是 {self.question['key']}。",
            "fee": self.question["fee"],
            "key": self.question["key"],
            "ready": True
        }
        return comment
    
    
    '''
    : 处理表格回复
    '''
    def step_table(self, result):
        if result == None:              # 没有结果，说明还没给出提示，生成提示对话
            comment = self.getTableTip()
            return comment
        else:                           # 结果不为空，学生给出了table，给出评价
            if self.judgeTable(result):
                self.history = self.history + "学生成功设计表格\n"
                return self.getTableOK()   
            else:
                self.history = self.history + "学生设计表格出现错误\n"
                return self.getTableErr()               

    def getTableTip(self):
        phase, step = self.steps[self.currentStep]
        self.question = self.getTableAnswer()
        return {
            "type": "TABLE_GET",
            "reply": self.question["queF"],
            "table_type": self.config[phase][step]["table_type"],
            "phase": phase,
            "step": step,
            "step_desc": self.config[phase][step]["desc"]
        }

    def getTableOK(self):
        comment = {
            "type": "TABLE_OK",
            "reply": self.question["trueAnsF"],
        }
        self.currentStep += 1
        return comment

    def getTableErr(self):
        phase, step = self.steps[self.currentStep]
        comment = {
            "type": "TABLE_ER",
            "reply": self.question["falseAnsF"],
            "table": self.config[phase][step]["right_table"]
        }
        self.currentStep += 1
        return comment


    '''
    : 判定表格设计正确与否，当前在前端判断，故后端只需要判断前端返回的是否为OK
    '''
    def judgeTable(self, res):
        try :
            data = res["data"]
            if len(data) < 4:
                return False
            if len(data[0]) != 3:
                return False
            
            if data[0][0]["type"] != "label" or data[0][0]["value"] != "序号":
                return False
            for idx,  c in enumerate(data[1:]):
                if c[0]["type"] != "label" or str(idx + 1) != c[0]["value"]:
                    return False

            for r in data[1:]:
                for c in r[1:]:
                    if c["type"] != "input":
                        return False

            if data[0][1]["type"] != "label" or data[0][2]["type"] != "label":
                return False 

            if res["table_type"] == "UI":
                if "电压" in data[0][1]["value"] and "电流" in data[0][2]["value"]:
                    return True
                if "电压" in data[0][2]["value"] and "电流" in data[0][1]["value"]:
                    return True
            elif res["table_type"] == "IR":
                if "电阻" in data[0][1]["value"] and "电流" in data[0][2]["value"]:
                    return True
                if "电阻" in data[0][2]["value"] and "电流" in data[0][1]["value"]:
                    return True
            return False
        except:
            return False


    '''
    : 处理电路图设计回复
    '''
    def step_circuit(self, result):     
        if result == None:              # 没有结果，说明还没给出提示，生成提示对话
            comment = self.getCircuitTip()
            return comment
        else:                           # 结果不为空，学生给出了电路图设计结果，大模型给出评价
            if self.judgeCircuit(result):
                self.history = self.history + "学生成功设计电路\n"
                return self.getCircuitOK()   
            else:
                self.history = self.history + "学生设计的电路有错误\n"
                return self.getCircuitErr() 
    
    def getCircuitTip(self):
        phase, step = self.steps[self.currentStep]
        self.question = self.getTableAnswer()
        return {
            "type": "CIRCUIT_GET",
            "reply": self.question["queF"],
            "phase": phase,
            "step": step,
            "step_desc": self.config[phase][step]["desc"]
        }

    def judgeCircuit(self, res):
        try :
            return res["answer"] == "OK"
        except:
            return False

    def getCircuitOK(self):
        comment = {
            "type": "CIRCUIT_OK",
            "reply": self.question["trueAnsF"]
        }
        self.currentStep += 1
        return comment

    def getCircuitErr(self):
        phase, step = self.steps[self.currentStep]
        comment = {
            "type": "CIRCUIT_ER",
            "reply": self.question["falseAnsF"],
            "circuit": self.config[phase][step]["right_img"]
        }
        self.currentStep += 1
        return comment


    '''
    : 处理实物连接回复
    '''
    def step_connection(self, result):
        if result == None:              # 没有结果，说明还没给出提示，大模型生成提示对话
            comment = self.getConnectionTip()
            return comment
        else:                           # 结果不为空，学生给出了实物连接结果，大模型给出评价
            if self.judgeConnection(result):
                self.history = self.history + "学生成功连接电路\n" 
                return self.getOKConnection()   
            else:
                self.history = self.history + "学生连接电路出错\n" 
                return self.getErrConnection() 
    
    def getConnectionTip(self):
        phase, step = self.steps[self.currentStep]
        self.question = self.getTableAnswer()
        return {
            "type": "CONN_GET",
            "reply": self.question["queF"],
            "phase": phase,
            "step": step,
            "step_desc": self.config[phase][step]["desc"]
        }

    ## HSY
    def judgeConnection(self, res):
        try :
            img = res["data"]
            w, h, c = res["w"], res["h"], res["c"]
            img = np.frombuffer(base64.b64decode(img), dtype=np.uint8).reshape(h, w, c)
            res = conn_det(img)
            print("DET_OK")
            return res
        except:
            return False

    def getOKConnection(self):
        comment = {
            "type": "CONN_OK",
            "reply": self.question["trueAnsF"]
        }
        self.currentStep += 1
        return comment

    def getErrConnection(self):
        comment = {
            "type": "CONN_ER",
            "reply": self.question["falseAnsF"],
        }
        # self.currentStep += 1
        return comment


    '''
    : 处理实验结束时的回复
    '''
    def getEndInfo(self):
        return {
            "type": "END",
            "reply": "实验结束"
        }
    
    
    '''
    处理表格记录过程 
    '''
    def step_record(self, result):
        if result == None:
            return self.getStartRecordAns()
        else:
            if self.judegRecord(result):
                comment = self.getOKRecordAns(result)
                self.currentStep += 1
                return comment
            else:
                comment = self.getFailedRecordAns(result)
                self.currentStep += 1
                return comment
    
    def getStartRecordAns(self):
        phase, step = self.steps[self.currentStep]
        self.question = self.getTableAnswer()
        return {
            "type": "RECORD_GET",
            "reply": self.question["queF"],
            "table_type": self.config[phase][step]["table_type"],
            "phase": phase,
            "step": step,
            "step_desc": self.config[phase][step]["desc"]
        }
    
    def judegRecord(self, res):
        try:
            data = res["data"]
            x = []
            y = []
            if "电流" in data[0][1]["value"]:
                for it in data[1:]:
                    x.append(float(it[1]["value"]))
                    y.append(float(it[2]["value"]))
            else:
                for it in data[1:]:
                    x.append(float(it[2]["value"]))
                    y.append(float(it[1]["value"]))
            
            if res["table_type"] == "UI":
                z = []
                for xi, yi in zip(x, y):
                    z.append(yi/xi)
                mz = sum(z)/len(z)
                for zi in z:
                    if abs(zi-mz) > 5:
                        return False
            elif res["table_type"] == "IR":
                z = []
                for xi, yi in zip(x, y):
                    z.append(yi*xi)
                mz = sum(z)/len(z)
                for zi in z:
                    if abs(zi-mz) > 1:
                        return False
            return True
        except:
            return False
    
    def getOKRecordAns(self, res):
        phase, step = self.steps[self.currentStep]
        comment = {
            "type": "RECORD_OK",
            "reply": self.question["trueAnsF"],
            "table_type": self.config[phase][step]["table_type"]
        }
        return comment
    
    def getFailedRecordAns(self, res):
        comment = {
            "type": "RECORD_ER",
            "reply": self.question["falseAnsF"],
        }
        return comment
    
    
    '''
    处理仪器整理
    '''
    def step_tidyup(self, result):
        if result == None:
            return self.getStartTidyupAns()
        else:
            if self.judegTidyup(result):
                self.history = self.history + "学生完成桌面清理\n" 
                comment = self.getOKTidyupAns(result)
                self.currentStep += 1
                return comment
            else:
                self.history = self.history + "学生没有完成桌面清理\n" 
                comment = self.getFailedTidyupAns(result)
                self.currentStep += 1
                return comment

    def getStartTidyupAns(self):
        phase, step = self.steps[self.currentStep]
        self.question = self.getTableAnswer()
        return {
            "type": "TIDYUP_GET",
            "reply": self.question["queF"],
            "phase": phase,
            "step": step,
            "step_desc": self.config[phase][step]["desc"]
        }
    
    def judegTidyup(self, res):
        try:
            img = res["data"]
            w, h, c = res["w"], res["h"], res["c"]
            img = np.frombuffer(base64.b64decode(img), dtype=np.uint8).reshape(h, w, c)
            return tidy_det(img)
        except Exception:
            return False
    
    def getOKTidyupAns(self, res):
        comment = {
            "type": "TIDYUP_OK",
            "reply": self.question["trueAnsF"]
        }
        return comment
    
    def getFailedTidyupAns(self, res):
        comment = {
            "type": "TIDYUP_ER",
            "reply": self.question["falseAnsF"],
        }
        return comment


'''
测试代码
'''
if __name__ == "__main__":
    SERVER_DIR = os.path.dirname(__file__)
    file_path = os.path.join(SERVER_DIR, '1_config.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    process = ChatProcess(config)
    
    process.nextStream()
    