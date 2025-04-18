import mistune
import os
import json
import time
import base64

SERVER_DIR = os.path.dirname(__file__)

PHASE2NAME = {
        "question": "情景导入",
        "evidence": "设计思考",
        "analysis": "实验验证",
        "discussion": "总结思考",
        "evaluation": "整体评价"
}


def image_to_base64_html(image_path):
    with open(os.path.join(SERVER_DIR, "sum_pages", image_path[image_path.rfind("imgs"):]), 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    image_format = image_path.split('.')[-1].lower()
    
    html_img = f'<img src="data:image/{image_format};base64,{encoded_string}" alt="Embedded Image">'
    
    return html_img


def render_page(ai_gen, history, out_file):
  
    with open("history.json", "w", encoding="utf-8") as fin:
        fin.write(json.dumps(history, ensure_ascii=False))
        
    history_html = ""
    score_sum = {
      "1.1": { "s": 0.0, "link": ""} ,
      "1.2": { "s": 0.0, "link": ""} ,
      "1.3": { "s": 0.0, "link": ""} ,
      "2.1": { "s": 0.0, "link": ""} ,
      "2.2": { "s": 0.0, "link": ""} ,
      "2.3": { "s": 0.0, "link": ""} ,
      "3.1": { "s": 0.0, "link": ""} ,
      "3.2": { "s": 0.0, "link": ""} ,
      "4.1": { "s": 0.0, "link": ""} ,
      "4.2": { "s": 0.0, "link": ""} ,
      "5.1": { "s": 0.0, "link": ""} ,
      "5.2": { "s": 0.0, "link": ""} ,
      "6.1": { "s": 0.0, "link": ""} ,
      "7.1": { "s": 0.0, "link": ""} 
    }
    
    for his_k in history:
      his = history[his_k]
      his_t = his["type"]
      phase = his_k[:his_k.find("-")]
      step = his_k[his_k.find("-")+1:]
            
      if his_t == "START":
        history_html += f"<h3>{his['title']}</h3>\n"
      elif his_t == "QUES":
        history_html += f'<h3 id="his-{his_k}">{PHASE2NAME[phase]}阶段-{step}<h3>\n'
        his['desc'] = his['desc'].replace('\n', '<br/>')
        history_html += f"<p>{his['desc']}</p>\n"
        history_html += f"<p>回答{'正确' if his['ispass'] else '错误'}</p>\n"
        if "point" in his:
          for pk in his["point"]:
            score_sum[pk]["s"] += his["point"][pk]["get"]
            if score_sum[pk]["link"] == "":
              score_sum[pk]["link"] = f"#his-{his_k}"
      elif his_t == "CIRCUIT":
        history_html += f'<h3 id="his-{his_k}">{his["title"]}</h3>\n'
        # history_html += f'<img src="{his["img-url"]}" alt="IMG">'
        history_html += image_to_base64_html(his["img-url"])
        history_html += f"<p>电路图绘制{'正确' if his['ispass'] else '错误'}</p>\n"
        if "point" in his:
          for pk in his["point"]:
            score_sum[pk]["s"] += his["point"][pk]["get"]
            if score_sum[pk]["link"] == "":
              score_sum[pk]["link"] = f"#his-{his_k}"
      elif his_t == "CONN":
        history_html += f'<h3 id="his-{his_k}">{his["title"]}</h3>\n'
        # history_html += f'<img src="{his["img-url"]}" alt="IMG">'
        history_html += image_to_base64_html(his["img-url"])
        history_html += f"<p>电路连接{'正确' if his['ispass'] else '错误'}</p>\n"
        history_html += f"<p>滑动变阻器位置{'正确' if his['point']['2.3']['get'] > 0.1 else '错误'}</p>\n"
        history_html += f"<p>开关状态{'正确' if his['point']['2.1']['get'] > 0.1 else '错误'}</p>\n"
        if "point" in his:
          for pk in his["point"]:
            score_sum[pk]["s"] += his["point"][pk]["get"]
            if score_sum[pk]["link"] == "":
              score_sum[pk]["link"] = f"#his-{his_k}"
      elif his_t == "TABLE":
        history_html += f'<h3 id="his-{his_k}">{his["title"]}</h3>\n'
        history_html += f"<p>表格设计{'正确' if his['ispass'] else '错误'}</p>\n"
        if "point" in his:
          for pk in his["point"]:
            score_sum[pk]["s"] += his["point"][pk]["get"]
            if score_sum[pk]["link"] == "":
              score_sum[pk]["link"] = f"#his-{his_k}"
      elif his_t == "RECORD":
        history_html += f'<h3 id="his-{his_k}">{his["title"]}</h3>\n'
        history_html += f"<p>表格记录 {'正确' if his['ispass'] else '错误'}</p>\n"
        if "point" in his:
          for pk in his["point"]:
            score_sum[pk]["s"] += his["point"][pk]["get"]
            if score_sum[pk]["link"] == "":
              score_sum[pk]["link"] = f"#his-{his_k}"
      elif his_t == "TIDYUP":
        history_html += f'<h3 id="his-{his_k}">{his["title"]}</h3>\n'
        # history_html += f'<img src="{his["img-url"]}" alt="IMG">'
        history_html += image_to_base64_html(his["img-url"])
        history_html += f"<p>桌面清理 {'正确' if his['ispass'] else '错误'}</p>\n"
        if "point" in his:
          for pk in his["point"]:
            score_sum[pk]["s"] += his["point"][pk]["get"]
            if score_sum[pk]["link"] == "":
              score_sum[pk]["link"] = f"#his-{his_k}"
      elif his_t == "ZERO":
        history_html += f'<h3 id="his-{his_k}">调零</h3>\n'
        # history_html += f'<img src="{his["img-url"]}" alt="IMG">'
        history_html += image_to_base64_html(his["img-url"])
        history_html += f"<p>调零 {'正确' if his['point']['5.1']['get'] > 0 else '错误'}</p>\n"
        if "point" in his:
          for pk in his["point"]:
            score_sum[pk]["s"] += his["point"][pk]["get"]
            if score_sum[pk]["link"] == "":
              score_sum[pk]["link"] = f"#his-{his_k}"
      elif his_t == "UID":
        history_html += f'<h3 id="his-uid">绘制UI曲线图</h3>\n'
        # history_html += f'<img src="{his["img-url"]}" alt="IMG">'
        history_html += image_to_base64_html(his["img-url"])
        history_html += f"<p>曲线图 {'正确' if his['ispass'] else '错误'}</p>\n"
        if his['ispass']:
          score_sum["3.2"]["s"] += 5.0
        if score_sum["3.2"]["link"] == "":
            score_sum["3.2"]["link"] = f"#his-uid"
      elif his_t == "IRD":
        history_html += f'<h3 id="his-ird">绘制IR曲线图</h3>\n'
        # history_html += f'<img src="{his["img-url"]}" alt="IMG">'
        history_html += image_to_base64_html(his["img-url"])
        history_html += f"<p>曲线图 {'正确' if his['ispass'] else '错误'}</p>\n"
        if his['ispass']:
          score_sum["4.2"]["s"] += 5.0
        if score_sum["4.2"]["link"] == "":
            score_sum["4.2"]["link"] = f"#his-ird"
      else:
        pass
    
    score_total = 0.0
    for sk in score_sum:
      score_total += score_sum[sk]["s"]
    
    ai_gen_md = mistune.html(ai_gen)
    page = f''' 
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: "SimSun", "Microsoft YaHei", sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: #333;
                background-color: #eee;
                padding: 20px;
            }}

            h1 {{
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            }}

            h2,
            h3 {{
                color: #2c3e50;
                margin-top: 40px;
            }}

            p {{
                text-align: justify;
                background: #f9f9f9;
                padding: 10px;
                border-radius: 5px;
                border-left: 5px solid #3498db;
            }}

            .section {{
                margin-bottom: 20px;
                padding: 20px;
                background: #ecf0f1;
                border-radius: 5px;
                box-shadow: #0000007e 4px 4px 10px 0px;
                
            }}

            .suggestion {{
                background: #eaf7ea;
                padding: 10px;
                border-left: 5px solid #27ae60;
            }}

            .table {{
                display: flex;
                justify-content: center;
            }}
            
            th {{
                background-color: #247db7;
                padding: 20px;
                color: #ffffff;
            }}

            td {{
                background-color: #eeeeee;
                padding: 10px;
                border: #fff solid 1px;
            }}
            
            table th:first-child {{
                border-radius: 10px 0px 0px 0px;
            }}

            table th:last-child {{
                border-radius: 0px 10px 0px 0px;
            }}

            table tr:last-child td:first-child {{
                border-radius: 0px 0px 0px 10px;
            }}

            table tr:last-child td:last-child {{
                border-radius: 0px 0px 10px 0px;
            }}

            table {{
                background-color: #00000000;
                box-shadow: #00000066 3px 3px 8px 0px;
                overflow: hidden;
                border-radius: 10px;
            }}
            img {{
              object-fit: contain;     
              width: 100%;         
            }}
            .main {{
                margin: 0px auto;
                width: 900px;
                background-color: #fff;
                padding: 100px 50px;
                box-shadow: #00000066 3px 3px 6px 0px;
            }}
        </style>
    </head>
    <body>
        <div class="main">
        <h1>实验总结</h1>
        <center>
          <h3>实验名称：探究电阻、电压与电流的关系</h3>    
          <h3>实验时间: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}</h3>    
        </center>
        <h2>得分详情</h2>
        <div class="table">
            <table border="0" cellspacing="0" cellpadding="5">
                <thead>
                  <tr>
                    <th>一级指标</th>
                    <th>二级指标</th>
                    <th>得分情况</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td rowspan="3">1 猜想并设计实验（15%）</td>
                    <td>1.1 提出合理的猜想假设（5%）</td>
                    <td>{score_sum["1.1"]["s"]} <a href="{score_sum["1.1"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td>1.2 设计实验电路图（5%）</td>
                    <td>{score_sum["1.2"]["s"]} <a href="{score_sum["1.2"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td>1.3 设计实验表格（5%）</td>
                    <td>{score_sum["1.3"]["s"]} <a href="{score_sum["1.3"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td rowspan="3">2 电路连接（15%）</td>
                    <td>2.1 开关断开时连接电路（5%）</td>
                    <td>{score_sum["2.1"]["s"]} <a href="{score_sum["2.1"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td>2.2 正确连接电流表、电压表、电阻和滑动变阻器（5%）</td>
                    <td>{score_sum["2.2"]["s"]} <a href="{score_sum["2.2"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td>2.3 闭合电路前滑动变阻器滑片位于电阻最大位置（5%）</td>
                    <td>{score_sum["2.3"]["s"]} <a href="{score_sum["2.3"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td rowspan="2">3 探究电流与电压的关系（15%）</td>
                    <td>3.1 记录电流表示数（10%）</td>
                    <td>{score_sum["3.1"]["s"]} <a href="{score_sum["3.1"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td>3.2 绘制U-I图像（5%）</td>
                    <td>{score_sum["3.2"]["s"]} <a href="{score_sum["3.2"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td rowspan="2">4 探究电流与电阻的关系（15%）</td>
                    <td>4.1 记录电流表示数（10%）</td>
                    <td>{score_sum["4.1"]["s"]} <a href="{score_sum["4.1"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td>4.2 绘制R-I图像（5%）</td>
                    <td>{score_sum["4.2"]["s"]} <a href="{score_sum["4.2"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td rowspan="2">5 仪器检查与整理（10%）</td>
                    <td>5.1 检查实验仪器，对电流表、电压表进行调零 （5%）</td>
                    <td>{score_sum["5.1"]["s"]} <a href="{score_sum["5.1"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td>5.2 拆除电路，整理实验仪器（5%）</td>
                    <td>{score_sum["5.2"]["s"]} <a href="{score_sum["5.2"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td>6 总结归纳（20%）</td>
                    <td>6.1 总结归纳电流与电压、电阻的关系（20%）</td>
                    <td>{score_sum["6.1"]["s"]} <a href="{score_sum["6.1"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td>7 交流讨论（10%）</td>
                    <td>7.1 讨论实验环节存在的问题及改进措施或其他合理问题（10%）</td>
                    <td>{score_sum["7.1"]["s"]} <a href="{score_sum["7.1"]["link"]}">详情</a></td>
                  </tr>
                  <tr>
                    <td>总分</td>
                    <td colspan="2">{score_total}/100.0</td>
                  </tr>
                </tbody>
            </table>
        </div>
        <h2>老师评价</h2>
        <div class="section">
            {ai_gen_md}
        </div>
        <h2>附录-实验历史记录</h2>
        <div class="section">
          {history_html}
        </div>
        </div>
    </body>
    </html>

    '''

    if not os.path.exists(os.path.join(SERVER_DIR, "sum_pages")):
        os.makedirs(os.path.join(SERVER_DIR, "sum_pages"))

    with open(f"{out_file}", "w", encoding="utf-8") as fout:
        fout.write(page)
    
    return page
