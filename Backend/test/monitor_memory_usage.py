import psutil
import os
import requests
from test_upload import test_file_upload


def monitor_memory_usage():
    """监控内存使用情况"""

    process = psutil.Process(os.getpid())

    print("内存使用监控:")
    initial_mem = process.memory_info().rss / 1024 / 1024
    print(f"  初始内存: {initial_mem:.2f} MB")

    # 上传文件后
    test_file_upload()
    print(f"  上传后内存: {process.memory_info().rss / 1024 / 1024:.2f} MB")

    # 多次切换章节后
    for i in range(10):
        requests.get(f'http://localhost:5000/api/chapter/{i % 100}')

    print(f"  切换章节后: {process.memory_info().rss / 1024 / 1024:.2f} MB")

    mem_increase = (process.memory_info().rss / 1024 / 1024) - initial_mem
    print(f"  内存增长: {mem_increase:.2f} MB")

    if mem_increase < 100:
        print("  ✅ 内存管理: 良好")
    else:
        print("  ⚠️  内存泄漏风险: 需检查")


if __name__ == '__main__':
    monitor_memory_usage()
