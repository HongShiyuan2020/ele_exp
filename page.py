import mistune



ai_gen = '''
根据学生的实验过程记录和评分细则，我们可以对学生的表现进行如下分析：

1. 猜想并设计实验：
   - 学生在提出合理的猜想假设时选择了错误的选项，未能正确理解电热丝的电学量变化，未得分。
   - 学生成功设计了实验电路图，得分。
   - 学生成功设计了实验表格，得分。

2. 电路连接：
   - 学生在连接电路时开关断开，得分。
   - 学生在连接电路时将滑动变阻器移动到最大阻值，得分。
   - 学生连接电路时电流表和电压表连接错误，未得分。

3. 探究关系：
   - 学生成功记录了电流与电压的三组数据，但绘制的U-I图像存在问题，部分得分。
   - 学生记录的电流与电阻的数据存在问题，且绘制的图像有误，未得分。

4. 仪器检查与整理：
   - 学生没有检查仪器，对电流表、电压表进行调零，未得分。
   - 学生在整理实验仪器时存在问题，未得分。

5. 总结归纳：
   - 学生在总结电流与电压、电阻关系时选择了错误的选项，未得分。

6. 交流讨论：
   - 学生未能提出合理的实验问题或改进措施，未得分。

从整体来看，学生在实验设计和电路连接的部分表现较好，但在数据记录、图像绘制和结论总结方面存在明显不足。学生在选择答案时多次出现错误，可能是由于对电学概念理解不够深入，或者对实验步骤的逻辑关系不够清晰。

科学核心素养评价：

1. 科学观念：学生对电学基本概念的理解不够准确，需加强基础知识的学习。
2. 科学思维：学生在实验设计中表现出一定的思维能力，但在数据分析和结论总结时缺乏理性思考。
3. 科学探究：学生在动手实践中表现出一定的能力，但在数据记录和分析中需要更多指导。
4. 态度与责任：学生在实验过程中表现出一定的责任感，但在整理仪器和总结归纳时需更加认真。

建议：学生应加强对电学基础知识的学习，特别是电流、电压和电阻之间的关系。同时，学生应在实验过程中多进行反思，确保每一步操作的准确性，并在总结时进行全面分析。通过更多的实践和讨论，学生可以提高科学思维和探究能力。
'''
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
                <td></td>
              </tr>
              <tr>
                <td>1.2 设计实验电路图（5%）</td>
                <td></td>
              </tr>
              <tr>
                <td>1.3 设计实验表格（5%）</td>
                <td></td>
              </tr>
              <tr>
                <td rowspan="3">2 电路连接（15%）</td>
                <td>2.1 开关断开时连接电路（5%）</td>
                <td></td>
              </tr>
              <tr>
                <td>2.2 正确连接电流表、电压表、电阻和滑动变阻器（5%）</td>
                <td></td>
              </tr>
              <tr>
                <td>2.3 闭合电路前滑动变阻器滑片位于电阻最大位置（5%）</td>
                <td></td>
              </tr>
              <tr>
                <td rowspan="2">3 探究电流与电压的关系（15%）</td>
                <td>3.1 记录电流表示数（10%）</td>
                <td></td>
              </tr>
              <tr>
                <td>3.2 绘制U-I图像（5%）</td>
                <td></td>
              </tr>
              <tr>
                <td rowspan="2">4 探究电流与电阻的关系（15%）</td>
                <td>4.1 记录电流表示数（10%）</td>
                <td></td>
              </tr>
              <tr>
                <td>4.2 绘制R-I图像（5%）</td>
                <td></td>
              </tr>
              <tr>
                <td rowspan="2">5 仪器检查与整理（10%）</td>
                <td>4.1 检查实验仪器，对电流表、电压表进行调零 （5%）</td>
                <td></td>
              </tr>
              <tr>
                <td>4.2 拆除电路，整理实验仪器（5%）</td>
                <td></td>
              </tr>
              <tr>
                <td>5 总结归纳（20%）</td>
                <td>5.1 总结归纳电流与电压、电阻的关系（20%）</td>
                <td></td>
              </tr>
              <tr>
                <td>6 交流讨论（10%）</td>
                <td>6.1 讨论实验环节存在的问题及改进措施或其他合理问题（10%）</td>
                <td></td>
              </tr>
              <tr>
                <td>总分</td>
                <td colspan="2"></td>
              </tr>
            </tbody>
        </table>
    </div>
    <h2>老师评价</h2>
    <div class="section">
        {ai_gen_md}
    </div>
    <h2>附录-实验历史记录</h2>
    <div class="section"></div>
    </div>
</body>
</html>

'''

with open("render.html", "w", encoding="utf-8") as fout:
    fout.write(page)