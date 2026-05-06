import os
import time
import statistics
import requests
from Backend.test.test_upload import test_file_upload


def benchmark_performance():
    """性能基准测试"""

    results = {
        'upload_time': [],
        'chapter_load_time': [],
        'quote_retrieval_time': []
    }

    # 测试 1: 文件上传时间
    print("=" * 50)
    print("测试 1: 文件上传与预处理")
    print("=" * 50)

    start = time.time()
    upload_response = test_file_upload()
    upload_time = time.time() - start
    results['upload_time'].append(upload_time)

    # filepath = '../test_data/凡人修仙传(1-100章).txt'
    filepath = '../test_data/年轮/刘伯钊.pdf'
    print(f"⏱️  上传耗时: {upload_time:.2f} 秒")
    print(f"   文件大小: {os.path.getsize(filepath) / 1024:.1f} KB")
    print(f"   处理速度: {os.path.getsize(filepath) / 1024 / upload_time:.1f} KB/s")

    # 测试 2: 章节加载时间
    print("\n" + "=" * 50)
    print("测试 2: 章节图谱加载")
    print("=" * 50)

    total_chapters = upload_response['total_chapters']
    test_chapters = [0, total_chapters // 2, total_chapters - 1]

    for ch_idx in test_chapters:
        start = time.time()
        requests.get(f'http://localhost:5000/api/chapter/{ch_idx}')
        load_time = time.time() - start
        results['chapter_load_time'].append(load_time)

        print(f"   第 {ch_idx + 1} 章: {load_time:.2f} 秒")

    avg_load = statistics.mean(results['chapter_load_time'])
    print(f"   平均加载时间: {avg_load:.2f} 秒")

    # 测试 3: 语录检索时间
    print("\n" + "=" * 50)
    print("测试 3: 人物语录检索")
    print("=" * 50)

    main_char = upload_response['main_characters'][0][0]

    for _ in range(5):  # 测试 5 次取平均
        start = time.time()
        requests.get(f'http://localhost:5000/api/character/{main_char}')
        retrieval_time = time.time() - start
        results['quote_retrieval_time'].append(retrieval_time)

    avg_retrieval = statistics.mean(results['quote_retrieval_time'])
    print(f"   平均检索时间: {avg_retrieval:.3f} 秒")

    # 性能评级
    print("\n" + "=" * 50)
    print("性能评级")
    print("=" * 50)

    if upload_time < 10:
        print("✅ 上传速度: 优秀")
    elif upload_time < 30:
        print("⚠️  上传速度: 良好")
    else:
        print("❌ 上传速度: 需优化")

    if avg_load < 1:
        print("✅ 章节加载: 优秀")
    elif avg_load < 3:
        print("⚠️  章节加载: 良好")
    else:
        print("❌ 章节加载: 需优化")

    if avg_retrieval < 0.5:
        print("✅ 语录检索: 优秀")
    elif avg_retrieval < 1:
        print("⚠️  语录检索: 良好")
    else:
        print("❌ 语录检索: 需优化")


if __name__ == '__main__':
    benchmark_performance()
