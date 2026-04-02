import os

class Config:
    # 上传文件夹路径（改回项目当前目录的 uploads 文件夹）
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

    # 最大上传文件大小 16MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # HanLP 配置
    HANLP_CUSTOM_DICT = True
    HANLP_ANALYZER = "Perceptron"  # 或 "CRF"

    # 人物提取阈值
    CHARACTER_THRESHOLD = 3  # 出现次数少于 3 次的人物不显示

    # 阵营分析参数
    FACTION_THRESHOLD = 2  # 互动次数超过此值认为在同一阵营

    # 度中心性计算
    TOP_MAIN_CHARACTERS = 10  # 返回前 10 个主角

    # 自定义词典文件路径
    CUSTOM_DICT_FILE = os.path.join(os.path.dirname(__file__), 'custom_dict.txt')

    # 临时文件保留时间（秒），默认 1 小时
    TEMP_FILE_LIFETIME = 3600

