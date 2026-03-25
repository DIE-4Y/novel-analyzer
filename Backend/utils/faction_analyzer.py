import networkx as nx
import community as community_louvain

class FactionAnalyzer:
    def __init__(self, threshold=2, use_louvain=True):
        """
        初始化阵营分析器

        Args:
            threshold: 互动阈值，超过此值认为在同一阵营
            use_louvain: 是否使用 Louvain 社区发现算法
        """
        self.threshold = threshold
        self.use_louvain = use_louvain

    def analyze_factions(self, graph_data):
        """
        使用 NetworkX 社区发现算法划分阵营

        Args:
            graph_data: 图谱数据（包含 nodes 和 links）

        Returns:
            阵营字典 {faction_id: [character_names]}
        """
        links = graph_data.get('links', [])
        nodes = graph_data.get('nodes', [])

        if not nodes:
            return {}

        # 构建 NetworkX 图
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

        # 如果图是空的或没有边，返回每个角色独立的阵营
        if G.number_of_edges() == 0:
            factions = {}
            for idx, node in enumerate(nodes):
                factions[idx] = [node['name']]
            return factions

        # 使用社区发现算法
        if self.use_louvain:
            factions = self._analyze_with_louvain(G)
        else:
            factions = self._analyze_with_connected_components(G)

        return factions

    def _analyze_with_louvain(self, G):
        """
        使用 Louvain 社区发现算法划分阵营

        Args:
            G: NetworkX 图对象

        Returns:
            阵营字典
        """
        try:
            # 使用 Louvain 算法进行社区划分
            partition = community_louvain.best_partition(G, weight='weight')

            # 将社区反转：community_id -> [members]
            factions = {}
            for node, community_id in partition.items():
                if community_id not in factions:
                    factions[community_id] = []
                factions[community_id].append(node)

            return factions

        except Exception as e:
            print(f"Louvain 算法失败，回退到连通分量算法：{e}")
            return self._analyze_with_connected_components(G)

    def _analyze_with_connected_components(self, G):
        """
        使用连通分量算法划分阵营（备用方案）

        Args:
            G: NetworkX 图对象

        Returns:
            阵营字典
        """
        factions = {}
        faction_id = 0

        # 使用 NetworkX 的连通分量算法
        for component in nx.connected_components(G):
            faction_members = list(component)
            factions[faction_id] = faction_members
            faction_id += 1

        return factions

