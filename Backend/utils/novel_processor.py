import os
import re
from tqdm import tqdm
from pyhanlp import *

class NovelProcessor:
    def __init__(self, analyzer_type="Perceptron", custom_dict=True):
        """初始化 HanLP 分析器"""
        data_path = "C:/Users/faker/AppData/Local/Programs/Python/Python312/Lib/site-packages/pyhanlp/static/data/model/perceptron/large/cws.bin"

        self.CRFLAnalyzer = JClass("com.hankcs.hanlp.model.crf.CRFLexicalAnalyzer")()

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

        characters = self._extract_characters(content)

        high_freq_chars = [name for name, count in characters.items() if count >= 5]
        self.add_characters_to_dict(high_freq_chars)

        characters = self._extract_characters(content)

        chapters = self._split_chapters(content)

        self.paragraphs_info = self._analyze_paragraphs(content, chapters)

        return {
            'content': content,
            'chapters': chapters,
            'characters': characters,
            'chapter_indices': [ch['index'] for ch in chapters],
            'paragraphs_info': self.paragraphs_info
        }

    def _read_file(self, filepath):
        """读取文件内容，支持 txt 和 pdf 格式"""
        file_ext = filepath.rsplit('.', 1)[1].lower()

        if file_ext == 'txt':
            return self._read_txt_file(filepath)
        elif file_ext == 'pdf':
            return self._read_pdf_file(filepath)
        else:
            raise ValueError(f'不支持的文件格式：{file_ext}')

    def _read_txt_file(self, filepath):
        """读取 TXT 文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='gbk') as f:
                return f.read()

    def _read_pdf_file(self, filepath):
        """读取 PDF 文件，保留自然段结构"""
        try:
            import fitz

            doc = fitz.open(filepath)

            all_pages_text = []
            found_text = False

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")

                if text and text.strip():
                    found_text = True
                    cleaned_text = text.strip()
                    all_pages_text.append(cleaned_text)

            doc.close()

            if not found_text:
                return ""

            full_text = "\n".join(all_pages_text)

            full_text = re.sub(r'\n{3,}', '\n\n', full_text)

            return full_text

        except ImportError:
            raise ImportError("需要安装 PyMuPDF 库：pip install PyMuPDF")
        except Exception as e:
            raise Exception(f"PDF 读取失败：{str(e)}")

    def _extract_characters(self, content):
        """提取全文人物并统计出现次数"""
        characters = {}

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

            paragraphs = chapter_content.split('\n')

            for para_idx, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue

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

        chapter_paragraphs = [
            p for p in paragraphs_info
            if p['chapter_index'] == chapter_idx and character_name in p['characters']
        ]

        for para_info in chapter_paragraphs[:10]:
            quotes.append({
                'text': para_info['text'],
                'paragraph_index': para_info['paragraph_index']
            })

        return quotes

