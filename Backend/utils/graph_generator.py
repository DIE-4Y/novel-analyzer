import numpy as np
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

        all_characters = {}
        character_appear_count = defaultdict(int)

        for para in chapter_paragraphs:
            chars = para['characters']
            for char in chars:
                all_characters[char] = True
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

        # 构建共现矩阵（段落共现原则）
        cooccurrence_matrix = defaultdict(lambda: defaultdict(int))

        for para in chapter_paragraphs:
            chars = para['characters']
            for i in range(len(chars)):
                for j in range(i + 1, len(chars)):
                    char1, char2 = sorted([chars[i], chars[j]])
                    cooccurrence_matrix[char1][char2] += 1

        # 生成节点数据
        nodes = []
        character_list = list(all_characters.keys())

        for char in character_list:
            degree = sum(1 for other in cooccurrence_matrix[char] if cooccurrence_matrix[char][other] > 0)
            degree += sum(1 for other_char in cooccurrence_matrix
                         if char in cooccurrence_matrix[other_char] and cooccurrence_matrix[other_char][char] > 0)

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
        processed_pairs = set()

        for char1 in cooccurrence_matrix:
            for char2, weight in cooccurrence_matrix[char1].items():
                pair = tuple(sorted([char1, char2]))
                if pair not in processed_pairs and weight > 0:
                    links.append({
                        'source': char1,
                        'target': char2,
                        'value': weight,
                        'weight': weight
                    })
                    processed_pairs.add(pair)

        return {
            'nodes': nodes,
            'links': links,
            'chapter_index': chapter_idx,
            'character_count': len(nodes),
            'relation_count': len(links)
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
        return graph_data

    def _get_faction_color(self, faction_id):
        """获取阵营颜色"""
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
            '#98D8C8', '#F7DC6F', '#BB8FCE', '#F1948A'
        ]
        return colors[faction_id % len(colors)]

