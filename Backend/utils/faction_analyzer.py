import networkx as nx
import community as community_louvain

class FactionAnalyzer:
    def __init__(self, threshold=1, use_louvain=True):
        """
        初始化阵营分析器

        Args:
            threshold: 互动阈值，超过此值认为在同一阵营（设为 1 表示只要有互动就在同一阵营）
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

        # 添加边（只要有互动就添加，不设置阈值）
        for link in links:
            source = link['source']
            target = link['target']
            weight = link.get('value', 1)

            # 只要有互动就添加边（threshold=1）
            if weight >= self.threshold:
                G.add_edge(source, target, weight=weight)

        # 使用社区发现算法
        if self.use_louvain and G.number_of_edges() > 0:
            factions = self._analyze_with_louvain(G)
        else:
            # 如果没有边，所有人都是独立阵营
            factions = {}
            for idx, node in enumerate(nodes):
                factions[idx] = [node['name']]
            return factions

        # 确保所有人都在某个阵营中（包括孤立节点）
        all_characters = {node['name'] for node in nodes}
        characters_in_factions = set()
        for members in factions.values():
            characters_in_factions.update(members)

        # 找出不在任何阵营中的人物（孤立节点）
        isolated_chars = all_characters - characters_in_factions

        # 为每个孤立人物分配一个独立的阵营
        if isolated_chars:
            max_faction_id = max(factions.keys()) + 1 if factions else 0
            for char in isolated_chars:
                factions[max_faction_id] = [char]
                max_faction_id += 1

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
            # 如果图为空或没有边，每个人都是独立阵营
            if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
                factions = {}
                for idx, node in enumerate(G.nodes()):
                    factions[idx] = [node]
                return factions

            # 使用 Louvain 算法进行社区划分
            # resolution 参数控制社区大小：值越小，社区越大（推荐的社区越少）
            partition = community_louvain.best_partition(
                G,
                weight='weight',
                resolution=0.8  # 降低 resolution，让算法倾向于产生更少、更大的社区
            )

            # 将社区反转：community_id -> [members]
            factions = {}
            for node, community_id in partition.items():
                if community_id not in factions:
                    factions[community_id] = []
                factions[community_id].append(node)

            # 优化：如果社区数量太多（超过节点数的一半），尝试降低 resolution 重新计算
            num_communities = len(factions)
            num_nodes = G.number_of_nodes()

            if num_communities > num_nodes * 0.8:
                # 社区太多了，重新计算，使用更小的 resolution
                partition = community_louvain.best_partition(
                    G,
                    weight='weight',
                    resolution=0.5  # 更小的值，产生更大的社区
                )

                # 重新构建 factions
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

