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

        # 构建邻接表（只保留高频互动）
        adjacency = defaultdict(set)

        for link in links:
            source = link['source']
            target = link['target']
            weight = link.get('value', 1)

            # 只有互动次数超过阈值才认为是同一阵营
            if weight >= self.threshold:
                adjacency[source].add(target)
                adjacency[target].add(source)

        # 使用并查集或 DFS 找出连通分量（阵营）
        factions = {}
        visited = set()
        faction_id = 0

        all_characters = {node['name'] for node in nodes}

        for character in all_characters:
            if character not in visited:
                # 从该人物开始 DFS，找出所有连通的人物
                faction_members = self._dfs_faction(character, adjacency, visited)

                # 只有阵营人数>=2 才分配颜色
                if len(faction_members) >= 2:
                    factions[faction_id] = faction_members
                    faction_id += 1
                else:
                    # 单独的人物也标记为一个阵营（用于后续处理）
                    factions[faction_id] = faction_members
                    faction_id += 1

        return factions

    def _dfs_faction(self, start_node, adjacency, visited):
        """使用 DFS 找出连通的所有人物"""
        faction = []
        stack = [start_node]

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                faction.append(node)

                # 添加相邻节点
                for neighbor in adjacency[node]:
                    if neighbor not in visited:
                        stack.append(neighbor)

        return faction
