import requests


def test_faction_analysis():
    """测试阵营划分合理性"""

    response = requests.get('http://localhost:5000/api/chapter/0')
    data = response.json()

    nodes = data['graph_data']['nodes']

    # 统计各阵营人数
    factions = {}
    for node in nodes:
        faction_id = node.get('factionId', -1)
        faction_name = node.get('factionName', '未知')

        if faction_id not in factions:
            factions[faction_id] = {
                'name': faction_name,
                'members': []
            }
        factions[faction_id]['members'].append(node['name'])

    print("阵营分布:")
    for fid, info in sorted(factions.items()):
        print(f"  {info['name']}: {len(info['members'])} 人")
        print(f"    成员: {', '.join(info['members'][:5])}...")

    # 验证合理性
    assert len(factions) > 0, "至少应有一个阵营"

    # 检查是否有孤立节点
    isolated = [f for f in factions.values() if len(f['members']) == 1]
    print(f"\n孤立人物数: {len(isolated)}")


if __name__ == '__main__':
    test_faction_analysis()
