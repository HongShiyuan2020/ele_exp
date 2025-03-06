import json
import os
# from weasyprint import HTML # type: ignore
import pdfkit


def json_to_pdf(json_data, pdf_file):
    try:
        # 解析 JSON 数据
        student_answer = json_data.get("学生回答情况", "暂无数据")
        overall_eval = json_data["生成评价"]["overall_evaluation"]
        phase_eval = json_data["生成评价"].get("phase_evaluation", {})
        suggestions = json_data["生成评价"].get("improvement_suggestions", [])

        # 处理换行：\n 替换为 <br>，并按段落包裹
        formatted_answer = "<br>".join(student_answer.split("\n"))

        # 生成 HTML 内容（用于进一步生成PDF）
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: "SimSun", "Microsoft YaHei", sans-serif;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #333;
                    background-color: #fff;
                    padding: 20px;
                }}
                h1 {{ text-align: center; font-size: 24px; font-weight: bold; }}
                h2, h3 {{ color: #2c3e50; margin-top: 20px; }}
                p {{
                    text-align: justify;
                    background: #f9f9f9;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 5px solid #3498db;
                }}
                .section {{ margin-bottom: 20px; padding: 10px; background: #ecf0f1; border-radius: 5px; }}
                .suggestion {{ background: #eaf7ea; padding: 10px; border-left: 5px solid #27ae60; }}
            </style>
        </head>
        <body>
            <h1>实验总结</h1>
            <h2>老师评价</h2>
            <h3>总体评价</h3>
            <p><b>Summary:</b> {overall_eval.get("summary", "暂无数据")}</p>
            <p><b>Score:</b> {overall_eval.get("score", "暂无数据")} / {overall_eval.get("max_score", "暂无数据")}</p>

            <h3>阶段评价</h3>
        """

        # 添加阶段评价
        for phase, details in phase_eval.items():
            html_content += f"<div class='section'><h4>{phase} 阶段</h4>"
            performance = details.get("表现分析", {})
            evaluation = details.get("评价", "")

            for step, description in performance.items():
                html_content += f"<p><b>{step}:</b> {description}</p>"

            html_content += f"<p><b>评价:</b> {evaluation}</p></div>"

        # 添加提升建议
        html_content += "<h2>提升建议</h2>"
        for suggestion in suggestions:
            html_content += f"<div class='suggestion'><p><b>{suggestion.get('title', '暂无标题')}:</b> {suggestion.get('details', '暂无详情')}</p></div>"

        html_content += "</body></html>"

        print("OK")
        
        # pdfkit.from_string(html_content, pdf_file)
        # 返回生成pdf的绝对路径
        with open(pdf_file, "w", encoding="utf-8") as fout:
            fout.write(html_content)
        print(f"文件已生成：{pdf_file}")
        abs_pdf_path = os.path.abspath(pdf_file)
        return abs_pdf_path

    except Exception as e:
        print(f"PDF 生成失败: {e}")

if __name__ == "__main__":
    obj = []
    with open("backend/answer.json", "r", encoding="utf-8") as fin:
        obj = json.load(fin)
        
    json_to_pdf(obj, "exm.html")