from graphviz import Digraph


# 创建一个有向图对象
dot = Digraph(comment='流程图示例')

# 添加节点
dot.node('A', '开始')
dot.node('B', '步骤1')
dot.node('C', '步骤2')
dot.node('D', '结束')

# 添加边
dot.edges(['AB', 'BC', 'CD'])

# 生成流程图并显示
dot.render('test-output/流程图示例.gv', view=True)