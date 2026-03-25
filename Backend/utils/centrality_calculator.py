import networkx as nx

class CentralityCalculator:
    def __init__(self):
        pass

    def calculate_main_characters(self, characters, paragraphs_info=None, top_n=10):
        """
        使用 NetworkX 度中心性计算主角

        Args:
            characters: 人物出现次数字典 {name: count}
            paragraphs_info: 段落信息列表（用于构建共现图）
            top_n: 返回前 N 个主角

        Returns:
            主角列表 [(name, score), ...]
        """
        if not characters:
            return []

        # 如果没有段落信息，直接按出现次数排序
        if paragraphs_info is None:
            sorted_chars = sorted(characters.items(), key=lambda x: x[1], reverse=True)
            return sorted_chars[:top_n]

        # 构建全文共现图
        G = self._build_full_graph(paragraphs_info)

        if G.number_of_nodes() == 0:
            # 如果图为空，按出现次数排序
            sorted_chars = sorted(characters.items(), key=lambda x: x[1], reverse=True)
            return sorted_chars[:top_n]

        # 使用 NetworkX 计算度中心性
        degree_centrality = nx.degree_centrality(G)

        # 结合出现次数和度中心性进行排序
        character_scores = []
        for name, count in characters.items():
            centrality_score = degree_centrality.get(name, 0)
            # 综合得分：度中心性权重 70%，出现次数权重 30%
            normalized_count = count / max(characters.values()) if characters else 0
            combined_score = 0.7 * centrality_score + 0.3 * normalized_count
            character_scores.append((name, combined_score))

        # 按综合得分排序
        character_scores.sort(key=lambda x: x[1], reverse=True)

        return character_scores[:top_n]

    def _build_full_graph(self, paragraphs_info):
        """
        根据段落信息构建全文共现图

        Args:
            paragraphs_info: 段落信息列表

        Returns:
            NetworkX 图对象
        """
        G = nx.Graph()

        # 统计边的权重
        edge_weights = {}

        for para_info in paragraphs_info:
            chars = para_info['characters']

            # 同一段落中的人物两两连边
            for i in range(len(chars)):
                for j in range(i + 1, len(chars)):
                    char1, char2 = sorted([chars[i], chars[j]])
                    edge_key = (char1, char2)
                    edge_weights[edge_key] = edge_weights.get(edge_key, 0) + 1

        # 添加所有节点
        all_chars = set()
        for para_info in paragraphs_info:
            all_chars.update(para_info['characters'])

        G.add_nodes_from(all_chars)

        # 添加边
        for (char1, char2), weight in edge_weights.items():
            G.add_edge(char1, char2, weight=weight)

        return G

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

