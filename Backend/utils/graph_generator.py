import networkx as nx
from collections import defaultdict

class GraphGenerator:
    def __init__(self):
        pass

    def generate_chapter_graph(self, content, chapter_idx, paragraphs_info):
        """
        根据章节生成人物关系图谱数据

        Args:
            content: 小说全文内容
            chapter_idx: 当前章节索引
            paragraphs_info: 段落信息列表

        Returns:
            ECharts 格式的图谱数据
        """
        chapter_paragraphs = [
            p for p in paragraphs_info
            if p['chapter_index'] == chapter_idx
        ]

        all_characters = set()
        character_appear_count = defaultdict(int)

        for para in chapter_paragraphs:
            chars = para['characters']
            for char in chars:
                all_characters.add(char)
                character_appear_count[char] += 1

        # 如果没有人物，返回空图谱
        if not all_characters:
            return {
                'nodes': [],
                'links': [],
                'chapter_index': chapter_idx,
                'character_count': 0,
                'relation_count': 0
            }

        # 使用 NetworkX 构建共现图
        G = nx.Graph()

        # 添加所有节点
        for char in all_characters:
            G.add_node(char)

        # 添加边（段落共现原则）
        edge_weights = defaultdict(int)

        for para in chapter_paragraphs:
            chars = para['characters']
            # 同一段落中出现的人物两两连边
            for i in range(len(chars)):
                for j in range(i + 1, len(chars)):
                    char1, char2 = sorted([chars[i], chars[j]])
                    edge_key = (char1, char2)
                    edge_weights[edge_key] += 1

        # 将边添加到图中
        for (char1, char2), weight in edge_weights.items():
            G.add_edge(char1, char2, weight=weight)

        # 生成节点数据
        nodes = []
        for char in all_characters:
            # 计算人物的度（连接数）
            degree = G.degree[char]
            appear_count = character_appear_count[char]

            nodes.append({
                'name': char,
                'symbolSize': min(50, 20 + appear_count * 2),
                'value': degree,
                'appearCount': appear_count,
                'draggable': True
            })

        # 生成边数据
        links = []
        for u, v, data in G.edges(data=True):
            links.append({
                'source': u,
                'target': v,
                'value': data.get('weight', 1),
                'weight': data.get('weight', 1)
            })

        return {
            'nodes': nodes,
            'links': links,
            'chapter_index': chapter_idx,
            'character_count': len(nodes),
            'relation_count': len(links),
            'networkx_graph': G  # 保留 NetworkX 图对象供后续分析使用
        }

    def apply_faction_colors(self, graph_data, faction_colors):
        """
        为图谱应用阵营颜色

        Args:
            graph_data: 图谱数据
            faction_colors: 阵营颜色字典

        Returns:
            带颜色的图谱数据
        """
        colored_links = []
        for link in graph_data['links']:
            source = link['source']
            target = link['target']

            color = '#aaa'
            for faction_id, members in faction_colors.items():
                if source in members and target in members:
                    color = self._get_faction_color(faction_id)
                    break

            colored_links.append({
                'source': source,
                'target': target,
                'value': link['value'],
                'lineStyle': {
                    'color': color,
                    'width': min(5, 1 + link['value'] * 0.5)
                }
            })

        graph_data['links'] = colored_links

        # 移除 NetworkX 图对象（不传递给前端）
        if 'networkx_graph' in graph_data:
            del graph_data['networkx_graph']

        return graph_data

    def _get_faction_color(self, faction_id):
        """获取阵营颜色"""
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
            '#98D8C8', '#F7DC6F', '#BB8FCE', '#F1948A'
        ]
        return colors[faction_id % len(colors)]

