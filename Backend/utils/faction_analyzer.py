import networkx as nx
from collections import defaultdict

class FactionAnalyzer:
    def __init__(self, threshold=2):
        """
        初始化阵营分析器

        Args:
            threshold: 互动阈值，超过此值认为在同一阵营
        """
        self.threshold = threshold

    def analyze_factions(self, graph_data):
        """
        根据互动关系划分阵营

        Args:
            graph_data: 图谱数据（包含 nodes 和 links）

        Returns:
            阵营字典 {faction_id: [character_names]}
        """
        links = graph_data.get('links', [])
        nodes = graph_data.get('nodes', [])

        if not nodes:
            return {}

        # 使用 NetworkX 构建图
        G = nx.Graph()

        # 添加所有节点
        for node in nodes:
            G.add_node(node['name'])

        # 添加边（只保留高频互动）
        for link in links:
            source = link['source']
            target = link['target']
            weight = link.get('value', 1)

            # 只有互动次数超过阈值才添加边
            if weight >= self.threshold:
                G.add_edge(source, target, weight=weight)

        # 使用 NetworkX 的连通分量算法找出阵营
        factions = {}
        faction_id = 0

        # connected_components 返回所有连通分量
        for component in nx.connected_components(G):
            faction_members = list(component)

            # 只有阵营人数>=2 才分配颜色
            if len(faction_members) >= 2:
                factions[faction_id] = faction_members
                faction_id += 1
            else:
                # 单独的人物也标记为一个阵营
                factions[faction_id] = faction_members
                faction_id += 1

        return factions

