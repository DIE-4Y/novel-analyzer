import networkx as nx

class CentralityCalculator:
    def __init__(self):
        pass

    def calculate_main_characters(self, characters, top_n=10):
        """
        根据人物出现次数计算度中心性，找出主角

        Args:
            characters: 人物出现次数字典 {name: count}
            top_n: 返回前 N 个主角

        Returns:
            主角列表 [(name, count), ...]
        """
        if not characters:
            return []

        # 按出现次数排序
        sorted_chars = sorted(characters.items(), key=lambda x: x[1], reverse=True)

        # 返回前 N 个
        return sorted_chars[:top_n]

    def calculate_degree_centrality(self, graph_data):
        """
        使用 NetworkX 计算图谱中每个人物的度中心性

        Args:
            graph_data: ECharts 图谱数据

        Returns:
            度中心性字典 {name: centrality}
        """
        nodes = graph_data.get('nodes', [])
        links = graph_data.get('links', [])

        if not nodes:
            return {}

        # 构建 NetworkX 图
        G = nx.Graph()

        # 添加节点
        for node in nodes:
            G.add_node(node['name'])

        # 添加边
        for link in links:
            source = link['source']
            target = link['target']
            weight = link.get('value', 1)
            G.add_edge(source, target, weight=weight)

        # 使用 NetworkX 计算度中心性（已归一化）
        degree_centrality = nx.degree_centrality(G)

        return degree_centrality

