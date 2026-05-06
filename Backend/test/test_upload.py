# test_upload.py - 自动化测试脚本
import requests
import time


def test_file_upload():
    """测试文件上传功能"""

    # filepath = '../test_data/凡人修仙传(1-100章).txt'
    # filepath = '../test_data/凡人修仙传(1-500章).txt'
    # filepath = '../test_data/凡人修仙传(全本+番外).txt'
    filepath = '../test_data/年轮/刘伯钊.pdf'
    # filepath = 'C:/Game/【0001】年轮/人物剧本/刘伯钊.pdf'
    # filepath = '../test_data/年轮/刘伯钊.docx'

    # 测试 1: 正常 TXT 文件
    with open(filepath, 'rb') as f:
        response = requests.post(
            'http://localhost:5000/api/upload',
            files={'file': f}
        )

    assert response.status_code == 200
    data = response.json()

    # 验证返回数据结构
    assert 'success' in data
    assert 'total_chapters' in data
    assert 'chapter_titles' in data
    assert 'main_characters' in data
    assert 'graph_data' in data

    print(f"✅ 上传成功")
    print(f"   章节数: {data['total_chapters']}")
    print(f"   主角数: {len(data['main_characters'])}")
    print(f"   首章人物: {data['graph_data']['character_count']}")
    print(f"   首章关系: {data['graph_data']['relation_count']}")

    return data


if __name__ == '__main__':
    test_file_upload()
