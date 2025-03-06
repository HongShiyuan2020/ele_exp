from openai import OpenAI
import json
import random
import base64
import numpy as np
import os
from utility3 import tidy_det, conn_det, sr_det_ans_final

class APIGetException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


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
        self.issr = False
        self.connecting = False
        self.client = OpenAI(api_key='sk-4vj3NYKrgqfUfHSDVD4xkiuOuBpOlo6jGY0kWiq6ioUXswoC', 
                base_url="https://api.hunyuan.cloud.tencent.com/v1")
        # self.client = OpenAI(api_key='sk-OWwbeu95SJyl88LXVaN4WWq3SuPHrnrLGAhSdU0tZJMiYiDv',
        #         base_url="https://api.planetzero.live/v1/")

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
                # model="gpt-4-turbo",
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

        print(self.currentStep)
        print(self.answer_times)
        print(result)  
        phase, step = self.steps[self.currentStep]
        input_t = self.config[phase][step]["format"]["input"]

        if input_t == "":
            return self.step_question(result)
        elif input_t == "table":
            return self.step_table(result)
        elif input_t == "circuit":
            return self.step_circuit(result)
        elif input_t == "connection":
            self.connecting = True
            return self.step_connection(result)
        elif input_t == "record":
            return self.step_record(result)
        elif input_t == "tidyUp":
            return self.step_tidyup(result)
        elif input_t == "evaluation":
            return self.step_evaluation(result)


    def streamOtherOK(self):
        pahse, step = self.steps[self.currentStep]
        prompt = self.config[pahse][step]["promptTrue"]
        if self.connecting:
            prompt += "，当前为电路连接判断阶段，生成的评价不要提连接的具体情况。"
            if self.issr:
                prompt += "并且，当前的滑动变阻器处于最大阻值状态，满足实验要求，在生成的评价中要简要提及。"
            else:
                prompt += "并且，当前的滑动变阻器不处于最大阻值状态，不满足实验要求，在生成的评价中要简要提及。"
        res = self.getTans(prompt, "")
        self.currentStep += 1
        try:
            for chunk in res:
                cont = chunk.choices[0].delta.content
                yield cont
        except:
            raise APIGetException()

    def streamOtherErr(self):
        pahse, step = self.steps[self.currentStep]
        prompt = self.config[pahse][step]["promptFalse"]
        if self.connecting:
            prompt += "，当前为电路连接判断阶段，生成的评价不要提连接的具体情况。"
            if self.issr:
                prompt += "并且，当前的滑动变阻器处于最大阻值状态，满足实验要求，在生成的评价要在另外一句中简要提及。"
            else:
                prompt += "并且，当前的滑动变阻器不处于最大阻值状态，不满足实验要求，在生成的评价要在另外一句中简要提及。"
        res = self.getTans(prompt, "")
        self.currentStep += 1
        try:
            for chunk in res:
                cont = chunk.choices[0].delta.content
                yield cont
        except:
            raise APIGetException()

    def streamOtherTip(self):
        pahse, step = self.steps[self.currentStep]
        prompt = self.config[pahse][step]["prompt"]
        res = self.getTans(prompt, "")
        try:
            for chunk in res:
                cont = chunk.choices[0].delta.content
                yield cont
        except:
            raise APIGetException()


    def streamGetQuesOK(self):
        prompt = f'当前问题为：\n{self.question["question"]}\n其答案为: {self.question["key"]}\n该学生回答的答案正确，请以温和的语气给出评价，并对正确答案作出解析。注意语言要简短，且为不带任何格式的纯文本'
        res = self.getTans(prompt, "")
        self.currentStep += 1
        self.answer_times = 0
        try:
            for chunk in res:
                cont = chunk.choices[0].delta.content
                self.question["question"] += cont
                yield cont
        except:
            raise APIGetException()

    def streamGetQuesRetry(self):
        prompt = f'当前问题为：\n{self.question["question"]}\n其答案为: {self.question["key"]}\n该学生回答的答案错误，错误选项为{self.question["w_ans"]}，请以温和的语气给出评价，对学生回答的答案作出解析并提醒他再试一次。注意语言要简短，且为不带任何格式的纯文本'
        res = self.getTans(prompt, "")
        self.answer_times += 1
        try:
            for chunk in res:
                cont = chunk.choices[0].delta.content
                self.question["question"] += cont
                yield cont
        except:
            raise APIGetException()
        
    def streamGetQuesEr(self):
        prompt = f'当前问题为：\n{self.question["question"]}\n其答案为: {self.question["key"]}\n该学生已经两次回答错误，请以温和的语气给出评价，告诉他正确答案并给出解析，解析中不要给出正确答案，一定不要给出正确答案。注意语言要简短，且为不带任何格式的纯文本'
        res = self.getTans(prompt, "")
        self.currentStep += 1
        self.answer_times = 0
        try:
            for chunk in res:
                cont = chunk.choices[0].delta.content
                self.question["question"] += cont
                yield cont
        except:
            raise APIGetException()

    def streamGetQuestion(self):
        phase, step = self.steps[self.currentStep]
        desc1 = self.config[phase]['desc1']
        desc2 = self.config[phase][step]["desc"]            
        example = self.config[phase][step]["prompt"]["example"]
        ques = example["question"]
        options = example["options"]
        ans = example["answer"]
        gen_key = chr(random.randint(0, 3) + ord('A'))
        
        prompt = f"{desc1}，当前步骤的目的为{desc2}，所出的问题要满足目的，且尽量容易理解\n例如：\n{ques}\n"
        for key in options:
            prompt += f"{key} {options[key]}\n"
        prompt += f"在我给出的例子中正确答案为：{ans}\n"
        prompt += f"这是我的教学目标，请你为我生成提问和答案选项，只要问题和选项注意只要输出这两项，不要任何提示文本，不要出现任何和功率相关的内容，遵循我给的样例，不要生成任何评价。在你生成的问题中，请确保{gen_key}选项为正确答案, 注意一定要保证{gen_key}选项为正确选项，再次强调一定要保证{gen_key}选项为正确选项"

        res = self.getTans(prompt, "")
        self.question = {
            "key": gen_key,
            "question": ""
        }
        
        try:
            for chunk in res:
                cont = chunk.choices[0].delta.content
                self.question["question"] += cont
                yield cont
        except:
            raise APIGetException()
        
 
    def setCurrentStep(self, idx):
        if idx < 0 and idx >= self.stepCount:
            print("Idx Invaild!")
        
        self.currentStep = idx
        self.question = None
        self.answer_times = 0
          
    def startStepByIdx(self, idx):
        self.setCurrentStep(idx)
        return self.next()

    '''
    :处理普通问答
    '''
    def step_question(self, result):
        if self.answer_times == 0:   
            if result != None:                              # 学生第一次回答问题
                if self.judge_answer(result) == True:
                    comment = self.getOKComment()
                    return comment
                else:
                    return self.getRetryComment(result)
            else:                                           # 学生没有回答这个问题且回答次数为0，说明还没给出问题，大模型生成问题，发送给学生
                self.question = self.getQuestion()
                return self.question
        else:
            if result != None:                              # 学生第二次回答问题
                if self.judge_answer(result) == True:
                    comment = self.getOKComment()
                    return comment
                else:
                    comment = self.getFailedComment()
                    return comment
            else:
                comment = self.getFailedComment()
                return comment

    def judge_answer(self, res):
        try:
            return res["answer"] == self.question["key"]
        except:
            return False

    def getOKComment(self):
        comment = {
            "type": "QUES_OK", 
        }
        return comment

    def getRetryComment(self, res):
        self.question["w_ans"] = res["answer"]
        comment = {
            "type": "QUES_RETRY",
        }
        return comment

    def getQuestion(self):
        phase, step = self.steps[self.currentStep]
        return {
            "type": "QUES_GET",
            "phase": phase,
            "step": step,
        }

    def getFailedComment(self):
        comment = {
            "type": "QUES_FAILED",
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
                return self.getTableOK()   
            else:
                return self.getTableErr()               

    def getTableTip(self):
        phase, step = self.steps[self.currentStep]
        return {
            "type": "TABLE_GET",
            "table_type": self.config[phase][step]["table_type"],
            "phase": phase,
            "step": step,
        }

    def getTableOK(self):
        comment = {
            "type": "TABLE_OK",
        }
        return comment

    def getTableErr(self):
        phase, step = self.steps[self.currentStep]
        comment = {
            "type": "TABLE_ER",
            "table": self.config[phase][step]["right_table"]
        }
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
                return self.getCircuitOK()   
            else:
                return self.getCircuitErr() 
    
    def getCircuitTip(self):
        phase, step = self.steps[self.currentStep]
        return {
            "type": "CIRCUIT_GET",
            "phase": phase,
            "step": step,
        }

    def judgeCircuit(self, res):
        try :
            return False
            return res["answer"] == "OK"
        except:
            return False

    def getCircuitOK(self):
        comment = {
            "type": "CIRCUIT_OK",
        }
        return comment

    def getCircuitErr(self):
        comment = {
            "type": "CIRCUIT_ER",
        }
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
                return self.getOKConnection()   
            else:
                return self.getErrConnection() 
    
    def getConnectionTip(self):
        phase, step = self.steps[self.currentStep]
        return {
            "type": "CONN_GET",
            "phase": phase,
            "step": step,
        }

    ## HSY
    def judgeConnection(self, res):
        try :
            img = res["data"]
            w, h, c = res["w"], res["h"], res["c"]
            img = np.frombuffer(base64.b64decode(img), dtype=np.uint8).reshape(h, w, c)
            self.issr = sr_det_ans_final(img)
            res = conn_det(img)
            return res
        except:
            return False

    def getOKConnection(self):
        comment = {
            "type": "CONN_OK",
        }
        return comment

    def getErrConnection(self):
        comment = {
            "type": "CONN_ER",
        }
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
                return comment
            else:
                comment = self.getFailedRecordAns(result)
                return comment
    
    def getStartRecordAns(self):
        phase, step = self.steps[self.currentStep]
        return {
            "type": "RECORD_GET",
            "table_type": self.config[phase][step]["table_type"],
            "phase": phase,
            "step": step,
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
            "table_type": self.config[phase][step]["table_type"]
        }
        return comment
    
    def getFailedRecordAns(self, res):
        comment = {
            "type": "RECORD_ER",
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
                comment = self.getOKTidyupAns(result)
                return comment
            else:
                comment = self.getFailedTidyupAns(result)
                return comment

    def getStartTidyupAns(self):
        phase, step = self.steps[self.currentStep]
        return {
            "type": "TIDYUP_GET",
            "phase": phase,
            "step": step,
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
        }
        return comment
    
    def getFailedTidyupAns(self, res):
        comment = {
            "type": "TIDYUP_ER",
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
    process.setCurrentStep(3)
    process.streamGetQuestion()
    