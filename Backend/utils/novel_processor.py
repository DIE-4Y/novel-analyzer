import os
import re
from tqdm import tqdm
from pyhanlp import *

class NovelProcessor:
    def __init__(self, analyzer_type="Perceptron", custom_dict=True):
        """初始化 HanLP 分析器"""
        data_path = "C:/Users/faker/AppData/Local/Programs/Python/Python312/Lib/site-packages/pyhanlp/static/data/model/perceptron/large/cws.bin"

        # CRF 分析器
        self.CRFLAnalyzer = JClass("com.hankcs.hanlp.model.crf.CRFLexicalAnalyzer")()

        # 感知机分析器
        PLAnalyzer = JClass("com.hankcs.hanlp.model.perceptron.PerceptronLexicalAnalyzer")
        self.PLAnalyzer = PLAnalyzer(
            data_path,
            HanLP.Config.PerceptronPOSModelPath,
            HanLP.Config.PerceptronNERModelPath
        )

        self.analyzer = self.PLAnalyzer
        if analyzer_type == "Perceptron":
            self.analyzer = self.PLAnalyzer.enableCustomDictionary(custom_dict)
        elif analyzer_type == "CRF":
            self.analyzer = self.CRFLAnalyzer.enableCustomDictionary(custom_dict)

        self.paragraphs_info = []

    def add_characters_to_dict(self, names_list):
        """添加人物到自定义词典"""
        for n in names_list:
            if CustomDictionary.get(n) is None:
                CustomDictionary.add(n, "nr 1000 ")
            else:
                attr = "nr 1000 " + str(CustomDictionary.get(n))
                CustomDictionary.insert(n, attr)

    def cut_text(self, text):
        """使用 HanLP 分词并识别人名"""
        terms = self.analyzer.seg(text)
        result = []
        for term in terms:
            result.append((str(term.word), str(term.nature)))
        return result

    def process_novel(self, filepath):
        """处理小说文件，提取人物和章节信息"""
        content = self._read_file(filepath)

        # 提取人物（全文）
        characters = self._extract_characters(content)

        # 添加高频人物到词典
        high_freq_chars = [name for name, count in characters.items() if count >= 5]
        self.add_characters_to_dict(high_freq_chars)

        # 重新处理（使用增强后的词典）
        characters = self._extract_characters(content)

        # 划分章节
        chapters = self._split_chapters(content)

        # 记录段落信息用于后续共现分析
        self.paragraphs_info = self._analyze_paragraphs(content, chapters)

        return {
            'content': content,
            'chapters': chapters,
            'characters': characters,
            'chapter_indices': [ch['index'] for ch in chapters],
            'paragraphs_info': self.paragraphs_info
        }

    def _read_file(self, filepath):
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='gbk') as f:
                return f.read()

    def _extract_characters(self, content):
        """提取全文人物并统计出现次数"""
        characters = {}

        # 智能段落分割：检测文本格式
        # 如果存在大量连续空行，说明是有空行的格式
        has_blank_lines = bool(re.search(r'\n\s*\n', content))

        if has_blank_lines:
            # 有空行格式（如十日终焉）
            paragraphs = re.split(r'\n\s*\n', content)
        else:
            # 无空行格式（如仙工开物），按单行分割
            paragraphs = content.split('\n')

        for paragraph in tqdm(paragraphs, desc="Extracting characters"):
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            words = self.cut_text(paragraph)

            for word, flag in words:
                if flag in ['nr', 'nrf']:
                    characters[word] = characters.get(word, 0) + 1

        return characters

    def _split_chapters(sell, content):
        """
        将小说内容按章节划分，返回章节列表。
        使用行首匹配的章节标题正则，支持中文和英文格式。
        """
        # 定义章节标题正则（行首匹配，支持多种格式）
        chapter_pattern = re.compile(
            r'^\s*(?:'
            r'第\s*[零一二三四五六七八九十百千万\d]+\s*[章节部卷]'
            r'|Chapter\s+\d+'
            r'|Part\s+\d+'
            r'|SECTION\s+\d+'
            r')[^\n]*',
            re.IGNORECASE | re.MULTILINE
        )

        matches = list(chapter_pattern.finditer(content))

        if not matches:
            return [{
                'index': 0,
                'title': '全文',
                'start': 0,
                'end': len(content),
                'content': content
            }]

        chapters = []
        for i, match in enumerate(matches):
            title = match.group(0).strip()
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)

            chapters.append({
                'index': i,
                'title': title,
                'start': start,
                'end': end,
                'content': content[start:end]
            })

        return chapters


    def _analyze_paragraphs(self, content, chapters):
        """分析每个段落的人物信息，用于共现计算"""
        paragraphs_info = []

        for chapter in chapters:
            chapter_content = chapter['content']

            # 智能段落分割：检测文本格式
            has_blank_lines = bool(re.search(r'\n\s*\n', chapter_content))

            if has_blank_lines:
                raw_paragraphs = re.split(r'\n\s*\n', chapter_content)
            else:
                raw_paragraphs = chapter_content.split('\n')

            for para_idx, paragraph in enumerate(raw_paragraphs):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue

                # 提取段落中的人物
                chars_in_para = set()
                words = self.cut_text(paragraph)

                for word, flag in words:
                    if flag in ['nr', 'nrf']:
                        chars_in_para.add(word)

                if chars_in_para:
                    paragraphs_info.append({
                        'chapter_index': chapter['index'],
                        'paragraph_index': para_idx,
                        'characters': list(chars_in_para),
                        'text': paragraph
                    })

        return paragraphs_info

    def find_character_quotes(self, content, character_name, chapter_idx, paragraphs_info):
        """查找人物在指定章节的相关语句"""
        quotes = []

        # 找到该章节的所有段落
        chapter_paragraphs = [
            p for p in paragraphs_info
            if p['chapter_index'] == chapter_idx and character_name in p['characters']
        ]

        # 限制返回数量，最多 10 条
        for para_info in chapter_paragraphs[:10]:
            quotes.append({
                'text': para_info['text'],
                'paragraph_index': para_info['paragraph_index']
            })

        return quotes

