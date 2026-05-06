import requests

from Backend.test.test_upload import test_file_upload


def test_character_quotes():
    """测试人物语录检索"""
    
    # 先上传文件
    upload_response = test_file_upload()
    
    # 获取主角列表
    main_chars = upload_response['main_characters']
    top_character = main_chars[0][0]  # 取第一名
    
    # 测试语录检索
    response = requests.get(
        f'http://localhost:5000/api/character/{top_character}'
    )
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"人物: {data['character_name']}")
    print(f"语录数: {len(data['quotes'])}")
    
    if data['quotes']:
        print(f"示例语录:")
        for i, quote in enumerate(data['quotes'][:3]):
            print(f"  {i+1}. {quote['text'][:50]}...")
    
    # 验证数据结构
    for quote in data['quotes']:
        assert 'text' in quote
        assert 'paragraph_index' in quote


if __name__ == '__main__':
    test_character_quotes()
