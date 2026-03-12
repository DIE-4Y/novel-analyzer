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
        计算图谱中每个人物的度中心性

        Args:
            graph_data: ECharts 图谱数据

        Returns:
            度中心性字典 {name: centrality}
        """
        nodes = graph_data.get('nodes', [])
        links = graph_data.get('links', [])

        centrality = {}

        # 初始化所有人的度为 0
        for node in nodes:
            centrality[node['name']] = 0

        # 统计每个人的连接数
        for link in links:
            source = link['source']
            target = link['target']

            if source in centrality:
                centrality[source] += 1
            if target in centrality:
                centrality[target] += 1

        # 归一化（可选）
        if nodes:
            n = len(nodes)
            if n > 1:
                max_possible_degree = n - 1
                for name in centrality:
                    centrality[name] = centrality[name] / max_possible_degree

        return centrality
